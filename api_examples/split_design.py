# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 17:13:42 2015

@author: danaukes
"""
#import popupcad
from popupcad.filetypes.design import Design
from popupcad.manufacturing.sub_operation2 import SketchData,InputData,OutputData,SubOperation2
from popupcad.manufacturing.freeze import Freeze

#import design_advanced_functions

#import sys
#import PySide.QtGui as qg
#app = qg.QApplication(sys.argv[0])

def add_frozen_inputs(subdesign,design):
    parent_links = []
    for op in subdesign.operations:
        for key in op.operation_links:
            parent_links.extend(op.operation_links[key])
    parent_links = list(set(parent_links))
    inner_inputs = [link for link in parent_links if link[0] not in [op.id for op in subdesign.operations]]
    
    frozen_operations = []    
    
    for parent_id,parent_output_ii in inner_inputs:
            generic_laminate = design.operation_dict[parent_id].output[parent_output_ii].csg.to_generic_laminate()
            frozen = Freeze(parent_id,parent_output_ii,generic_laminate)
            frozen_operations.append(frozen)
            
            subdesign.replace_op_refs_force((parent_id,parent_output_ii),(frozen.id,0))
            subdesign.operations.insert(0,frozen)
    
    return inner_inputs,frozen_operations

def create_subdesign(design,indices):
    inner_operation_indices = sorted(indices)
    inner_operations = [design.operations[ii] for ii in inner_operation_indices]

    subdesign = design.copy_yaml(identical=False)
    subdesign.operations = [subdesign.operations[ii] for ii in inner_operation_indices]
    
    inner_inputs,frozen_operations =add_frozen_inputs(subdesign,design)
    #after creating new frozen operations, cleanup the subdesign
    subdesign.cleanup_sketches()
    subdesign.cleanup_subdesigns() 
    
    input_list = build_input_list(inner_inputs,frozen_operations)    
    
    return subdesign,input_list,inner_operations

def remove_redundant_ops(design,subdesign):
    design_refs = [op.id for op in design.operations]
    subdesign_refs = [op.id for op in subdesign.operations]
    
    to_remove = list(set(design_refs).intersection(set(subdesign_refs)))    
    
    for ref in to_remove:
        design.operations.remove(design.operation_dict[ref])

def build_sketch_list(subdesign):
    sketch_list = []
    for key,value in subdesign.sketches.items():
        sketch_list.append(SketchData(key,key))
    return sketch_list
    
def build_input_list(inner_inputs,frozen_operations):
    input_list = []
    for input_link,frozen_op in zip(inner_inputs,frozen_operations):
        input_list.append(InputData((frozen_op.id,0),input_link,0))
    return input_list    
    
def build_output_list(inner_operations):
    children = set([item for op in inner_operations for item in op.children()])
    required_outputs = []
    for op in children:
        for key in op.operation_links:
            required_outputs.extend(op.operation_links[key])
    
    required_outputs = list(set(required_outputs))
    
    output_list = []    

    inner_operation_ids = [op.id for op in inner_operations]
    required_outputs2 = []
    for link in required_outputs:
        if link[0] in inner_operation_ids:
            required_outputs2.append(link)
            output_list.append(OutputData(link,0))    
    return required_outputs2,output_list
    
design = Design.load_yaml('C:/Users/danaukes/desktop/test5.cad')
design = design.upgrade()
design.reprocessoperations()
t = design.build_tree()

#ops = design.operations[2:4]
inner_operation_indices = [3,4]

subdesign,input_list,inner_operations= create_subdesign(design,inner_operation_indices)
remove_redundant_ops(design,subdesign)

#build information required to build subop
sketch_list = build_sketch_list(subdesign)
design_links =  {'source':[subdesign.id]}

required_outputs,output_list = build_output_list(inner_operations)

subop = SubOperation2(design_links,sketch_list,input_list,output_list)

subdesign.save_yaml('C:/Users/danaukes/desktop/test6.cad')

for ii,link in enumerate(required_outputs):
    design.replace_op_refs_force(link, (subop.id,ii))


design.operations.insert(3,subop)
design.subdesigns[subdesign.id] = subdesign

design.save_yaml('C:/Users/danaukes/desktop/test7.cad')
