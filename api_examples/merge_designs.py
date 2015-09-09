# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 17:13:42 2015

@author: danaukes
"""
#import sys
#import PySide.QtGui as qg
#app = qg.QApplication(sys.argv[0])

import popupcad

#from popupcad.manufacturing.dummy_operation1 import DummyOp1

from popupcad.filetypes.design import Design

#design = Design.open()
#subdesign = Design.open()
overwrite_sketches = False
overwrite_operations = False

design = Design.load_yaml('C:/Users/danaukes/popupCAD_files/designs/hinges/supported_hinge.cad')
#subdesign = Design.load_yaml('C:/Users/danaukes/popupCAD_files/designs/hinges/supported_hinge_half1.cad')
design = design.upgrade()

subdesign = design.subdesigns[338535312]
subdesign = subdesign.copy_yaml()

#subdesign = subdesign.upgrade()
#
if not overwrite_sketches:
    sub_sketches_orig = subdesign.sketches.copy()
    sketch_mapping = []
    sub_sketches_new = {} 
    for key,sketch in sub_sketches_orig.items():
        new_sketch = sketch.copy(identical = False)
        sub_sketches_new[new_sketch.id] = new_sketch
        sketch_mapping.append((key,new_sketch.id))

    sketch_mapping_dict = dict(sketch_mapping)
    
    for oldref, newref in sketch_mapping:
        subdesign.replace_sketch_refs_force(oldref,newref)
    
    subdesign.sketches = sub_sketches_new
#
test_file = 'C:/Users/danaukes/desktop/test.cad'
subdesign.save_yaml(test_file)

design_sketches_new = subdesign.sketches
design_sketches_new.update(design.sketches)
design.sketches = design_sketches_new
#
test_file = 'C:/Users/danaukes/desktop/test2.cad'
design.save_yaml(test_file)
#
#if not overwrite_operations:
sub_ops_orig = subdesign.operations
op_mapping = []
sub_ops_new = []
sub_ops_old = subdesign.operations.copy()
for op in subdesign.operations:
    if not hasattr(op,'locationgeometry'):
        new_op = op.copy_wrapper()
        new_op.id = id(new_op)
        sub_ops_new.append(new_op)
        op_mapping.append((op,new_op))    
    
for oldref,newref in op_mapping:
    subdesign.replace_op_refs2(oldref,newref)

for ii,op in enumerate(sub_ops_new):
    if hasattr(op,'switch_layer_defs'):
        sub_ops_new[ii]=op.switch_layer_defs(subdesign.return_layer_definition(),design.return_layer_definition())
subdesign.operations = sub_ops_new

test_file = 'C:/Users/danaukes/desktop/test3.cad'
subdesign.save_yaml(test_file)

design.operations = subdesign.operations+design.operations
#design.cleanup_sketches()

test_file = 'C:/Users/danaukes/desktop/test4.cad'
design.save_yaml(test_file)

from popupcad.manufacturing.transform_external import TransformExternal
from popupcad.manufacturing.transform_internal import TransformInternal

op_mapping_dict = dict([(item1.id,item2.id) for item1,item2 in op_mapping])

op_mapping2 = []

for ii,op in enumerate(design.operations):
    if isinstance(op, TransformExternal):
        if op.design_links['subdesign'][0] == subdesign.id:
            sketch_links = op.sketch_links.copy()
            sketch_links['sketch_from'] = [sketch_mapping_dict[op.sub_sketch_id]]
            operation_link = op.subopref
            operation_link = op_mapping_dict[operation_link[0]],operation_link[1]
            operation_links = {'from':[operation_link]}
            new = TransformInternal(sketch_links,operation_links,op.transformtype_x,op.transformtype_y,op.shift,op.flip,op.scalex,op.scaley)
            new.customname = op.customname
            design.operations[ii]=new
            op_mapping2.append((op.id,new.id))

for oldref,newref in op_mapping2:
    design.replace_op_refs2(oldref,newref)

#design.cleanup_sketches()
design.cleanup_subdesigns()
        
test_file = 'C:/Users/danaukes/desktop/test5.cad'
design.save_yaml(test_file)
#
##sketches = design.sketches.copy()
##for key,value in sketches.items():
##    sketches[key] = value.copy()
##subdesign.sketches.update(sketches)
#
##
##layerdef_subdesign = subdesign.return_layer_definition()
##layerdef_design = design.return_layer_definition()
##
##for sketch_data in self.sketch_list:
##    from_ref = sketch_data.ref1
##    to_ref = sketch_data.ref2
##    subdesign.replace_sketch_refs_force(from_ref, to_ref)
##
##for input_data in self.input_list:
##    from_ref = input_data.ref1
##    to_ref = input_data.ref2
##
##    csg = design.op_from_ref(to_ref[0]).output[to_ref[1]].csg
##    csg2 = popupcad.algorithms.manufacturing_functions.shift_flip_rotate(csg,input_data.shift,False,False)
##    csg3 = csg2.switch_layer_defs(layerdef_subdesign)
##    dummy_op = DummyOp1(csg3)
##    to_ref2 = (dummy_op.id,0)
##    subdesign.operations.insert(0, dummy_op)
##    subdesign.replace_op_refs_force(from_ref, to_ref2)
##
##subdesign.reprocessoperations()
