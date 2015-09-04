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

design = Design.load_yaml('C:\\Users\\danaukes\\popupCAD_files\\designs\\hinges\\supported_hinge.cad')
subdesign = Design.load_yaml('C:\\Users\\danaukes\\popupCAD_files\\designs\\hinges\\supported_hinge_half1.cad')

design = design.upgrade()
subdesign = subdesign.upgrade()

sub_sketches_orig = subdesign.sketches
sketch_mapping = []
sub_sketches_new = {} 
for key,sketch in sub_sketches_orig.items():
    new_sketch = sketch.copy(identical = False)
    sub_sketches_new[new_sketch.id] = new_sketch
    sketch_mapping.append((key,new_sketch.id))
#
#sketches = design.sketches.copy()
#for key,value in sketches.items():
#    sketches[key] = value.copy()
#subdesign.sketches.update(sketches)
#
#layerdef_subdesign = subdesign.return_layer_definition()
#layerdef_design = design.return_layer_definition()
#
#for sketch_data in self.sketch_list:
#    from_ref = sketch_data.ref1
#    to_ref = sketch_data.ref2
#    subdesign.replace_sketch_refs_force(from_ref, to_ref)
#
#for input_data in self.input_list:
#    from_ref = input_data.ref1
#    to_ref = input_data.ref2
#
#    csg = design.op_from_ref(to_ref[0]).output[to_ref[1]].csg
#    csg2 = popupcad.algorithms.manufacturing_functions.shift_flip_rotate(csg,input_data.shift,False,False)
#    csg3 = csg2.switch_layer_defs(layerdef_subdesign)
#    dummy_op = DummyOp1(csg3)
#    to_ref2 = (dummy_op.id,0)
#    subdesign.operations.insert(0, dummy_op)
#    subdesign.replace_op_refs_force(from_ref, to_ref2)
#
#subdesign.reprocessoperations()
