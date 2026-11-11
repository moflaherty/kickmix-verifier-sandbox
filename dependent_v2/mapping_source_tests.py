"""Source-only metadata proofs; no native compiler/simulator dependency."""
from types import SimpleNamespace
import json
import fixture
from classical_mapping import source_layout,validate_program,expand_original

def object_for(p):return SimpleNamespace(orig_num_bits=p['original_num_bits'],num_bits=p['compact_num_bits'],bit_map=p['bit_map'].copy(),bit_compact=p['bit_compact'].copy())
def reject(p,obj):
    try:validate_program(obj,p)
    except ValueError:return
    raise AssertionError('invalid map accepted')
def run():
    minimal='PUSH_CONDITION if b0\nHMR q0 b2\nPOP_CONDITION\n'
    p=source_layout(minimal,3,2)
    assert p['bit_map']==[0,2]and p['bit_compact']==[0,-1,1]
    assert p['bit_map']!=list(range(3))  # Original assertion fails by construction.
    validate_program(object_for(p),p)
    assert expand_original([5,0b101,0],p['bit_map'],[5,0b110])==[5,0b101,0b110]
    text,meta=fixture.build();plan=source_layout(text,727,7)
    want=[0,7,6]+list(range(8,151))+[1,5]+list(range(151,295))+[2]+list(range(295,727))+[4]
    assert plan['bit_map']==want and plan['compact_num_bits']==726
    assert plan['omitted_original_bits']==[3]and plan['bit_compact'][3]==-1
    assert plan['HMR_original_ids']==list(range(7,727))==meta['measurement_bits']
    assert plan['input_original_ids']==[0,1,2,4,5,6]
    assert plan['input_compact_ids']==[0,146,292,725,147,2]
    iq,ib=fixture.initial_state();assert ib[3].bit_count()==51
    validate_program(object_for(plan),plan)
    synthetic=[ib[i]for i in plan['bit_map']]
    assert expand_original(ib,plan['bit_map'],synthetic)==ib
    defects=0
    for i in (0,7,726):
        obj=object_for(plan);obj.bit_map.remove(i);reject(plan,obj);defects+=1
    obj=object_for(plan);obj.bit_map[0]=obj.bit_map[1];reject(plan,obj);defects+=1
    obj=object_for(plan);obj.bit_compact[3]=0;reject(plan,obj);defects+=1
    obj=object_for(plan);obj.bit_compact[7]=-1;reject(plan,obj);defects+=1
    obj=object_for(plan);obj.orig_num_bits=726;reject(plan,obj);defects+=1
    obj=object_for(plan);obj.bit_map[0],obj.bit_map[1]=obj.bit_map[1],obj.bit_map[0];reject(plan,obj);defects+=1
    return dict(status='SOURCE_ONLY_PASS',native_executed=False,original_bits=727,expected_compact_bits=726,omitted=[3],omitted_initial_one_shots=51,HMR_outputs_preserved=720,input_original_ids=plan['input_original_ids'],input_compact_ids=plan['input_compact_ids'],invalid_mapping_controls_rejected=defects,minimal_map=[0,2],fixture_source_check=fixture.source_check()),plan

if __name__=='__main__':print(json.dumps(run()[0]))
