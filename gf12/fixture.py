"""New public synthetic GF(2^12) fixture; no competition circuit/source input."""
import hashlib
from collections import Counter

MODULUS=0x1053  # x^12+x^6+x^4+x+1, official default polynomial.
SEED=7
SHOTS=256
ALL=(1<<SHOTS)-1
NQ=85

def multiply_reference(a,b):
    """Carryless integer product then polynomial long division (independent of emitter)."""
    assert 0<=a<4096 and 0<=b<4096
    product=0
    for j in range(12):
        if (b>>j)&1:product^=a<<j
    for j in range(22,11,-1):
        if (product>>j)&1:product^=MODULUS<<(j-12)
    return product

def emitter_weights():
    """Successive x powers, reduced one shift at a time, for all 23 monomials."""
    value=1;weights=[]
    for k in range(23):
        weights.append(value);value<<=1
        if value&4096:value^=MODULUS
    return weights

def inputs():
    # First 144 positions cover every monomial pair; the remainder add dense data.
    state=0x20261110
    def word():
        nonlocal state
        state=(1664525*state+1013904223)&0xffffffff
        return (state>>12)&4095
    rows=[]
    for s in range(SHOTS):
        a,b=(1<<(s//12),1<<(s%12))if s<144 else(word(),word())
        if s>=144 and s%4==2:a=b=1  # Nonzero omitted-repair phase probes.
        z=word()
        if s<12:z=1<<s
        rows.append((a,b,z,int(s<144 or s%2==0),s%4))
    return rows

def build():
    lines=[];next_bit=4;weights=emitter_weights();missing_bit=None;measurements=[]
    def op(s):lines.append(s)
    def mac(target,reverse=False,omit=False):
        nonlocal next_bit,missing_bit
        pairs=[(i,j)for i in range(12)for j in range(12)]
        if reverse:pairs.reverse()
        for i,j in pairs:
            bit=next_bit;next_bit+=1;measurements.append(bit)
            op(f'CCX q{i} q{12+j} q84')
            for k in range(12):
                if weights[i+j]>>k&1:op(f'CX q84 q{target+k}')
            op(f'HMR q84 b{bit}')
            if omit and i==j==0:missing_bit=bit
            else:op(f'CZ q{i} q{12+j} if b{bit}')
    op('PUSH_CONDITION if b0')
    mac(24)
    for k in range(12):op(f'CX q{24+k} q{36+k}')
    mac(24,reverse=True)
    op('PUSH_CONDITION if b1');mac(48);op('X q48');op('POP_CONDITION')
    op('PUSH_CONDITION if b2');mac(60,omit=True);op('POP_CONDITION')
    op('PUSH_CONDITION if b3');mac(72)
    dirty_bit=next_bit;next_bit+=1;measurements.append(dirty_bit)
    op(f'HMR q79 b{dirty_bit}');op('POP_CONDITION');op('POP_CONDITION')
    text='\n'.join(lines)+'\n'
    meta=dict(num_qubits=NQ,num_bits=next_bit,static_toffoli=sum(s.startswith('CCX ')for s in lines),missing_repair_bit=missing_bit,dirty_reset_bit=dirty_bit,measurement_bits=measurements,fixture_sha256=hashlib.sha256(text.encode()).hexdigest())
    return text,meta

def pack(values,width):return [sum(((v>>k)&1)<<s for s,v in enumerate(values))for k in range(width)]
def unpack_word(q,start):return [sum(((q[start+k]>>s)&1)<<k for k in range(12))for s in range(SHOTS)]

def initial_state():
    rows=inputs();q=[0]*NQ;_,meta=build();bits=[0]*meta['num_bits']
    q[:12]=pack([r[0]for r in rows],12);q[12:24]=pack([r[1]for r in rows],12)
    z=pack([r[2]for r in rows],12)
    for start in (24,48,60,72):q[start:start+12]=z
    for s,(_,_,_,enabled,mode)in enumerate(rows):
        bits[0]|=enabled<<s
        for k in (1,2,3):bits[k]|=int(mode==k)<<s
    return q,bits

def replay(text,initial_q,initial_bits,measured_bits):
    """Exact 256-way gate/phase oracle using the actual recorded HMR transcript."""
    q=initial_q.copy();bits=initial_bits.copy();stack=[ALL];phase=0;counts=Counter()
    for line in text.splitlines():
        t=line.split();name=t[0]
        if name=='PUSH_CONDITION':
            assert t[1]=='if';stack.append(stack[-1]&bits[int(t[2][1:])]);counts[name]+=SHOTS;continue
        if name=='POP_CONDITION':stack.pop();counts[name]+=SHOTS;continue
        mask=stack[-1]
        if 'if'in t:
            i=t.index('if');mask&=bits[int(t[i+1][1:])];t=t[:i]
        counts[name]+=mask.bit_count();ids=[int(v[1:])for v in t[1:]]
        if name=='X':q[ids[0]]^=mask
        elif name=='CX':q[ids[1]]^=q[ids[0]]&mask
        elif name=='CCX':q[ids[2]]^=q[ids[0]]&q[ids[1]]&mask
        elif name=='CZ':phase^=q[ids[0]]&q[ids[1]]&mask
        elif name=='HMR':
            value=measured_bits[ids[1]]
            assert not(value&~mask),'skipped HMR outcome must remain zero'
            bits[ids[1]]=value;phase^=q[ids[0]]&value&mask;q[ids[0]]&=ALL^mask
        else:raise ValueError('illegal fixture operation '+name)
    assert len(stack)==1
    return q,bits,phase,dict(counts)

def validate(q,bits,phase,counts):
    text,meta=build();iq,ib=initial_state()
    eq,eb,ep,ec=replay(text,iq,ib,bits)
    assert q==eq and bits==eb and phase==ep,'gate/phase/transcript mismatch'
    assert {k:v for k,v in counts.items()if v}=={k:v for k,v in ec.items()if v},'charged/opcode count mismatch'
    assert q[:24]==iq[:24] and q[24:36]==iq[24:36] and q[84]==0,'input/inverse/scratch mismatch'
    snapshot=unpack_word(q,36);wp=unpack_word(q,48);mp=unpack_word(q,60);dt=unpack_word(q,72)
    wrong=missing_phase=dirty_value=dirty_phase=normal=0
    expected_phase=0;active=0;negative_active=0
    for s,(a,b,z,e,mode)in enumerate(inputs()):
        prod=multiply_reference(a,b);expected=z^(prod if e else 0)
        assert snapshot[s]==(expected if e else 0),'correct dirty-target XOR product'
        for name,values,tag in [('wrong_product',wp,1),('missing_phase',mp,2),('dirty_target',dt,3)]:
            want=z^(prod if e and mode==tag else 0)
            if name=='wrong_product':
                assert values[s]==(want^(1 if e and mode==tag else 0));wrong+=int(values[s]!=want)
            elif name=='missing_phase':assert values[s]==want
            else:
                assert values[s]==(want&~128 if e and mode==tag else want);dirty_value+=int(values[s]!=want)
        m=(bits[meta['missing_repair_bit']]>>s)&1
        f=int(e and mode==2 and (a&1)and(b&1))*m
        v=(bits[meta['dirty_reset_bit']]>>s)&1
        g=int(e and mode==3)*((z^prod)>>7&1)*v
        expected_phase|=(f^g)<<s;missing_phase+=f;dirty_phase+=g
        if mode==0:assert not(phase>>s&1);normal+=1
        active+=e;negative_active+=int(e and mode!=0)
    assert phase==expected_phase,'closed-form measurement-phase equation'
    assert min(wrong,missing_phase,dirty_value)>0,'negative control not detected'
    assert ec['CCX']==288*active+144*negative_active
    assert bits[:4]==ib[:4],'classical inputs changed'
    return dict(correct_MAC_and_inverse_checked_shots=256,unfaulted_phase_checked_shots=normal,enabled_shots=active,disabled_shots=256-active,negative_controls=dict(wrong_product_shots=wrong,missing_repair_phase_shots=missing_phase,dirty_target_value_shots=dirty_value,dirty_target_phase_shots=dirty_phase),expected_toffoli=ec['CCX'],expected_counts=ec,all_HMR_outcomes_retained=len(meta['measurement_bits']))

def source_check():
    text,meta=build();w=emitter_weights()
    assert MODULUS==4179 and meta['static_toffoli']==720 and meta['num_bits']==725
    # Bilinearity proves multiplication on every input from its 144 monomial pairs;
    # targets occur only as XOR destinations, proving arbitrary initial target words.
    for i in range(12):
        for j in range(12):assert w[i+j]==multiply_reference(1<<i,1<<j)
    iq,ib=initial_state();zero=ib.copy()
    # Source-only known-transcript checks. No simulator, no measurement sampling.
    for ones in (False,True):
        measured=ib.copy();stack=[ALL]
        for line in text.splitlines():
            t=line.split()
            if t[0]=='PUSH_CONDITION':stack.append(stack[-1]&measured[int(t[2][1:])])
            elif t[0]=='POP_CONDITION':stack.pop()
            elif t[0]=='HMR':measured[int(t[2][1:])]=stack[-1]if ones else 0
        q,b,ph,ct=replay(text,iq,ib,measured)
        if ones:assert validate(q,b,ph,ct)['expected_toffoli']==77184
        else:assert ph==0 and ct['CCX']==77184
    return dict(source_check='PASS',monomial_pairs=144,num_qubits=85,num_bits=725,static_CCX=720,expected_executed_CCX_per_backend=77184,fixture_sha256=meta['fixture_sha256'])
