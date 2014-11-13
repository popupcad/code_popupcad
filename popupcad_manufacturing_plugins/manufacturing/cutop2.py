# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.operationoutput import OperationOutput

import PySide.QtCore as qc
import PySide.QtGui as qg
import popupcad.filetypes.enum as enum
from popupcad.widgets.dragndroptree import DraggableTreeWidget,ParentItem,ChildItem

class Dialog(qg.QDialog):
    def __init__(self,keepouttypes,valuenames,defaults,operations,show,operationindeces  = None,values = None,keepouttype = None):
        super(Dialog,self).__init__()
            
        self.operations = operations


        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations)

        self.le2 = DraggableTreeWidget()
        self.le2.linklist(self.operations)

        self.le3 = DraggableTreeWidget()
        self.le3.linklist(self.operations)
        if operationindeces !=None:
            self.le1.selectIndeces(operationindeces [0:1])
            self.le2.selectIndeces(operationindeces [1:2])
            self.le3.selectIndeces(operationindeces [2:3])
        
        if values==None:
            values = defaults[:]

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Sheet'))
        layout.addWidget(self.le1)
        layout.addWidget(qg.QLabel('Supported Device'))
        layout.addWidget(self.le2)
        layout.addWidget(qg.QLabel('Final Device'))
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

    def sizeHint(self):
        return qc.QSize(400,800)

    def acceptdata(self):
        option = None
        for b in self.radiobuttons:
            if b.isChecked():
                option = b.uservalue
        operationlinks = [self.le1.currentRefs()[0],self.le2.currentRefs()[0],self.le3.currentRefs()[0]]
        values = [float(valueedit.text()) for valueedit in self.valueboxes]
        return operationlinks,values,option
        
class CutOperation2(Operation):
    name = 'Cut Op'
    valuenames = []
    show = ['keepout']
    defaults = []

    attr_init = 'operation_links','values','keepout_type'
    attr_init_k = tuple()
    attr_copy = 'id','customname'
    
    keepout_types = enum.enum(laser_keepout = 301,mill_keepout = 302,mill_flip_keepout = 303)
    
    def __init__(self,*args):
        super(CutOperation2,self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,operation_links,values,keepout_type):
        super(CutOperation2,self).editdata()
        self.operation_links = operation_links
        self.values = values
        self.keepout_type = keepout_type
        
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
        
        sheet = design.op_from_ref(self.operation_links[0][0]).output[self.operation_links[0][1]].csg
        supported_device= design.op_from_ref(self.operation_links[1][0]).output[self.operation_links[1][1]].csg
        device= design.op_from_ref(self.operation_links[2][0]).output[self.operation_links[2][1]].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            keepout = popupcad.algorithms.keepout.laserkeepout(supported_device)
            keepout2 = popupcad.algorithms.keepout.laserkeepout(device)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            keepout = popupcad.algorithms.keepout.millkeepout(supported_device)
            keepout2 = popupcad.algorithms.keepout.laserkeepout(device)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            keepout = popupcad.algorithms.keepout.millflipkeepout(supported_device)
            keepout2 = popupcad.algorithms.keepout.laserkeepout(device)

        firstpass = sheet.difference(keepout.difference(supported_device))
        secondpass = sheet.difference(keepout2)
        laminate = Laminate(design.return_layer_definition())
        device2= firstpass.difference(secondpass)
        error = device2.symmetric_difference(device)
        error = error.buffer(-.001)

        a = OperationOutput(firstpass,'first pass',self)
        b = OperationOutput(secondpass,'second pass',self)
        c = OperationOutput(error ,'error',self)
        self.output = [a,a,b,c]
                
    
