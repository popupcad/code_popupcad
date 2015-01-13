# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation2 import Operation2

import PySide.QtCore as qc
import PySide.QtGui as qg
import popupcad.filetypes.enum as enum
from popupcad.widgets.dragndroptree import DraggableTreeWidget,ParentItem,ChildItem

class Dialog(qg.QDialog):
    def __init__(self,keepouttypes,valuenames,defaults,operations,selectedop,show,values = None,keepouttype = None,outputref = 0):
        super(Dialog,self).__init__()
            
        self.operations = operations

        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations)
        self.le1.selectIndeces([(selectedop,outputref)])
        
        if values==None:
            values = defaults[:]

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Parent Operation'))
        layout.addWidget(self.le1)
            
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
        ref,ii= self.le1.currentRefs()[0]
        
        values = [float(valueedit.text()) for valueedit in self.valueboxes]
        return ref,values,option,ii
        
class MultiValueOperation2(Operation2):
    name = 'Multi-Value Operation'
    valuenames = ['value']
    show = ['keepout']
    defaults = [0.]

    attr_init = 'operation_link1','values','keepout_type','outputref'
    attr_init_k = tuple()
    attr_copy = 'id','customname'
    
    keepout_types = enum.enum(laser_keepout = 301,mill_keepout = 302,mill_flip_keepout = 303)
    keepout_type_default = keepout_types.laser_keepout
    
    def __init__(self,*args):
        super(MultiValueOperation2,self).__init__()
        self.id = id(self)

        self.editdata(*args)

    def editdata(self,operation_link1,values,keepout_type,outputref):
        super(MultiValueOperation2,self).editdata()
        self.operation_link1 = operation_link1
        self.values = values
        self.keepout_type = keepout_type
        self.outputref = outputref
        
    def parentrefs(self):
        return [self.operation_link1]

    def getoutputref(self):
        return self.outputref

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(cls.keepout_types,cls.valuenames,cls.defaults,design.operations,currentop,cls.show,keepouttype = cls.keepout_type_default)
        return dialog

    def buildeditdialog(self,design):
        selectedindex = design.operation_index(self.operation_link1)
        dialog = Dialog(self.keepout_types,self.valuenames,self.defaults,design.prioroperations(self),selectedindex,self.show,self.values,self.keepout_type,self.getoutputref())
        return dialog

    def upgrade(self):
        operation_links = {}
        operation_links['parent'] = [(self.operation_link1,self.outputref)]
        new = self.upgradeclass(operation_links,{},{},self.values,self.keepout_type)
        new.id = self.id
        new.customname = self.customname
        return new

    def copy(self):
        return self.upgrade()

