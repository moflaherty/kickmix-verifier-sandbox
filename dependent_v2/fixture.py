"""Public dependent GF12 arithmetic fixture; no private scientific inputs."""
import hashlib
from collections import Counter
MODULUS=0x1053
SEED=7
SHOTS=256
ALL=(1<<256)-1
NQ=85

def multiply_reference(a,b):
    # Independent carryless polynomial product and long division.
    result=0
    for j in range(12):
        if b>>j&1:result^=a<<j
    for j in range(22,11,-1):
        if result>>j&1:result^=MODULUS<<(j-12)
    return result

def weights():
    w=[];x=1
    for i in range(23):
        w.append(x);x<<=1
        if x&4096:x^=MODULUS
    return w

def inputs():
    state=0x20261110
    def word():
        nonlocal state
        state=(1664525*state+1013904223)&0xffffffff
        return state>>12&4095
    rows=[]
    for s in range(256):
        a,b=(1<<(s//12),1<<(s%12))if s<144 else(word(),word())
        c,z=word(),word()
        if s<12:z=1<<s
        mode=s%5
        if s>=144 and mode in (2,3,4):a=b=c=1
        rows.append((a,b,c,z,int(s<144 or s%2==0),mode))
    return rows

def pack(values,width):return [sum((v>>k&1)<<s for s,v in enumerate(values))for k in range(width)]
def unpack_word(q,start):return [sum((q[start+k]>>s&1)<<k for k in range(12))for s in range(256)]

def build():
    lines=[];next_bit=7;measurement_bits=[];w=weights();stages={}
    def op(s):lines.append(s)
    def mac(a,b,target,reverse=False,first=False):
        nonlocal next_bit
        pairs=[(i,j)for i in range(12)for j in range(12)]
        if reverse:pairs.reverse()
        for i,j in pairs:
            bit=next_bit;next_bit+=1;measurement_bits.append(bit)
            op(f'CCX q{a+i} q{b+j} q84')
            for k in range(12):
                if w[i+j]>>k&1:op(f'CX q84 q{target+k}')
            op(f'HMR q84 b{bit}')
            if first and i==j==0:op('PUSH_CONDITION if b6')
            op(f'CZ q{a+i} q{b+j} if b{bit}')
            if first and i==j==0:op('POP_CONDITION')
    op('PUSH_CONDITION if b0')
    mac(0,12,36,first=True)
    op('X q36 if b1')  # Wrong product in selected shots only.
    for k in range(12):op(f'CX q{36+k} q{60+k}')
    stages['after_first']=len(lines)
    op('PUSH_CONDITION if b5');mac(36,24,0);op('POP_CONDITION')
    op('PUSH_CONDITION if b2');mac(48,24,0);op('POP_CONDITION')  # Wrong: original Z.
    for k in range(12):op(f'CX q{k} q{72+k}')
    stages['after_second']=len(lines)
    mac(36,24,0,reverse=True)
    stages['after_reverse_second']=len(lines)
    mac(0,12,36,reverse=True)
    stages['after_reverse_first']=len(lines)
    op('CCX q0 q12 q84 if b4')  # Incomplete cleanup: leave one borrowed AND.
    op('POP_CONDITION')
    text='\n'.join(lines)+'\n'
    return text,dict(num_qubits=85,num_bits=next_bit,static_toffoli=721,measurement_bits=measurement_bits,missing_repair_bit=7,stages=stages,fixture_sha256=hashlib.sha256(text.encode()).hexdigest())

def initial_state():
    rows=inputs();q=[0]*85;bits=[0]*727
    for start,column in ((0,0),(12,1),(24,2),(36,3),(48,3)):
        q[start:start+12]=pack([r[column]for r in rows],12)
    for s,(a,b,c,z,on,mode)in enumerate(rows):
        bits[0]|=on<<s
        for k in (1,2,3,4):bits[k]|=int(mode==k)<<s
        bits[5]|=int(mode!=2)<<s;bits[6]|=int(mode!=3)<<s
    return q,bits

def replay(text,iq,ib,transcript):
    q=iq.copy();bits=ib.copy();phase=0;counts=Counter();stack=[ALL]
    for line in text.splitlines():
        t=line.split();op=t[0]
        if op=='PUSH_CONDITION':stack.append(stack[-1]&bits[int(t[-1][1:])]);counts[op]+=256;continue
        if op=='POP_CONDITION':stack.pop();counts[op]+=256;continue
        mask=stack[-1]
        if 'if'in t:
            at=t.index('if');mask&=bits[int(t[at+1][1:])];t=t[:at]
        x=[int(v[1:])for v in t[1:]];counts[op]+=mask.bit_count()
        if op=='CCX':q[x[2]]^=q[x[0]]&q[x[1]]&mask
        elif op=='CX':q[x[1]]^=q[x[0]]&mask
        elif op=='X':q[x[0]]^=mask
        elif op=='CZ':phase^=q[x[0]]&q[x[1]]&mask
        elif op=='HMR':
            value=transcript[x[1]];assert value&~mask==0
            phase^=q[x[0]]&value&mask;q[x[0]]&=ALL^mask;bits[x[1]]=value
        else:raise ValueError('illegal operation '+op)
    assert len(stack)==1
    return q,bits,phase,dict(counts)

def validate(q,bits,phase,counts,require_negative=True):
    text,meta=build();iq,ib=initial_state();eq,eb,ep,ec=replay(text,iq,ib,bits)
    assert q==eq and bits==eb and phase==ep,'gate/phase/transcript mismatch'
    assert {k:v for k,v in counts.items()if v}=={k:v for k,v in ec.items()if v},'exact operation ledger mismatch'
    assert q[12:36]==iq[12:36]and q[48:60]==iq[48:60]and bits[:7]==ib[:7],'preserved input changed'
    result={start:unpack_word(q,start)for start in (0,36,60,72)}
    wrong_product=wrong_dependency=missing_phase=incomplete_cleanup=enabled=unfaulted=0;want_phase=0;want_scratch=0
    for s,(a,b,c,z,on,mode)in enumerate(inputs()):
        z1=z^(multiply_reference(a,b)if on else 0)
        if on and mode==1:z1^=1
        a1=a^(multiply_reference(z if mode==2 else z1,c)if on else 0)
        a2=a1^(multiply_reference(z1,c)if on else 0)
        z2=z1^(multiply_reference(a2,b)if on else 0)
        assert result[60][s]==(z1 if on else 0)and result[72][s]==(a1 if on else 0),'changed-operand forward stage'
        assert result[0][s]==a2 and result[36][s]==z2,'inverse/fault equation'
        if on and mode==1:wrong_product+=int(z2!=z)
        if on and mode==2:wrong_dependency+=int(a2!=a or z2!=z)
        f=int(on and mode==3)*(a&1)*(b&1)*(bits[7]>>s&1)
        missing_phase+=f;want_phase|=f<<s
        dirty=int(on and mode==4)*(a2&1)*(b&1);want_scratch|=dirty<<s;incomplete_cleanup+=dirty
        if mode==0:
            assert a2==a and z2==z and not(phase>>s&1)and not(q[84]>>s&1);unfaulted+=1
        if not on:assert a2==a and z2==z and not(phase>>s&1)and not(q[84]>>s&1)
        enabled+=on
    assert phase==want_phase and q[84]==want_scratch,'phase or cleanup defect not predicted'
    assert ec['CCX']==576*enabled+40==115240 and ec['HMR']==576*enabled==115200
    if require_negative:assert min(wrong_product,wrong_dependency,missing_phase,incomplete_cleanup)>0,'negative control missing'
    return dict(primary_sequence_checked_shots=256,unfaulted_rows=unfaulted,enabled_shots=enabled,disabled_shots=256-enabled,negative_controls=dict(wrong_product_shots=wrong_product,wrong_dependency_shots=wrong_dependency,missing_repair_phase_shots=missing_phase,incomplete_cleanup_shots=incomplete_cleanup),expected_toffoli=ec['CCX'],expected_counts=ec,all_HMR_outcomes_retained=720)

def source_check():
    text,meta=build();iq,ib=initial_state()
    assert meta['num_bits']==727 and sum(s.startswith('CCX ')for s in text.splitlines())==721
    for i in range(12):
        for j in range(12):assert weights()[i+j]==multiply_reference(1<<i,1<<j)
    for ones in (False,True):
        transcript=ib.copy();stack=[ALL]
        for line in text.splitlines():
            t=line.split()
            if t[0]=='PUSH_CONDITION':stack.append(stack[-1]&transcript[int(t[-1][1:])])
            elif t[0]=='POP_CONDITION':stack.pop()
            elif t[0]=='HMR':transcript[int(t[2][1:])]=stack[-1]if ones else 0
        q,b,phase,counts=replay(text,iq,ib,transcript)
        report=validate(q,b,phase,counts,require_negative=ones)
        if not ones:assert phase==0
    return dict(source_check='PASS',monomial_pairs=144,num_qubits=85,num_bits=727,static_CCX=721,expected_executed_CCX_per_backend=115240,expected_executed_HMR_per_backend=115200,fixture_sha256=meta['fixture_sha256'],all_zero_and_one_transcript_checks='PASS',all_one_controls=report['negative_controls'])
