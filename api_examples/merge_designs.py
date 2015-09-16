# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 17:13:42 2015

@author: danaukes
"""
#import sys
#import PySide.QtGui as qg
#app = qg.QApplication(sys.argv[0])

import popupcad
import design_advanced_functions
#from popupcad.manufacturing.dummy_operation1 import DummyOp1

from popupcad.filetypes.design import Design
from popupcad.manufacturing.sub_operation2 import SubOperation2
#from popupcad.manufacturing.transform_external import TransformExternal
#from popupcad.manufacturing.transform_internal import TransformInternal

#design = Design.open()
#subdesign = Design.open()

#get design
design = Design.load_yaml('C:/Users/danaukes/popupCAD_files/designs/hinges/supported_hinge.cad')
#subdesign = Design.load_yaml('C:/Users/danaukes/popupCAD_files/designs/hinges/supported_hinge_half1.cad')
design = design.upgrade()

#get subdesign
subdesign = design.subdesigns[338535312]

#upgrade is unnecessary if subdesign is a child of design
#subdesign = subdesign.upgrade()

#ensure subdesign is a totally separate copy
subdesign = subdesign.copy_yaml()

#reassign new ids to subdesign sketches and remap their use within the subdesign
sketch_mapping = design_advanced_functions.remap_sketch_ids(subdesign)

test_file = 'C:/Users/danaukes/desktop/test.cad'
subdesign.save_yaml(test_file)

#design_sketches_new = subdesign.sketches
#design_sketches_new.update(design.sketches)
#design.sketches = design_sketches_new
design.sketches.update(subdesign.sketches)

test_file = 'C:/Users/danaukes/desktop/test2.cad'
design.save_yaml(test_file)

design_advanced_functions.strip_locates(subdesign)

op_mapping = design_advanced_functions.remap_operation_ids(subdesign)

design_advanced_functions.switch_layer_defs(subdesign,design.return_layer_definition())

subdesign.save_yaml('C:/Users/danaukes/desktop/test3.cad')

design.operations = subdesign.operations+design.operations

design.save_yaml('C:/Users/danaukes/desktop/test4.cad')

design_advanced_functions.external_to_internal_transform_outer(design,subdesign,sketch_mapping,op_mapping)

if subdesign.id in design.subdesigns:
    del design.subdesigns[subdesign.id]
        
test_file = 'C:/Users/danaukes/desktop/test5.cad'
design.save_yaml(test_file)
