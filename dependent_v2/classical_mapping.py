"""Strict, source-derived classical map for this public fixture dialect."""
import hashlib,json

def source_layout(text,declared_bits,input_count):
    order=[];seen=set();hmr=[]
    allowed={'X','CX','CCX','CZ','HMR','PUSH_CONDITION','POP_CONDITION'}
    for line in text.splitlines():
        t=line.split()
        if not t or t[0]not in allowed:raise ValueError('unsupported fixture dialect')
        if t[0]=='HMR':hmr.append(int(t[2][1:]))
        # These operations have either one bit operand or HMR's bit target
        # before its optional condition, exactly Builder::op's cb order.
        for v in t[1:]:
            if v.startswith('b')and v[1:].isdigit():
                i=int(v[1:])
                if not 0<=i<declared_bits:raise ValueError('bit outside declared range')
                if i not in seen:seen.add(i);order.append(i)
    compact=[-1]*declared_bits
    for j,i in enumerate(order):compact[i]=j
    omitted=sorted(set(range(declared_bits))-seen)
    inputs=[i for i in range(input_count)if i in seen]
    if len(hmr)!=len(set(hmr))or not set(hmr)<=seen:raise ValueError('HMR coverage')
    return dict(original_num_bits=declared_bits,compact_num_bits=len(order),bit_map=order,bit_compact=compact,omitted_original_bits=omitted,input_original_ids=inputs,input_compact_ids=[compact[i]for i in inputs],HMR_original_ids=hmr,fixture_sha256=hashlib.sha256(text.encode()).hexdigest())

def validate_program(program,plan):
    actual_map=[int(x)for x in program.bit_map]
    actual_compact=[int(x)for x in program.bit_compact]
    actual=dict(original_num_bits=int(program.orig_num_bits),compact_num_bits=int(program.num_bits),bit_map=actual_map,bit_compact=actual_compact)
    for key in actual:
        if actual[key]!=plan[key]:raise ValueError('classical map '+key+' mismatch; actual='+json.dumps(actual,separators=(',',':')))
    if len(set(actual_map))!=len(actual_map):raise ValueError('non-bijective map')
    for j,i in enumerate(actual_map):
        if actual_compact[i]!=j:raise ValueError('map inverse mismatch')
    if any(actual_compact[i]!=-1 for i in plan['omitted_original_bits']):raise ValueError('omitted sentinel mismatch')
    return dict(plan,validation='PASS',implicit_untouched_bits='carried from initial input, not dumped by engine',map_sha256=hashlib.sha256(json.dumps(actual_map,separators=(',',':')).encode()).hexdigest())

def expand_original(initial_bits,bit_map,compact_values):
    if len(compact_values)!=len(bit_map):raise ValueError('compact dump dimension')
    result=list(initial_bits)  # Preserve nonzero *untouched* inputs, never zero-fill.
    for original,value in zip(bit_map,compact_values):result[original]=value
    return result
