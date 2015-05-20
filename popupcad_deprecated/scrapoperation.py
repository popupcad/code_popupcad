# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.operation import Operation
from popupcad.filetypes.operationoutput import OperationOutput

import PySide.QtCore as qc
import PySide.QtGui as qg
import dev_tools.enum as enum
from popupcad.widgets.dragndroptree import DraggableTreeWidget

class Dialog(qg.QDialog):
    def __init__(self,keepouttypes,valuenames,defaults,operations,show,operationindeces  = None,values = None,keepouttype = None):
        super(Dialog,self).__init__()
            
        self.operations = operations


        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations)

        self.le3 = DraggableTreeWidget()
        self.le3.linklist(self.operations)
        if operationindeces !=None:
            self.le1.selectIndeces(operationindeces [0:1])
            self.le3.selectIndeces(operationindeces [1:2])
        
        if values==None:
            values = defaults[:]

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Sheet'))
        layout.addWidget(self.le1)
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.le3)
            
        self.valueboxes = []
        for valuename,v in zip(valuenames,values):
            templayout = qg.QHBoxLayout()
            valueedit = qg.QLineEdit()
            valueedit.setAlignment(qc.Qt.AlignRight)
            valueedit.setText(str(v))

    #        self.valueedit.setInputMask('#009.0')
            valueedit.setValidator(qg.QDoubleValidator(-999.0, 999.0, 4, valueedit))
            templayout.addStretch()
            templayout.addWidget(qg.QLabel(valuename))
            templayout.addWidget(valueedit)
            self.valueboxes.append(valueedit)
            layout.addLayout(templayout)

        self.radiobuttons = []
        if 'keepout' in show:
            for key,value2 in keepouttypes.dict.items():
                b = qg.QRadioButton(key)
                b.setChecked(keepouttype == value2)
                b.uservalue = value2
                self.radiobuttons.append(b)
                layout.addWidget(b)

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout.addLayout(layout2)

        self.setLayout(layout)    

        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)

    def acceptdata(self):
        option = None
        for b in self.radiobuttons:
            if b.isChecked():
                option = b.uservalue
        operationlinks = [self.le1.currentRefs()[0],self.le3.currentRefs()[0]]
        values = [float(valueedit.text()) for valueedit in self.valueboxes]
        return operationlinks,values,option
        
class ScrapOperation(Operation):
    name = 'Scrap Operation'
    valuenames = ['device buffer']
    show = ['keepout']
    defaults = [1.]

    keepout_types = enum.enum(laser_keepout = 301,mill_keepout = 302,mill_flip_keepout = 303)
    
    def __init__(self,*args):
        super(ScrapOperation,self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,operation_links,values,keepout_type):
        super(ScrapOperation,self).editdata()
        self.operation_links = operation_links
        self.values = values
        self.keepout_type = keepout_type

    def copy(self):
        new = type(self)(self.operation_links,self.values,self.keepout_type)
        new.customname = self.customname
        new.id = self.id
        return new
        
    def parentrefs(self):
        return [link[0] for link in self.operation_links]

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(cls.keepout_types,cls.valuenames,cls.defaults,design.operations,cls.show,keepouttype = cls.keepout_types.laser_keepout)
        return dialog

    def buildeditdialog(self,design):
        operationindeces = [[design.operation_index(l[0]),l[1]] for l in self.operation_links]
        dialog = Dialog(self.keepout_types,self.valuenames,self.defaults,design.prioroperations(self),self.show,operationindeces,self.values,self.keepout_type)
        return dialog

    def generate(self,design):
        import popupcad
        import popupcad_manufacturing_plugins.algorithms.removability as removability
        
        sheet = design.op_from_ref(self.operation_links[0][0]).output[self.operation_links[0][1]].csg
        device= design.op_from_ref(self.operation_links[1][0]).output[self.operation_links[1][1]].csg

        removable_both,removable_up,removable_down = removability.generate_removable_scrap(device,sheet,device_buffer=self.values[0]*popupcad.internal_argument_scaling)

        a = OperationOutput(removable_both,'removable_both',self)
        b = OperationOutput(removable_up,'removable_up',self)
        c = OperationOutput(removable_down ,'removable_down',self)
        self.output = [a,a,b,c]                
    
    def upgrade(self,*args,**kwargs):
        from popupcad_manufacturing_plugins.manufacturing.scrapoperation2 import ScrapOperation2
        operation_links = {'sheet':[(self.operation_links[0][0],self.operation_links[0][1])],'device':[(self.operation_links[1][0],self.operation_links[1][1])]}
        new = ScrapOperation2(operation_links,self.values,self.keepout_type)
        new.customname = self.customname
        new.id = self.id
        return new
