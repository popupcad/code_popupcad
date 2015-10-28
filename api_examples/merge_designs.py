# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 17:13:42 2015

@author: danaukes
"""
#import sys
#import qt
#qc = qt.QtCore
#qg = qt.QtGui
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
if __name__=='__main__':
    
    #get design
    design = Design.load_yaml('C:/Users/danaukes/Dropbox/zhis sentinal 11 files/modified/sentinal 11 manufacturing_R07.cad')
    #subdesign = Design.load_yaml('C:/Users/danaukes/popupCAD_files/designs/hinges/supported_hinge_half1.cad')
    design = design.upgrade()
    
    #get subdesign
    subdesign = design.subdesigns[230308440]
    
    #upgrade is unnecessary if subdesign is a child of design
    #subdesign = subdesign.upgrade()
    
    #ensure subdesign is a totally separate copy
    
    subdesign = subdesign.copy_yaml()
    
    subdesign_mapping,sketch_mapping,op_mapping = design_advanced_functions.merge_designs(design,subdesign,0)
    
    design_advanced_functions.external_to_internal_transform_outer(design,subdesign,sketch_mapping,op_mapping)
    
    #if the subdesigns subdesigns can also be found in the design, switch back to them
    #   this could cause a problem if they are different versions of the same file, so use this feature cautiously.
    for oldref, newref in subdesign_mapping:
        if oldref in design.subdesigns:
            design.replace_subdesign_refs(newref,oldref)
            design.subdesigns.pop(newref)
    
    if subdesign.id in design.subdesigns:
        design.subdesigns.pop(subdesign.id)
    
    design_out = 'C:/Users/danaukes/Dropbox/zhis sentinal 11 files/modified/sentinal 11 manufacturing_R08.cad'
    design.save_yaml(design_out)
