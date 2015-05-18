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
class OutputData(object):
    def __init__(self,ref1):
        self.ref1 = ref1
        
class InputRow(Row):
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
        self.output_table= Table(OutputRow(self.get_subdesign_operations))
        
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

        self.designwidget.itemlist.itemSelectionChanged.connect(self.input_table.reset)
        self.designwidget.itemlist.itemSelectionChanged.connect(self.output_table.reset)
    def get_operations(self):
        return self.operations
    def get_subdesign_operations(self):
        return self.subdesign().operations
#        return []
    def subdesign(self):
        try:
            return self.designwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        
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
        
        return design_links,input_list,output_list
        

class SubOperation(Operation2):
    resolution = 2
    name = 'Sub-Operation'
    def copy(self):
        new = type(self)(self.design_links.copy(),self.input_list.copy(),self.output_list.copy())
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SubOperation,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,design_links,input_list,output_list):  
        super(SubOperation,self).editdata({},{},design_links)
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

    def operate(self,design):
        subdesign = design.subdesigns[self.design_links['source']].copy(identical = False)
        subdesign.reprocessoperations()
        layerdef = design.return_layer_definition()
        return Laminate(layerdef)
