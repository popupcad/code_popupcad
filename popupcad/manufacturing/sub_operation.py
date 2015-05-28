# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 14:41:02 2014

@author: danaukes
"""
from popupcad.widgets.dragndroptree import DraggableTreeWidget

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.filetypes.operation2 import Operation2
from popupcad.filetypes.laminate import Laminate
from popupcad.widgets.table_editor import Table,SingleItemListElement,Row,TableControl
from  popupcad.widgets.listmanager import SketchListManager,DesignListManager

def get_sketches(parent):
    return parent.parent().parent().sketches

def get_layers(parent):
    return parent.parent().parent().layers

class InputData(object):
    def __init__(self,ref1,ref2):
        self.ref1 = ref1
        self.ref2 = ref2

class SketchData(object):
    def __init__(self,ref1,ref2):
        self.ref1 = ref1
        self.ref2 = ref2

class OutputData(object):
    def __init__(self,ref1):
        self.ref1 = ref1
        
class InputRow(Row):
    def __init__(self,get_sketches,get_layers):
        elements = []
        elements.append(SingleItemListElement('to replace',get_sketches))
        elements.append(SingleItemListElement('replace with',get_layers))
        self.elements = elements

class SketchRow(Row):
    def __init__(self,get_sketches,get_layers):
        elements = []
        elements.append(SingleItemListElement('to replace',get_sketches))
        elements.append(SingleItemListElement('replace with',get_layers))
        self.elements = elements

class OutputRow(Row):
    def __init__(self,get_sketches):
        elements = []
        elements.append(SingleItemListElement('output',get_sketches))
        self.elements = elements
        
class JointDef(object):
    def __init__(self,sketch,joint_layer,sublaminate_layers,width,stiffness,damping,preload_angle):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width
        self.stiffness = stiffness
        self.damping = damping
        self.preload_angle = preload_angle

class MainWidget(qg.QDialog):
    def __init__(self,design,sketches,layers,operations,jointop=None):
        super(MainWidget,self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations
        
        self.designwidget = DesignListManager(design)

        self.input_table= Table(InputRow(self.get_subdesign_operations,self.get_operations))
        self.sketch_table= Table(SketchRow(self.get_subdesign_sketches,self.get_sketches))
        self.output_table= Table(OutputRow(self.get_subdesign_operations))
        
        self.sketch_control = TableControl(self.sketch_table,self)
        self.input_control = TableControl(self.input_table,self)
        self.output_control = TableControl(self.output_table,self)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.pressed.connect(self.accept)        
        button_cancel.pressed.connect(self.reject)        

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.designwidget)
        layout.addWidget(self.sketch_control)
        layout.addWidget(self.input_control)
        layout.addWidget(self.output_control)
        layout.addLayout(sublayout2)
        self.setLayout(layout)

        if jointop!=None:
            subdesign = design.subdesigns[jointop.design_links['source']]
            for ii in range(self.designwidget.itemlist.count()):
                item = self.designwidget.itemlist.item(ii)
                if item.value==subdesign:
                    item.setSelected(True)
            for item in jointop.input_list:
                self.input_table.row_add(subdesign.op_from_ref(item.ref1[0]),design.op_from_ref(item.ref2[0]))
            for item in jointop.output_list:
                self.output_table.row_add(subdesign.op_from_ref(item.ref1[0]))
            for item in jointop.sketch_list:
                self.sketch_table.row_add(subdesign.sketches[item.ref1],design.sketches[item.ref2])

        self.designwidget.itemlist.itemSelectionChanged.connect(self.input_table.reset)
        self.designwidget.itemlist.itemSelectionChanged.connect(self.output_table.reset)
    def get_operations(self):
        return self.operations
    def get_subdesign_operations(self):
        return self.subdesign().operations
    def get_sketches(self):
        return self.design.sketches.values()
    def get_subdesign_sketches(self):
        return self.subdesign().sketches.values()
#        return []
    def subdesign(self):
        try:
            return self.designwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        
        sketch_list = []
        data = self.sketch_table.export_data()
        for sketch1,sketch2 in data:
            sketch_list.append(SketchData(sketch1.id,sketch2.id))

        input_list = []
        data = self.input_table.export_data()
        for op1,op2 in data:
            input_list.append(InputData((op1.id,0),(op2.id,0)))

        output_list= []
        data = self.output_table.export_data()
        for op1, in data:
            output_list.append(OutputData((op1.id,0)))
            
        design_links = {}
        design_links['source'] = self.subdesign().id
        
        return design_links,sketch_list,input_list,output_list
        

class SubOperation(Operation2):
    resolution = 2
    name = 'Sub-Operation'
    def copy(self):
        new = type(self)(self.design_links.copy(),self.sketch_list.copy(),self.input_list.copy(),self.output_list.copy())
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SubOperation,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,design_links,sketch_list,input_list,output_list):  
        super(SubOperation,self).editdata({},{},design_links)
        self.sketch_list = sketch_list
        self.design_links = design_links
        self.input_list = input_list
        self.output_list = output_list

    def replace_op_refs(self,refold,refnew):
        for item in self.input_list:
            if item.ref2 ==refold:
                item.ref2 = refnew
        self.clear_output()

    def parentrefs(self):
        return [item.ref2[0] for item in self.input_list]

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.prioroperations(self),self)
        return dialog

    def generate(self,design):
        subdesign_orig = design.subdesigns[self.design_links['source']]
        subdesign = subdesign_orig.copy_yaml()
        
        layerdef_old = subdesign.return_layer_definition()
        layerdef_new = design.return_layer_definition()
        new_operations = []
        for operation in subdesign.operations:
            try:
                operation = operation.switch_layer_defs(layerdef_old,layerdef_new)
            except AttributeError:
                pass
            new_operations.append(operation)
        subdesign.sketches.update(design.sketches)
        subdesign.operations = new_operations
        for input_data in self.input_list:
            from_ref = input_data.ref1
            to_ref = input_data.ref2
            op_to_insert = design.op_from_ref(to_ref[0])
            subdesign.operations.insert(0,op_to_insert)
            subdesign.replace_op_refs_force(from_ref,to_ref)
        for sketch_data in self.sketch_list:
            from_ref = sketch_data.ref1
            to_ref = sketch_data.ref2
            subdesign.replace_sketch_refs_force(from_ref,to_ref)
            
        subdesign.define_layers(layerdef_new)
        subdesign.reprocessoperations()
        self.output = []
        for output_data in self.output_list:
            self.output.extend(subdesign.op_from_ref(output_data.ref1[0]).output)
