"""Disposable public-only CI controller. Executes no competition task."""
import os,sys,subprocess,json,time,hashlib,urllib.request,urllib.parse,zipfile,stat,uuid,threading,shutil,signal
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'evidence';OUT.mkdir(exist_ok=False)
START=time.monotonic();DEADLINE=START+50
UNIT='kickmixpilot'+uuid.uuid4().hex+'.slice';CG=Path('/sys/fs/cgroup')/UNIT
IMAGE_TAG='python:3.12.13-bookworm';LIMIT=512*1024**2
containers=[];receipt=dict(status='FAIL_CLOSED',pilot_executed=False,container_limits=dict(memory_bytes=LIMIT,swap_bytes=0,cpus=1,aggregate_CPU_seconds=30,wall_seconds=60,pids=16,writable_scratch_bytes=16*1024**2),controls=[],private_inputs=False,production_secrets=False,source_commit_engine='b455a8a6120b515219b49cd469f83a230cf4989f')
def terminated(signum,frame):raise TimeoutError('outer wall termination')
signal.signal(signal.SIGTERM,terminated)
def save(): (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def cmd(argv,timeout=20,check=True):
 rem=DEADLINE-time.monotonic()
 if rem<=0:raise RuntimeError('aggregate wall admission deadline')
 p=subprocess.run(argv,capture_output=True,text=True,timeout=max(.01,min(timeout,rem)))
 if check and p.returncode:raise RuntimeError(str(argv[:3])+': '+p.stderr[-1200:])
 return p

def scalar(path):return (CG/path).read_text().strip()
def counters():
 d={}
 for name in ['memory.current','memory.peak','memory.events','cpu.stat','pids.current','pids.events']:
  s=scalar(name);d[name]=int(s)if s.isdecimal()else dict((k,int(v))for k,v in (l.split()for l in s.splitlines()))
 return d

def run(mode,wall=3):
 name='kickmix-'+uuid.uuid4().hex;containers.append(name)
 args=['docker','run','--name',name,'--cgroup-parent',UNIT,'--memory','512m','--memory-swap','512m','--cpus','1','--pids-limit','16','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65532:65532','--shm-size','1m','--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=15m,mode=1777','--log-driver','none','--mount',f'type=bind,src={ROOT},dst=/code,readonly']
 if mode=='pilot':args+=['--mount',f'type=bind,src={ROOT.parent/"deps"},dst=/deps,readonly']
 for k,v in {'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','RAYON_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','HOME':'/nonexistent'}.items():args+=['-e',k+'='+v]
 args +=[receipt['image_id'],'python','-I','-B','/code/worker.py',mode]
 before=counters();t=time.monotonic();p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);samples=[];reason=None
 # Bound pipe retention even if an imported extension produces unexpected output.
 output=[bytearray(),bytearray()]
 def drain(stream,index,limit):
  nonlocal reason
  while True:
   block=stream.read(4096)
   if not block:return
   encoded=block.encode()
   if len(output[index])+len(encoded)>limit:
    reason='OUTPUT_BOUND';subprocess.run(['docker','kill',name],capture_output=True,timeout=3);return
   output[index].extend(encoded)
 readers=[threading.Thread(target=drain,args=(p.stdout,0,262144)),threading.Thread(target=drain,args=(p.stderr,1,65536))]
 for reader in readers:reader.start()
 def watch():
  nonlocal reason
  while p.poll()is None:
   try:
    s=counters();samples.append(s)
    if len(samples)>12000:raise RuntimeError('monitor record bound')
    if s['cpu.stat']['usage_usec']>=25_000_000:reason='CPU_EARLY_STOP'
    if time.monotonic()-t>=wall:reason='WALL_NEGATIVE_EXPECTED'if mode=='wall'else'CONTAINER_WALL_STOP'
    if time.monotonic()>=DEADLINE:reason='AGGREGATE_WALL_STOP'
    if reason:subprocess.run(['docker','kill',name],capture_output=True,timeout=3);return
   except Exception as e:
    reason='MONITOR_FAILURE:'+type(e).__name__;subprocess.run(['docker','kill',name],capture_output=True,timeout=3);return
   time.sleep(.01)
 w=threading.Thread(target=watch);w.start()
 try:p.wait(timeout=max(.01,DEADLINE-time.monotonic()))
 finally:
  if p.poll()is None:
   subprocess.run(['docker','kill',name],capture_output=True,timeout=3);p.kill();p.wait(timeout=3)
  w.join(timeout=4)
  for reader in readers:reader.join(timeout=2)
 if w.is_alive():raise RuntimeError('watcher cleanup failed')
 if any(reader.is_alive()for reader in readers):raise RuntimeError('pipe cleanup failed')
 stdout,stderr=(b.decode()for b in output)
 after=counters();state=json.loads(cmd(['docker','inspect',name]).stdout)[0]
 row=dict(mode=mode,returncode=p.returncode,container_exit=state['State']['ExitCode'],OOMKilled=state['State']['OOMKilled'],stop_reason=reason,wall_seconds=time.monotonic()-t,before=before,after=after,sampled_peak_bytes=max([s['memory.peak']for s in samples]+[after['memory.peak']]),stdout=stdout,stderr=stderr[-3000:],child_reaped=p.poll()is not None)
 cmd(['docker','rm','-f',name]);containers.remove(name)
 if int(scalar('pids.current'))!=0:raise RuntimeError('container children remain')
 row['all_cgroup_processes_reaped']=True
 if after['memory.peak']>LIMIT:raise RuntimeError('measured memory budget exceeded')
 if after['cpu.stat']['usage_usec']>=30_000_000 or time.monotonic()-START>=60:raise RuntimeError('aggregate limit exceeded')
 if reason and not(mode=='wall'and reason=='WALL_NEGATIVE_EXPECTED'):raise RuntimeError(reason)
 return row

def download(url,dest,expected=None,maxbytes=32*1024**2):
 u=urllib.parse.urlparse(url)
 if u.scheme!='https' or not(u.hostname in ['pypi.org','github.com','files.pythonhosted.org']):raise RuntimeError('download host')
 with urllib.request.urlopen(url,timeout=max(.1,min(8,DEADLINE-time.monotonic())))as f,dest.open('xb')as out:
  n=0;h=hashlib.sha256()
  for b in iter(lambda:f.read(1024**2),b''):
   n+=len(b)
   if n>maxbytes:raise RuntimeError('download bound')
   out.write(b);h.update(b)
 actual=h.hexdigest()
 if expected and actual!=expected:raise RuntimeError('executable digest mismatch')
 return actual
try:
 pins=json.loads((ROOT.parent/'SHA256SUMS.json').read_text())
 for rel,expected in pins.items():
  if hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()!=expected:raise RuntimeError('sandbox source integrity '+rel)
 receipt['verified_source_sha256']=pins
 if os.environ.get('GITHUB_REPOSITORY')!='moflaherty/kickmix-verifier-sandbox' or os.environ.get('GITHUB_RUN_ATTEMPT')!='1' or os.environ.get('GITHUB_RUN_NUMBER')!='1':raise RuntimeError('one-run repository admission')
 if not Path('/sys/fs/cgroup/cgroup.controllers').exists():raise RuntimeError('cgroup-v2 unavailable')
 if cmd(['docker','info','--format','{{.CgroupDriver}}']).stdout.strip()!='systemd':raise RuntimeError('requires systemd cgroup driver')
 # Only public standard image. Resolve and record immutable content before execution.
 cmd(['docker','pull','--platform','linux/amd64',IMAGE_TAG],timeout=35)
 image=json.loads(cmd(['docker','image','inspect',IMAGE_TAG]).stdout)[0];receipt.update(image_tag=IMAGE_TAG,image_id=image['Id'],image_repo_digests=image['RepoDigests'],workflow_commit=os.environ['GITHUB_SHA'])
 if image['Architecture']!='amd64' or not image['RepoDigests']:raise RuntimeError('image identity')
 unit='[Unit]\nDescription=Disposable kickmix pilot containment\n[Slice]\nMemoryAccounting=yes\nMemoryMax=536870912\nMemorySwapMax=0\nCPUAccounting=yes\nCPUQuota=100%\nTasksAccounting=yes\nTasksMax=16\n'
 f=ROOT.parent/'slice.unit';f.write_text(unit);cmd(['sudo','install','-m','644',str(f),'/run/systemd/system/'+UNIT]);cmd(['sudo','systemctl','daemon-reload']);cmd(['sudo','systemctl','start',UNIT])
 limits={k:scalar(k)for k in ['memory.max','memory.swap.max','cpu.max','pids.max']};q,period=map(int,limits['cpu.max'].split())
 if int(limits['memory.max'])!=LIMIT or limits['memory.swap.max']!='0'or q!=period or limits['pids.max']!='16':raise RuntimeError('resource boundary mismatch')
 receipt['verified_cgroup_limits']=limits;save()
 for mode in ['memory','pids','scratch','cpu','wall']:
  row=run(mode,wall=.6 if mode=='wall'else 3)
  if mode=='memory'and not(row['OOMKilled']and row['after']['memory.events'].get('oom_kill',0)>row['before']['memory.events'].get('oom_kill',0)):raise RuntimeError('memory negative not detected')
  if mode=='pids'and not(row['returncode']==0 and row['after']['pids.events'].get('max',0)>row['before']['pids.events'].get('max',0)):raise RuntimeError('PID negative not detected')
  if mode=='scratch'and not(row['returncode']==0 and json.loads(row['stdout']).get('scratch_limit_detected')):raise RuntimeError('scratch negative not detected')
  if mode=='cpu'and not(row['container_exit']==137 and row['after']['cpu.stat']['usage_usec']-row['before']['cpu.stat']['usage_usec']>=900000):raise RuntimeError('CPU negative not detected')
  if mode=='wall'and row['stop_reason']!='WALL_NEGATIVE_EXPECTED':raise RuntimeError('wall negative not detected')
  receipt['controls'].append(row);save()
 if counters()['cpu.stat']['usage_usec']>4_000_000:raise RuntimeError('no aggregate CPU reserve')
 receipt['containment']='PASS';save()
 # Public metadata + content hashes before extraction/import. No setup.py or pip.
 wheels=ROOT.parent/'wheels';deps=ROOT.parent/'deps';wheels.mkdir();deps.mkdir();wheel_records=[]
 for package,version in [('kickmix','1.0.0'),('numpy','2.1.3')]:
  meta=wheels/(package+'.json');download(f'https://pypi.org/pypi/{package}/{version}/json',meta,maxbytes=1024**2);data=json.loads(meta.read_text())
  choices=[x for x in data['urls']if x['filename'].endswith('.whl')and '-cp312-'in x['filename']and'manylinux'in x['filename']and'x86_64'in x['filename']]
  if len(choices)!=1:raise RuntimeError('ambiguous dependency wheel')
  x=choices[0];dest=wheels/x['filename'];digest=download(x['url'],dest,x['digests']['sha256']);wheel_records.append(dict(package=package,version=version,file=dest.name,sha256=digest,manifest_url=f'https://pypi.org/pypi/{package}/{version}/json'))
 ename='kickmix_engine-0.6.0-cp312-abi3-manylinux_2_28_x86_64.whl';dest=wheels/ename;digest=download('https://github.com/manwithacat/kickmix-engine/releases/download/v0.6.0/'+ename,dest,'76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178');wheel_records.append(dict(package='kickmix-engine',version='0.6.0',file=ename,sha256=digest,source_commit=receipt['source_commit_engine']))
 total=0
 for p in wheels.glob('*.whl'):
  with zipfile.ZipFile(p)as z:
   for i in z.infolist():
    rel=Path(i.filename);total+=i.file_size
    if rel.is_absolute()or'..'in rel.parts or stat.S_ISLNK(i.external_attr>>16)or total>160*1024**2:raise RuntimeError('wheel extraction boundary')
   z.extractall(deps)
 receipt['verified_wheels']=wheel_records;save()
 if DEADLINE-time.monotonic()<5:raise RuntimeError('no pilot wall reserve')
 receipt['pilot_executed']=True;save()
 row=run('pilot',wall=min(23,DEADLINE-time.monotonic()-3));receipt['pilot_container']=row
 if row['returncode']!=0:raise RuntimeError('pilot child failed')
 result=json.loads(row['stdout']);receipt['comparison']=result
 if result.get('pilot')!='PASS':raise RuntimeError('pilot semantic failure')
 receipt.update(status='PASS',scope='Research microtest only; unchanged official verifier remains authoritative')
except BaseException as e:
 receipt.update(status='FAIL_CLOSED',error=type(e).__name__+': '+str(e));raise
finally:
 for name in list(containers):subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=4)
 if CG.exists():
  receipt['final_cgroup']=counters();receipt['cgroup_empty_before_cleanup']=int(scalar('pids.current'))==0
 subprocess.run(['sudo','systemctl','stop',UNIT],capture_output=True,timeout=4)
 subprocess.run(['sudo','rm','-f','/run/systemd/system/'+UNIT],capture_output=True,timeout=4)
 subprocess.run(['sudo','systemctl','daemon-reload'],capture_output=True,timeout=4)
 receipt['cleanup_complete']=not CG.exists();receipt['wall_seconds']=time.monotonic()-START
 if not receipt['cleanup_complete']or receipt['wall_seconds']>=60:receipt['status']='FAIL_CLOSED';receipt['cleanup_or_wall_failure']=True
 save()
 print(json.dumps(receipt))
if receipt['status']!='PASS':sys.exit(1)
