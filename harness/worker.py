"""Public synthetic parity microtest. No competition circuits or private inputs."""
import os,sys,json,time,resource,ctypes,errno,hashlib,threading
from pathlib import Path
START=time.monotonic()
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
mode=sys.argv[1]
resource.setrlimit(resource.RLIMIT_CPU,(1,1)if mode=='cpu'else(19,20))
# Stack this restriction on Docker's default seccomp profile. Only threads may
# clone: one TGID's kernel RLIMIT_CPU includes every native worker thread.
def restrict_process_creation():
 if os.uname().machine!='x86_64':raise RuntimeError('x86_64 required')
 class F(ctypes.Structure):_fields_=[('code',ctypes.c_ushort),('jt',ctypes.c_ubyte),('jf',ctypes.c_ubyte),('k',ctypes.c_uint)]
 class P(ctypes.Structure):_fields_=[('len',ctypes.c_ushort),('filter',ctypes.POINTER(F))]
 # arch check; reject x32 ABI; forbid fork/vfork/clone3, allow only CLONE_THREAD.
 ins=[(0x20,0,0,4),(0x15,1,0,0xc000003e),(0x06,0,0,0x80000000),(0x20,0,0,0),
      (0x35,0,1,0x40000000),(0x06,0,0,0x80000000),
      (0x15,0,1,57),(0x06,0,0,0x50001),(0x15,0,1,58),(0x06,0,0,0x50001),
      (0x15,0,1,435),(0x06,0,0,0x50026),(0x15,1,0,56),(0x06,0,0,0x7fff0000),
      (0x20,0,0,16),(0x45,1,0,0x10000),(0x06,0,0,0x50001),(0x06,0,0,0x7fff0000)]
 arr=(F*len(ins))(*(F(*r)for r in ins));p=P(len(ins),arr);lib=ctypes.CDLL(None,use_errno=True)
 if lib.prctl(38,1,0,0,0)!=0 or lib.prctl(22,2,ctypes.byref(p),0,0)!=0:raise OSError(ctypes.get_errno(),'seccomp')
restrict_process_creation()
try:pid=os.fork()
except OSError as e:
 if e.errno!=errno.EPERM:raise
else:
 if pid==0:os._exit(99)
 raise RuntimeError('fork not denied')
def emit(v):print(json.dumps(v),flush=True)
if mode=='memory':
 emit({'control':'memory','allocation_bytes':768*1024**2});v=bytearray(768*1024**2)
 raise RuntimeError('memory negative survived')
if mode=='cpu':
 while True:pass
if mode=='wall':time.sleep(120);raise RuntimeError('wall control survived')
if mode=='scratch':
 denied=False
 try:
  with open('/tmp/limit-negative','wb')as f:
   for i in range(17):f.write(bytes(1024**2));f.flush()
 except OSError as e:
  if e.errno!=errno.ENOSPC:raise
  denied=True
 if not denied:raise RuntimeError('scratch negative survived')
 emit({'control':'scratch','scratch_limit_detected':True});sys.exit(0)
if mode=='pids':
 stop=threading.Event();threads=[];denied=False
 try:
  for i in range(40):
   t=threading.Thread(target=stop.wait);t.start();threads.append(t)
 except RuntimeError:denied=True
 finally:
  stop.set()
  for t in threads:t.join()
 if not denied:raise RuntimeError('PID negative survived')
 emit({'control':'pids','fork_denied':True,'thread_limit_detected':True,'threads_created':len(threads)});time.sleep(.15);sys.exit(0)
if mode!='pilot':raise RuntimeError('unknown mode')
# Immutable, hash-verified wheel extraction is mounted read-only at /deps.
if sys.version_info[:3]!=(3,12,13):raise RuntimeError('Python version')
sys.path.insert(0,'/deps')
import numpy as np
import kickmix as km
import kickmix_engine as ke
import importlib.metadata
if importlib.metadata.version('numpy')!='2.1.3' or importlib.metadata.version('kickmix')!='1.0.0' or importlib.metadata.version('kickmix-engine')!='0.6.0':raise RuntimeError('dependency version')
BASE='''REGISTER r0 "x"
APPEND_TO_REGISTER q0 r0
APPEND_TO_REGISTER q1 r0
R q2
CCX q0 q1 q2
Z_POW q2 0.125
HMR q2 b0
CZ q0 q1 if b0
BIT_STORE1 b1
PUSH_CONDITION if b0
HMR q3 b1
PUSH_CONDITION if b1
CCX q0 q1 q4
CCX q0 q1 q4
POP_CONDITION
POP_CONDITION
R q4
HMR q3 b2
'''
xs=np.arange(256,dtype=np.uint64)%4;xreg=km.array([km.q(0),km.q(1)])
def unpack(v):
 return np.unpackbits(np.ascontiguousarray(v).view(np.uint8).reshape(len(v),32),axis=1,bitorder='little')
def original(c,seed):
 s=km.Simulator(batch_size=256,debug_print=False,counting_operations=True,seed=seed)
 s.write_across_shots(xreg,((xs[None,:]>>np.arange(2,dtype=np.uint64)[:,None])&1).astype(bool));s.do(c)
 q=s.read_across_shots(km.array([km.q(i)for i in range(c.num_qubits)])).astype(np.uint8)
 bits=s.read_across_shots(km.array([km.b(i)for i in range(c.num_bits)])).astype(np.uint8)
 phase=np.zeros((256,2),dtype=np.uint64);units=np.zeros(256,dtype=np.uint64)
 for i in range(256):
  h=s.read_shot_phase(i);v=int(h*(1<<127))%(1<<128);phase[i]=(v&((1<<64)-1),v>>64)
  n,d=h.as_integer_ratio();units[i]=(((n<<64)//d+1)>>1)&((1<<64)-1)
 st=s.operation_statistics();stats=dict(st);kc=np.array([stats.get(k,0)for k in ke.KINDS],dtype=np.uint64);z=np.zeros(129,dtype=np.uint64)
 for k,v in dict(st.z_pow_clifford_hierarchy_counts).items():z[int(k)]=v
 return dict(q=q,bits=bits,phase=phase,units=units,kc=kc,z=z,toffoli=int(st.num_toffoli_like))
def engine(p,seed):
 out=ke.run(p,[seed],xs.reshape(1,1,256),[0,1],s=1,threads=1,counting=True,dump=True)
 return dict(q=unpack(out['dump_q'][0]),bits=unpack(out['dump_bits'][0][:p.num_bits]),phase=out['dump_vphase'][0],units=out['phase_units'][0,0],kc=out['kind_counts'][0],z=out['z_levels'][0],toffoli=int(out['toffoli_count'][0]))
def compare(ref,got,p):
 bm=np.array(p.bit_map,dtype=int);diff={}
 for k in ['q','phase','units','kc','z','toffoli']:
  if not np.array_equal(ref[k],got[k]):diff[k]=int(np.count_nonzero(np.asarray(ref[k])!=np.asarray(got[k])))
 if not np.array_equal(ref['bits'][bm],got['bits']):diff['classical_bits']=int(np.count_nonzero(ref['bits'][bm]!=got['bits']))
 return diff
results=[];summaries={};budget_shots=0
for name,text,seeds in [('base',BASE,[7,11]),('missing_phase_correction',BASE.replace('CZ q0 q1 if b0\n',''),[7]),('dirty_R',BASE+'CX q0 q4\nR q4\n',[7]),('wrong_output',BASE+'X q0\n',[7])]:
 c=km.Circuit(text);path=Path('/tmp')/(name+'.kmb');c.to_file(str(path),format='kmb');digest=hashlib.sha256(path.read_bytes()).hexdigest();p=ke.compile_kmb(str(path))
 if int(p.reaction_depth)!=c.reaction_depth():raise RuntimeError('reaction depth mismatch '+name)
 for seed in seeds:
  t=time.monotonic();ref=original(c,seed);official_s=time.monotonic()-t;t=time.monotonic();got=engine(p,seed);engine_s=time.monotonic()-t;budget_shots+=512
  diff=compare(ref,got,p)
  if diff:raise RuntimeError('semantic mismatch '+name+json.dumps(diff))
  expected=np.where(xs==3,np.uint64(1<<60),np.uint64(0));phase_bad=int(np.count_nonzero(ref['units']!=expected));output_bad=int(np.count_nonzero(ref['q'][:2]!=((xs[None,:]>>np.arange(2,dtype=np.uint64)[:,None])&1)));dirty=int(np.count_nonzero(ref['q'][2:]))
  if name=='base'and(phase_bad or output_bad or dirty):raise RuntimeError('base analytic oracle failed')
  if name in ['missing_phase_correction','dirty_R']and phase_bad==0:raise RuntimeError('missing phase negative detection')
  if name=='wrong_output'and output_bad==0:raise RuntimeError('missing output negative detection')
  row=dict(case=name,seed=seed,kmb_sha256=digest,reaction_depth=c.reaction_depth(),mismatches=diff,phase_bad_vs_ideal=phase_bad,output_bad_vs_ideal=output_bad,dirty_scratch_bits=dirty,official_seconds=official_s,engine_seconds=engine_s,official_toffoli=ref['toffoli'],official_counts={k:int(v)for k,v in zip(ke.KINDS,ref['kc'])if v})
  if name=='base'and seed==11:
   wrong=engine(p,12);budget_shots+=256;wd=compare(ref,wrong,p)
   if not('classical_bits'in wd or 'kc'in wd or 'toffoli'in wd):raise RuntimeError('wrong seed not detected')
   results.append(dict(case='wrong_seed',original_seed=11,engine_seed=12,expected_mismatch_detected=True,differences=wd))
  results.append(row)
 if budget_shots>2816:raise RuntimeError('shot limit')
u=resource.getrusage(resource.RUSAGE_SELF)
emit(dict(cgroup_memory_peak=int(Path('/sys/fs/cgroup/memory.peak').read_text()),cgroup_CPU_stat=Path('/sys/fs/cgroup/cpu.stat').read_text(),pilot='PASS',science_scope='synthetic only; no task verifier or competition data',backend_shots=budget_shots,source_fixture_sha256=hashlib.sha256(BASE.encode()).hexdigest(),python=sys.version,numpy=np.__version__,kickmix_version=importlib.metadata.version('kickmix'),engine_version=ke.__version__,kickmix_binary_sha256=hashlib.sha256(Path(km.__file__).read_bytes()).hexdigest(),engine_binary_sha256=hashlib.sha256(Path(ke._engine.__file__).read_bytes()).hexdigest()if hasattr(ke,'_engine')else None,fork_denied=True,results=results,CPU_seconds=u.ru_utime+u.ru_stime,peak_RSS_bytes=u.ru_maxrss*1024,wall_seconds=time.monotonic()-START))
