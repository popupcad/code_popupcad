# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 14:41:02 2014

@author: danaukes
"""
from popupcad.widgets.dragndroptree import DraggableTreeWidget

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.genericlaminate import GenericLaminate
from popupcad.filetypes.operation2 import Operation2
import popupcad
from popupcad.filetypes.laminate import Laminate
import popupcad_manufacturing_plugins
from popupcad.widgets.table_editor import Table,SingleItemListElement,MultiItemListElement,FloatElement,Row

def get_sketches(parent):
    return parent.parent().parent().sketches

def get_layers(parent):
    return parent.parent().parent().layers

class JointRow(Row):
    column_count = 7
    elements = []
    elements.append(SingleItemListElement('joint sketch',get_sketches))
    elements.append(SingleItemListElement('joint layer',get_layers))
    elements.append(MultiItemListElement('sublaminate layers',get_layers))
    elements.append(FloatElement('hinge width'))
    elements.append(FloatElement('stiffness'))
    elements.append(FloatElement('damping'))
    elements.append(FloatElement('preload'))

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
        
        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.fixed = DraggableTreeWidget()
        self.fixed.linklist(self.operations)
        
        self.table= Table(JointRow)

        button_add = qg.QPushButton('Add')
        button_remove = qg.QPushButton('Remove')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.pressed.connect(self.table.row_add_empty)
        button_remove.pressed.connect(self.table.row_remove)
        button_up.pressed.connect(self.table.row_shift_up)
        button_down.pressed.connect(self.table.row_shift_down)

        sublayout1 = qg.QHBoxLayout()
        sublayout1.addWidget(button_add)
        sublayout1.addWidget(button_remove)
        sublayout1.addStretch()
        sublayout1.addWidget(button_up)
        sublayout1.addWidget(button_down)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.pressed.connect(self.accept)        
        button_cancel.pressed.connect(self.reject)        

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.operation_list)
        layout.addWidget(qg.QLabel('Fixed Region'))
        layout.addWidget(self.fixed)
        layout.addWidget(self.table)
        layout.addLayout(sublayout1)
        layout.addLayout(sublayout2)
        self.setLayout(layout)

        if jointop!=None:
            try:
                op_ref,output_ii = jointop.operation_links['parent'][0]
                op_ii = design.operation_index(op_ref)
                self.operation_list.selectIndeces([(op_ii,output_ii)])
            except(IndexError,KeyError):
                pass

            try:
                fixed_ref,fixed_output_ii = jointop.operation_links['fixed'][0]
                fixed_ii = design.operation_index(fixed_ref)
                self.fixed.selectIndeces([(fixed_ii,fixed_output_ii)])
            except(IndexError,KeyError):
                pass

            for item in jointop.joint_defs:
                sketch = self.design.sketches[item.sketch]
                joint_layer = self.design.return_layer_definition().getlayer(item.joint_layer)
                sublaminate_layers = [self.design.return_layer_definition().getlayer(item2) for item2 in item.sublaminate_layers]
                self.table.row_add(sketch,joint_layer,sublaminate_layers,item.width,item.stiffness,item.damping,item.preload_angle)
        else:
            self.table.row_add_empty()
            
    def acceptdata(self):
        jointdefs = []
        for ii in range(self.table.rowCount()):
            sketch = self.table.item(ii,0).data(qc.Qt.ItemDataRole.UserRole)
            joint_layer = self.table.item(ii,1).data(qc.Qt.ItemDataRole.UserRole)
            sublaminate_layers = self.table.item(ii,2).data(qc.Qt.ItemDataRole.UserRole)
            width = (self.table.item(ii,3).data(qc.Qt.ItemDataRole.UserRole))
            stiffness = (self.table.item(ii,4).data(qc.Qt.ItemDataRole.UserRole))
            damping = (self.table.item(ii,5).data(qc.Qt.ItemDataRole.UserRole))
            preload_angle = (self.table.item(ii,6).data(qc.Qt.ItemDataRole.UserRole))
            jointdefs.append(JointDef(sketch.id,joint_layer.id,[item.id for item in sublaminate_layers],width,stiffness,damping,preload_angle))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        operation_links['fixed'] = self.fixed.currentRefs()
        return operation_links,jointdefs
        

class SubOperation(Operation2):
    resolution = 2
    name = 'Sub-Operation'
    def copy(self):
        new = type(self)(self.operation_links,self.joint_defs)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SubOperation,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,operation_links,joint_defs):  
        self.operation_links = operation_links
        self.joint_defs = joint_defs
        self.clear_output()

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.prioroperations(self),self)
        return dialog

    def operate(self,design):
        layerdef = design.return_layer_definition()
        return Laminate(layerdef)
