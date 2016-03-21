# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
def remap_subdesign_ids(design):
    subdesigns_orig = design.subdesigns.copy()
    subdesign_mapping = []
    subdesigns_new = {} 
    for key,subdesign in subdesigns_orig.items():
        new_sketch = subdesign.copy(identical = False)
        subdesigns_new[new_sketch.id] = new_sketch
        subdesign_mapping.append((key,new_sketch.id))

    for oldref, newref in subdesign_mapping:
        design.replace_subdesign_refs(oldref,newref)
    
    design.subdesigns = subdesigns_new
    return subdesign_mapping

def remap_sketch_ids(design):
    sub_sketches_orig = design.sketches.copy()
    sketch_mapping = []
    sub_sketches_new = {} 
    for key,sketch in sub_sketches_orig.items():
        new_sketch = sketch.copy(identical = False)
        sub_sketches_new[new_sketch.id] = new_sketch
        sketch_mapping.append((key,new_sketch.id))

    for oldref, newref in sketch_mapping:
        design.replace_sketch_refs_force(oldref,newref)
    
    design.sketches = sub_sketches_new
    return sketch_mapping
    
def strip_locates(design):
    for ii in range(len(design.operations))[::-1]:
        op = design.operations[ii]
        if hasattr(op,'locationgeometry'):
            design.pop_operation(ii)
            
def remap_operation_ids(design):
    op_mapping = []
    sub_ops_new = []
    for op in design.operations:
        new_op = op.copy_wrapper()
        new_op.id = id(new_op)
        sub_ops_new.append(new_op)
        op_mapping.append((op,new_op))    
        
    design.operations = sub_ops_new
    
    for oldref,newref in [(op1.id,op2.id) for op1,op2 in op_mapping]:
        design.replace_op_refs2(oldref,newref)    

    return op_mapping
    
def switch_layer_defs(design,layerdef_new):
    for ii,op in enumerate(design.operations):
        if hasattr(op,'switch_layer_defs'):
            design.operations[ii]=op.switch_layer_defs(design.return_layer_definition(),layerdef_new)
    
def external_to_internal_transform_outer(design,subdesign,sketch_mapping,op_mapping):
    op_mapping2 = []

    from popupcad.manufacturing.transform_external import TransformExternal
    sketch_mapping_dict = dict(sketch_mapping)
    op_mapping_dict = dict([(item1.id,item2.id) for item1,item2 in op_mapping])
    for ii,op in enumerate(design.operations):
        if isinstance(op, TransformExternal):
            if op.design_links['subdesign'][0] == subdesign.id:
                new = op.to_internal_transform(sketch_mapping_dict,op_mapping_dict)
                design.operations[ii]=new
                op_mapping2.append((op.id,new.id))
    
    for oldref,newref in op_mapping2:
        design.replace_op_refs2(oldref,newref)

def remap_sub(subdesign):
    #reassign new ids to subdesign sketches and remap their use within the subdesign

    debug = True

    subdesign_mapping = remap_subdesign_ids(subdesign)
    sketch_mapping = remap_sketch_ids(subdesign)
    strip_locates(subdesign)
    op_mapping = remap_operation_ids(subdesign)
    if debug:
        subdesign.save_yaml('C:/Users/danaukes/desktop/test.cad')
    return subdesign_mapping,sketch_mapping,op_mapping


def merge_designs(design,subdesign,index):
    debug = True
    subdesign_mapping,sketch_mapping,op_mapping = remap_sub(subdesign)

    design.subdesigns.update(subdesign.subdesigns)
    design.sketches.update(subdesign.sketches)
    if debug:
        design.save_yaml('C:/Users/danaukes/desktop/test2.cad')
    
    switch_layer_defs(subdesign,design.return_layer_definition())
    if debug:
        subdesign.save_yaml('C:/Users/danaukes/desktop/test3.cad')
    
    design.operations = design.operations[:index]+subdesign.operations+design.operations[index:]
    if debug:
        design.save_yaml('C:/Users/danaukes/desktop/test4.cad')

    return subdesign_mapping,sketch_mapping,op_mapping
    
    
