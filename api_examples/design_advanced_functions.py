# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 15:54:21 2015

@author: danaukes
"""
def remap_sketch_ids(subdesign):
    sub_sketches_orig = subdesign.sketches.copy()
    sketch_mapping = []
    sub_sketches_new = {} 
    for key,sketch in sub_sketches_orig.items():
        new_sketch = sketch.copy(identical = False)
        sub_sketches_new[new_sketch.id] = new_sketch
        sketch_mapping.append((key,new_sketch.id))

    for oldref, newref in sketch_mapping:
        subdesign.replace_sketch_refs_force(oldref,newref)
    
    subdesign.sketches = sub_sketches_new
    return sketch_mapping
    
def strip_locates(subdesign):
    for ii in range(len(subdesign.operations))[::-1]:
        op = subdesign.operations[ii]
        if hasattr(op,'locationgeometry'):
            subdesign.operations.pop(ii)
            
def remap_operation_ids(subdesign):
    op_mapping = []
    sub_ops_new = []
    for op in subdesign.operations:
        new_op = op.copy_wrapper()
        new_op.id = id(new_op)
        sub_ops_new.append(new_op)
        op_mapping.append((op,new_op))    
        
    for oldref,newref in op_mapping:
        subdesign.replace_op_refs2(oldref,newref)    

    subdesign.operations = sub_ops_new

    return op_mapping
    
def switch_layer_defs(subdesign,layerdef_new):
    for ii,op in enumerate(subdesign.operations):
        if hasattr(op,'switch_layer_defs'):
            subdesign.operations[ii]=op.switch_layer_defs(subdesign.return_layer_definition(),layerdef_new)
    
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
        