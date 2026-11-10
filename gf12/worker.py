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
# Native execution occurs only here, inside the admitted container.
sys.path.insert(0,'/code')
import fixture
source_checks=fixture.source_check()
if sys.version_info[:3]!=(3,12,13):raise RuntimeError('Python version')
sys.path.insert(0,'/deps')
import numpy as np
import kickmix as km
import kickmix_engine as ke
import importlib.metadata,base64
for package,version in [('numpy','2.1.3'),('kickmix','1.0.0'),('kickmix-engine','0.6.0')]:
 if importlib.metadata.version(package)!=version:raise RuntimeError('dependency version '+package)
text,meta=fixture.build();c=km.Circuit(text)
if c.num_qubits!=85 or c.num_bits!=725:raise RuntimeError('fixture dimensions')
path=Path('/tmp/gf12.kmb');c.to_file(str(path),format='kmb');p=ke.compile_kmb(str(path))
if int(p.reaction_depth)!=c.reaction_depth():raise RuntimeError('reaction depth')
if sorted(int(x)for x in p.bit_map)!=list(range(c.num_bits)):raise RuntimeError('classical bit coverage')
iq,ib=fixture.initial_state();input_ids=list(range(36))+list(range(48,84))
def aswords(masks):return np.array([[(m>>(64*k))&((1<<64)-1)for k in range(4)]for m in masks],dtype=np.uint64)
def asmasks(words):return [sum(int(v)<<(64*k)for k,v in enumerate(row))for row in words]
def bools(masks):return np.array([[(m>>s)&1 for s in range(256)]for m in masks],dtype=bool)
def masks_from_bools(data):return [sum(int(v)<<i for i,v in enumerate(row))for row in data]
def stats_and_check(q,bits,phase,counts):
 return fixture.validate(q,bits,phase,{k:int(v)for k,v in counts.items()if v})
start=time.monotonic();sim=km.Simulator(batch_size=256,debug_print=False,counting_operations=True,seed=fixture.SEED)
sim.write_across_shots(km.array([km.q(i)for i in input_ids]),bools([iq[i]for i in input_ids]))
sim.write_across_shots(km.array([km.b(i)for i in range(4)]),bools(ib[:4]));sim.do(c)
oq=masks_from_bools(sim.read_across_shots(km.array([km.q(i)for i in range(c.num_qubits)])))
ob=masks_from_bools(sim.read_across_shots(km.array([km.b(i)for i in range(c.num_bits)])))
op=0
for i in range(256):
 h=sim.read_shot_phase(i)%2
 if h not in (0,1):raise RuntimeError('non-binary exact phase')
 op|=int(h)<<i
st=sim.operation_statistics();oc={k:int(v)for k,v in dict(st).items()if v}
oz={str(k):int(v)for k,v in dict(st.z_pow_clifford_hierarchy_counts).items()if v}
oreport=stats_and_check(oq,ob,op,oc)
if oz or int(st.num_toffoli_like)!=oreport['expected_toffoli']:raise RuntimeError('official charged cost')
official_seconds=time.monotonic()-start
# Exactly one engine batch, using the same seed, quantum inputs and classical inputs.
compact=[int(p.bit_compact[i])for i in range(4)]
if min(compact)<0:raise RuntimeError('classical input compact mapping')
start=time.monotonic()
out=ke.run_batches(p,[fixture.SEED],input_ids,aswords([iq[i]for i in input_ids]).reshape(1,len(input_ids),4),compact,aswords(ib[:4]).reshape(1,4,4),threads=1,counting=True,dump=True)
eq=asmasks(out['dump_q'][0]);eb=[0]*c.num_bits
for original_index,value in zip(p.bit_map,asmasks(out['dump_bits'][0][:p.num_bits])):eb[int(original_index)]=value
ep=asmasks(out['phase'])[0]
ec={k:int(v)for k,v in zip(ke.KINDS,out['kind_counts'][0])if v}
ez={str(k):int(v)for k,v in enumerate(out['z_levels'][0])if v}
ereport=stats_and_check(eq,eb,ep,ec)
if eq!=oq or eb!=ob or ep!=op or ec!=oc or ez!=oz:raise RuntimeError('backend parity mismatch')
expected_units=np.array([((ep>>s)&1)<<63 for s in range(256)],dtype=np.uint64)
if not np.array_equal(out['phase_units'][0],expected_units):raise RuntimeError('exact binary phase units')
if int(out['toffoli_count'][0])!=oreport['expected_toffoli']:raise RuntimeError('engine charged cost')
engine_seconds=time.monotonic()-start
def raw(q,bits,phase):
 data=aswords(q).tobytes()+aswords(bits).tobytes()+phase.to_bytes(32,'little')
 return dict(format='little-endian qubit rows then classical rows, 4xu64 per256shots; final32-byte phase bitmask',num_qubits=85,num_bits=725,sha256=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode())
u=resource.getrusage(resource.RUSAGE_SELF)
emit(dict(pilot='PASS',scope='public synthetic field arithmetic only; not task qualification',shots_per_backend=256,backend_shots=512,seed=fixture.SEED,modulus=fixture.MODULUS,fixture=meta,source_checks=source_checks,kmb_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reaction_depth=c.reaction_depth(),official=oreport,engine=ereport,charged_counts=oc,mismatches=dict(qubits=0,classical_bits=0,exact_binary_phase=0,operation_counts=0,reaction_depth=0),official_seconds=official_seconds,engine_seconds=engine_seconds,CPU_seconds=u.ru_utime+u.ru_stime,peak_RSS_bytes=u.ru_maxrss*1024,wall_seconds=time.monotonic()-START,cgroup_memory_peak=int(Path('/sys/fs/cgroup/memory.peak').read_text()),fork_denied=True,python=sys.version,kickmix_binary_sha256=hashlib.sha256(Path(km.__file__).read_bytes()).hexdigest(),engine_binary_sha256=hashlib.sha256(Path(ke._engine.__file__).read_bytes()).hexdigest(),raw_official=raw(oq,ob,op),raw_engine=raw(eq,eb,ep)))
