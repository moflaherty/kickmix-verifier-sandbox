"""Read-only transcript audit: no native compiler or simulator imports."""
from pathlib import Path
import json,hashlib,base64,importlib.util
from collections import Counter
P=Path(__file__).resolve().parent
d=json.loads((P/'audit_input.json').read_text());r=d['receipt'];c=r['comparison'];M=(1<<256)-1
assert hashlib.sha256((P/'receipt.json').read_bytes()).hexdigest()==d['artifact']['receipt_sha256']
for name,sha in r['verified_source_sha256'].items():assert hashlib.sha256(d['sources'][name].encode()).hexdigest()==sha,name
assert hashlib.sha256((P/'source/fixture.py').read_bytes()).hexdigest()==r['verified_source_sha256']['dependent_v2/fixture.py']
spec=importlib.util.spec_from_file_location('emitter',P/'source/fixture.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
text,meta=f.build();assert hashlib.sha256(text.encode()).hexdigest()==c['fixture']['fixture_sha256']

def mul(a,b):
    coeff=[0]*23
    for i in range(12):
        for j in range(12):coeff[i+j]^=(a>>i&1)&(b>>j&1)
    for k in range(22,11,-1):
        if coeff[k]:
            for e in (0,1,4,6,12):coeff[k-12+e]^=1
    assert not any(coeff[12:])
    return sum(coeff[i]<<i for i in range(12))
for i in range(12):
    for j in range(12):assert mul(1<<i,1<<j)==f.weights()[i+j]

state=0x20261110
def draw():
    global state
    state=(1664525*state+1013904223)&0xffffffff
    return state>>12&4095
rows=[]
for s in range(256):
    a,b=(1<<(s//12),1<<(s%12))if s<144 else(draw(),draw())
    cc,z=draw(),draw()
    if s<12:z=1<<s
    mode=s%5
    if s>=144 and mode in (2,3,4):a=b=cc=1
    rows.append((a,b,cc,z,int(s<144 or s%2==0),mode))
assert rows==f.inputs()
iq=[0]*85;ib=[0]*727
for s,(a,b,cc,z,on,mode)in enumerate(rows):
    for start,v in ((0,a),(12,b),(24,cc),(36,z),(48,z)):
        for k in range(12):iq[start+k]|=(v>>k&1)<<s
    ib[0]|=on<<s
    for k in (1,2,3,4):ib[k]|=int(mode==k)<<s
    ib[5]|=int(mode!=2)<<s;ib[6]|=int(mode!=3)<<s
assert ib[3].bit_count()==51

order=[];seen=set();hmr=[]
for line in text.splitlines():
    t=line.split()
    if t[0]=='HMR':hmr.append(int(t[2][1:]))
    for v in t[1:]:
        if v.startswith('b')and v[1:].isdigit():
            i=int(v[1:])
            if i not in seen:order.append(i);seen.add(i)
inverse=[-1]*727
for j,i in enumerate(order):inverse[i]=j
cm=c['classical_mapping']
assert len(order)==726 and sorted(set(range(727))-seen)==[3]
assert cm['original_num_bits']==727 and cm['compact_num_bits']==726
assert cm['bit_map']==order and cm['bit_compact']==inverse
assert cm['HMR_original_ids']==hmr==list(range(7,727))==meta['measurement_bits']
assert cm['input_original_ids']==[0,1,2,4,5,6]and cm['input_compact_ids']==[0,146,292,725,147,2]
assert hashlib.sha256(json.dumps(order,separators=(',',':')).encode()).hexdigest()==cm['map_sha256']

def decode(item):
    b=base64.b64decode(item['base64'],validate=True)
    assert len(b)==(85+727)*32+32
    assert hashlib.sha256(b).hexdigest()==item['sha256']
    v=[int.from_bytes(b[i:i+32],'little')for i in range(0,len(b),32)]
    return b,v[:85],v[85:812],v[812]
raw,oq,ob,op=decode(c['raw_official']);eraw,eq,eb,ep=decode(c['raw_engine'])
assert raw==eraw and oq==eq and ob==eb and op==ep
assert ob[3]==eb[3]==ib[3]
native_compact=b''.join(eb[i].to_bytes(32,'little')for i in order)
assert hashlib.sha256(native_compact).hexdigest()==c['engine_compact_classical_sha256']

def word(q,start,s):return sum((q[start+k]>>s&1)<<k for k in range(12))
expected=[];expected_phase=expected_scratch=0;faults=Counter()
for s,(a,b,cc,z,on,mode)in enumerate(rows):
    z1=z^(mul(a,b)if on else 0)
    if on and mode==1:z1^=1
    a1=a^(mul(z if mode==2 else z1,cc)if on else 0)
    a2=a1^(mul(z1,cc)if on else 0)
    z2=z1^(mul(a2,b)if on else 0)
    missing=int(on and mode==3)*(a&1)*(b&1)*(ob[7]>>s&1)
    dirty=int(on and mode==4)*(a2&1)*(b&1)
    expected_phase|=missing<<s;expected_scratch|=dirty<<s
    faults['wrong_product']+=int(on and mode==1 and z2!=z)
    faults['wrong_dependency']+=int(on and mode==2 and(a2!=a or z2!=z))
    faults['missing_phase']+=missing;faults['incomplete_cleanup']+=dirty
    expected.append((z1,a1,a2,z2))

q=iq.copy();bits=ib.copy();phase=0;counts=Counter();stack=[M];observed_hmr=[];stages=[]
for ln,line in enumerate(text.splitlines(),1):
    t=line.split();kind=t[0]
    if kind=='PUSH_CONDITION':stack.append(stack[-1]&bits[int(t[-1][1:])]);counts[kind]+=256
    elif kind=='POP_CONDITION':assert len(stack)>1;stack.pop();counts[kind]+=256
    else:
        mask=stack[-1]
        if 'if'in t:
            at=t.index('if');mask&=bits[int(t[at+1][1:])];t=t[:at]
        x=[int(z[1:])for z in t[1:]];counts[kind]+=mask.bit_count()
        if kind=='CCX':q[x[2]]^=q[x[0]]&q[x[1]]&mask
        elif kind=='CX':q[x[1]]^=q[x[0]]&mask
        elif kind=='X':q[x[0]]^=mask
        elif kind=='CZ':phase^=q[x[0]]&q[x[1]]&mask
        elif kind=='HMR':
            assert x[1]not in observed_hmr;observed_hmr.append(x[1])
            outcome=ob[x[1]];assert outcome&~mask==0
            phase^=q[x[0]]&outcome&mask;q[x[0]]&=M^mask;bits[x[1]]=outcome
        else:raise AssertionError('unexpected opcode '+kind)
    for name,end in meta['stages'].items():
        if ln==end:
            assert q[84]==0 and phase==expected_phase
            for s,(a,b,cc,z,on,mode)in enumerate(rows):
                z1,a1,a2,z2=expected[s]
                want_a=a if name=='after_first'else a1 if name=='after_second'else a2
                want_z=z2 if name=='after_reverse_first'else z1
                assert word(q,0,s)==want_a and word(q,36,s)==want_z
                assert word(q,60,s)==(z1 if on else 0)
                if name!='after_first':assert word(q,72,s)==(a1 if on else 0)
                assert word(q,12,s)==b and word(q,24,s)==cc and word(q,48,s)==z
            stages.append(name)
assert len(stages)==4 and len(stack)==1
assert q==oq and bits==ob and phase==op==expected_phase
assert q[84]==expected_scratch and bits[:7]==ib[:7]
assert observed_hmr==hmr
assert dict(counts)==c['charged_counts']==c['official']['expected_counts']==c['engine']['expected_counts']
assert counts['CCX']==115240 and counts['HMR']==115200 and counts['CZ']==57996
assert dict(faults)=={'wrong_product':40,'wrong_dependency':40,'missing_phase':5,'incomplete_cleanup':12}
assert op.bit_count()==5 and q[84].bit_count()==12
for s,(_,_,_,_,on,mode)in enumerate(rows):
    if mode==0 or not on:
        assert all((q[i]>>s&1)==(iq[i]>>s&1)for i in range(60))
        assert not(op>>s&1)and not(q[84]>>s&1)
assert c['reaction_depth']==3 and not any(c['mismatches'].values())
assert c['shots_per_backend']==256 and c['backend_shots']==512 and c['seed']==7 and c['modulus']==4179
assert r['status']==r['containment']=='PASS'and json.loads(r['pilot_container']['stdout'])==c
assert r['verified_cgroup_limits']=={'memory.max':'536870912','memory.swap.max':'0','cpu.max':'100000 100000','pids.max':'16'}
controls={v['mode']:v for v in r['controls']}
assert controls['memory']['OOMKilled']and controls['memory']['returncode']==137
assert controls['memory']['after']['memory.events']['oom_kill']-controls['memory']['before']['memory.events']['oom_kill']==1
assert controls['pids']['after']['pids.events']['max']>controls['pids']['before']['pids.events']['max']
assert json.loads(controls['pids']['stdout'])['threads_created']==15
assert json.loads(controls['scratch']['stdout'])['scratch_limit_detected']
assert controls['cpu']['returncode']==137 and not controls['cpu']['OOMKilled']
assert controls['wall']['returncode']==137 and controls['wall']['stop_reason']=='WALL_NEGATIVE_EXPECTED'
assert all(v['child_reaped']and v['all_cgroup_processes_reaped']and v['after']['pids.current']==0 for v in r['controls']+[r['pilot_container']])
assert r['pilot_container']['returncode']==0 and not r['pilot_container']['OOMKilled']and r['pilot_container']['stop_reason']is None
assert r['cleanup_complete']and r['cgroup_empty_before_cleanup']and r['final_cgroup']['pids.current']==0
assert r['final_cgroup']['memory.peak']==536870912 and r['final_cgroup']['cpu.stat']['usage_usec']<30000000 and r['wall_seconds']<60
assert c['kickmix_binary_sha256']=='d965e0ad42e7e3a147d4b28d6971a517f772dd79795cfc364be2fe9ffe3a7b80'
assert c['engine_binary_sha256']=='74e205f8120bbfdbf5b759b42c1f344c842ed8c543da127adecf4dad1cd7db5c'
out=dict(verdict='PASS',synthetic_series='CLOSED',audit='read-only raw-transcript replay; no native rerun',source_hashes_verified=len(r['verified_source_sha256']),shots_per_backend=256,total_shots=512,original_bits=727,compact_bits=726,omitted=[3],untouched_one_rows_preserved=51,HMR_records=720,HMR_executions_per_backend=counts['HMR'],basis_products_checked=144,all_quantum_bits_checked=85*256*2,all_original_classical_bits_checked=727*256*2,engine_untouched_bit_observation='b3 carried by source-proven identity, not native compact output',raw_state_bytes=len(raw),raw_state_sha256=c['raw_official']['sha256'],native_compact_dump_sha256=c['engine_compact_classical_sha256'],stage_checks=stages,relative_phase='exact binary; all actual histories replayed',faults=dict(faults),counts=dict(counts),native_reaction_depth_agreement=3,CPU_total_contained_seconds=r['final_cgroup']['cpu.stat']['usage_usec']/1e6,CPU_pilot_contained_seconds=(r['pilot_container']['after']['cpu.stat']['usage_usec']-r['pilot_container']['before']['cpu.stat']['usage_usec'])/1e6,controller_wall_seconds=r['wall_seconds'],worker_peak_RSS_MiB=c['peak_RSS_bytes']/2**20,pilot_cgroup_peak_MiB=c['cgroup_memory_peak']/2**20,cleanup_complete=True)
(P/'AUDIT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
