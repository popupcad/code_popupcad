# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 17:13:42 2015

@author: danaukes
"""
#import sys
#import PySide.QtGui as qg
#app = qg.QApplication(sys.argv[0])

import popupcad
import popupcad.manufacturing.sub_operation2 as sub_operation

#from popupcad.manufacturing.dummy_operation1 import DummyOp1

from popupcad.filetypes.design import Design
design = Design.load_yaml('C:/Users/danaukes/desktop/test5.cad')
design = design.upgrade()
design.reprocessoperations()
t = design.build_tree()

#ops = design.operations[2:4]
op_ii = [3,4]
ops = [design.operations[ii] for ii in op_ii]
op_ids = [item.id for item in ops]

parents = set([item for op in ops for item in op.parents()])
inputs = parents-set(ops)
input_ids = [item.id for item in inputs]

children = set([item for op in ops for item in op.children()])
outputs = children-set(ops)


parents_ii = [design.operations.index(parent) for parent in parents]
op_ii = sorted(set(op_ii+parents_ii))

subdesign = design.copy_yaml(identical=False)
subdesign.operations = [subdesign.operations[ii] for ii in op_ii]
subdesign.cleanup_sketches()

design_links =  {'source':[subdesign.id]}

sketch_list = []
for key,value in subdesign.sketches.items():
    sketch_list.append(sub_operation.SketchData(key,key))

parent_links = []
for op in ops:
    for key in op.operation_links:
        parent_links.extend(op.operation_links[key])
        
parent_links = list(set(parent_links))

input_list = []    
for link in parent_links:
    if link[0] in input_ids:
        input_list.append(sub_operation.InputData(link,link,0))

required_outputs = []
for op in children:
    for key in op.operation_links:
        required_outputs.extend(op.operation_links[key])

required_outputs = list(set(required_outputs))

output_list = []    
for link in required_outputs:
    if link[0] in op_ids:
        output_list.append(sub_operation.OutputData(link,0))

subop = sub_operation.SubOperation2(design_links,sketch_list,input_list,output_list)
filename = 'C:/Users/danaukes/desktop/test6.cad'
subdesign.save_yaml(filename)
