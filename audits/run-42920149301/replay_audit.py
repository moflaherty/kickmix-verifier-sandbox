"""Read-only audit of recorded data. Never imports or executes a simulator."""
import json,base64,hashlib,importlib.util
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'receipt.json').read_text());context=json.loads((HERE/'audit-input.json').read_text())
c=r['comparison'];M=(1<<256)-1
for p,h in r['verified_source_sha256'].items():
    assert hashlib.sha256(context['sources'][p].encode()).hexdigest()==h,p
assert hashlib.sha256((HERE/'source/fixture.py').read_bytes()).hexdigest()==r['verified_source_sha256']['gf12/fixture.py']
spec=importlib.util.spec_from_file_location('public_fixture',HERE/'source/fixture.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
text,meta=f.build()
assert hashlib.sha256(text.encode()).hexdigest()==c['fixture']['fixture_sha256']==meta['fixture_sha256']

def polynomial_product(a,b):
    # Independent coefficient convolution and descending polynomial elimination.
    v=[0]*23
    for i in range(12):
        for j in range(12):v[i+j]^=(a>>i&1)&(b>>j&1)
    for k in range(22,11,-1):
        if v[k]:
            for e in (0,1,4,6,12):v[k-12+e]^=1
    assert not any(v[12:])
    return sum(v[k]<<k for k in range(12))
for i in range(12):
    for j in range(12):assert polynomial_product(1<<i,1<<j)==f.emitter_weights()[i+j]

state=0x20261110
def draw():
    global state
    state=(1664525*state+1013904223)&0xffffffff
    return state>>12&4095
rows=[]
for s in range(256):
    a,b=(1<<(s//12),1<<(s%12))if s<144 else(draw(),draw())
    if s>=144 and s%4==2:a=b=1
    z=draw()
    if s<12:z=1<<s
    rows.append((a,b,z,int(s<144 or s%2==0),s%4))
assert rows==f.inputs()
iq=[0]*85;ib=[0]*725
for s,(a,b,z,e,mode)in enumerate(rows):
    for k in range(12):
        iq[k]|=(a>>k&1)<<s;iq[12+k]|=(b>>k&1)<<s
        for start in (24,48,60,72):iq[start+k]|=(z>>k&1)<<s
    ib[0]|=e<<s
    for k in (1,2,3):ib[k]|=int(mode==k)<<s

def decode(raw):
    b=base64.b64decode(raw['base64'],validate=True)
    assert len(b)==(85+725)*32+32
    assert hashlib.sha256(b).hexdigest()==raw['sha256']
    ints=[int.from_bytes(b[k:k+32],'little')for k in range(0,len(b),32)]
    return b,ints[:85],ints[85:810],ints[810]
o,oq,ob,op=decode(c['raw_official']);e,eq,eb,ep=decode(c['raw_engine'])
assert o==e and oq==eq and ob==eb and op==ep

def word(q,start,s):return sum((q[start+k]>>s&1)<<k for k in range(12))
def check_primary(q,phase,stage):
    assert phase==0,stage+' phase'
    for s,(a,b,z,on,mode)in enumerate(rows):
        assert word(q,0,s)==a and word(q,12,s)==b
        if stage=='forward':assert word(q,24,s)==z^(polynomial_product(a,b)if on else 0)
        else:
            assert word(q,24,s)==z
            assert word(q,36,s)==(z^polynomial_product(a,b)if on else 0)
    assert q[84]==0

q=iq.copy();bits=ib.copy();phase=0;stack=[M];counts=Counter();measurements=[];stages=[]
for line in text.splitlines():
    if line=='CX q24 q36':check_primary(q,phase,'forward');stages.append('forward')
    if line=='PUSH_CONDITION if b1':check_primary(q,phase,'inverse');stages.append('inverse')
    a=line.split();kind=a[0]
    if kind=='PUSH_CONDITION':stack.append(stack[-1]&bits[int(a[-1][1:])]);counts[kind]+=256;continue
    if kind=='POP_CONDITION':assert len(stack)>1;stack.pop();counts[kind]+=256;continue
    enabled=stack[-1]
    if 'if'in a:
        at=a.index('if');enabled&=bits[int(a[at+1][1:])];a=a[:at]
    x=[int(t[1:])for t in a[1:]];counts[kind]+=enabled.bit_count()
    if kind=='CCX':q[x[2]]^=q[x[0]]&q[x[1]]&enabled
    elif kind=='CX':q[x[1]]^=q[x[0]]&enabled
    elif kind=='X':q[x[0]]^=enabled
    elif kind=='CZ':phase^=q[x[0]]&q[x[1]]&enabled
    elif kind=='HMR':
        assert x[1]not in measurements;measurements.append(x[1])
        outcome=ob[x[1]];assert outcome&~enabled==0
        phase^=q[x[0]]&outcome&enabled;q[x[0]]&=M^enabled;bits[x[1]]=outcome
    else:raise AssertionError('unexpected opcode '+kind)
assert len(stack)==1 and stages==['forward','inverse']
assert measurements==list(range(4,725))==meta['measurement_bits']
assert q==oq and bits==ob and phase==op
assert dict(counts)==c['charged_counts']==c['official']['expected_counts']==c['engine']['expected_counts']
assert counts['CCX']==77184 and counts['HMR']==77220 and counts['CZ']==38747
assert q[84]==0 and q[:24]==iq[:24]and q[24:36]==iq[24:36]and bits[:4]==ib[:4]
bad_product=bad_dirty=missing_phase=dirty_phase=0;expected_phase=0
for s,(a,b,z,on,mode)in enumerate(rows):
    product=polynomial_product(a,b)
    assert word(q,36,s)==(z^product if on else 0)
    for start,tag in ((48,1),(60,2),(72,3)):
        ideal=z^(product if on and mode==tag else 0);actual=word(q,start,s)
        if tag==1:
            assert actual==ideal^(1 if on and mode==tag else 0);bad_product+=int(actual!=ideal)
        elif tag==2:assert actual==ideal
        else:
            assert actual==(ideal&~128 if on and mode==tag else ideal);bad_dirty+=int(actual!=ideal)
    missing=int(on and mode==2)*(a&1)*(b&1)*(ob[436]>>s&1)
    dirty=int(on and mode==3)*((z^product)>>7&1)*(ob[724]>>s&1)
    missing_phase+=missing;dirty_phase+=dirty;expected_phase|=(missing^dirty)<<s
assert expected_phase==op and op.bit_count()==23
assert (bad_product,missing_phase,bad_dirty,dirty_phase)==(36,19,13,4)
assert sum(t[3]for t in rows)==200
assert c['shots_per_backend']==256 and c['backend_shots']==512 and c['seed']==7 and c['modulus']==4179
assert c['reaction_depth']==1 and not any(c['mismatches'].values())
assert r['status']==r['containment']=='PASS'
assert r['verified_cgroup_limits']=={'memory.max':'536870912','memory.swap.max':'0','cpu.max':'100000 100000','pids.max':'16'}
ctrl={v['mode']:v for v in r['controls']}
assert ctrl['memory']['OOMKilled']and ctrl['memory']['container_exit']==137
assert ctrl['memory']['after']['memory.events']['oom_kill']-ctrl['memory']['before']['memory.events']['oom_kill']==1
assert ctrl['pids']['after']['pids.events']['max']-ctrl['pids']['before']['pids.events']['max']==1
assert json.loads(ctrl['pids']['stdout'])['threads_created']==15
assert json.loads(ctrl['scratch']['stdout'])['scratch_limit_detected']
assert ctrl['cpu']['container_exit']==137 and not ctrl['cpu']['OOMKilled']
assert ctrl['wall']['container_exit']==137 and ctrl['wall']['stop_reason']=='WALL_NEGATIVE_EXPECTED'
assert all(v['child_reaped']and v['all_cgroup_processes_reaped']and v['after']['pids.current']==0 for v in r['controls']+[r['pilot_container']])
assert r['pilot_container']['returncode']==0 and r['pilot_container']['stop_reason']is None
assert r['cleanup_complete']and r['cgroup_empty_before_cleanup']and r['final_cgroup']['pids.current']==0
assert r['final_cgroup']['memory.peak']==536870912 and r['final_cgroup']['cpu.stat']['usage_usec']<30000000 and r['wall_seconds']<60
assert json.loads(r['pilot_container']['stdout'])==c
summary=dict(verdict='PASS',audit_type='read-only transcript replay; no simulator or workflow rerun',shots_per_backend=256,total_backend_shots=512,source_files_checked=6,field_modulus=4179,basis_products_checked=144,all_quantum_bits_checked=85*256*2,all_classical_bits_checked=725*256*2,HMR_instruction_records_checked=721,HMR_executions_per_backend=counts['HMR'],CCX_per_backend=counts['CCX'],complete_counts=dict(counts),reaction_depth_agreement_recorded=1,primary_forward_and_inverse_transcript_stages='PASS',phase_equation='PASS',negative_controls=dict(wrong_product=bad_product,missing_phase=missing_phase,dirty_target_value=bad_dirty,dirty_target_phase=dirty_phase),raw_backend_sha256=c['raw_official']['sha256'],raw_backend_bytes=len(o),resources=dict(total_contained_CPU_seconds=r['final_cgroup']['cpu.stat']['usage_usec']/1e6,pilot_contained_CPU_seconds=(r['pilot_container']['after']['cpu.stat']['usage_usec']-r['pilot_container']['before']['cpu.stat']['usage_usec'])/1e6,controller_wall_seconds=r['wall_seconds'],worker_wall_seconds=c['wall_seconds'],worker_peak_RSS_MiB=c['peak_RSS_bytes']/2**20,pilot_cgroup_peak_MiB=c['cgroup_memory_peak']/2**20),cleanup_complete=True)
(HERE/'AUDIT_RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
