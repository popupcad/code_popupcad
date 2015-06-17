# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation2 import Operation2

import PySide.QtGui as qg
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.filetypes.design import NoOperation

class Dialog(qg.QDialog):
    def __init__(self,design,operations,selectedop=None,outputref = 0):
        super(Dialog,self).__init__()
            
            
        self.design = design
        
        self.le1 = DraggableTreeWidget()
        self.le1.linklist(operations)
        if selectedop!=None:
            self.le1.selectIndeces([(selectedop,outputref)])
        
        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Operation to Flatten'))
        layout.addWidget(self.le1)
            
        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout.addLayout(layout2)

        self.setLayout(layout)    

        button1.clicked.connect(self.accept)
        button2.clicked.connect(self.reject)
        
    def acceptdata(self):
        ref,ii= self.le1.currentRefs()[0]
        generic = self.design.op_from_ref(ref).output[ii].generic_laminate()
        return ref,ii,generic
        
class Freeze(Operation2):
    name = 'Freeze'
    def __init__(self,*args):
        super(Freeze,self).__init__()
        self.id = id(self)
        self.editdata(*args)

    def editdata(self,operation_link1,outputref,generic):
        super(Freeze,self).editdata()
        self.operation_link1 = operation_link1
        self.generic = generic
        self.outputref = outputref
        
    def copy(self):
        new = type(self)(self.operation_link1,self.outputref,self.generic)
        new.id = self.id
        new.customname = self.customname
        return new

    def getoutputref(self):
        return self.outputref

    def operate(self,design):
        layerdef = design.return_layer_definition()
        csg = Laminate(layerdef)
        for layer in layerdef.layers:
            shapelygeoms = [geom.outputshapely() for geom in self.generic.geoms[layer]] 
            csg.insertlayergeoms(layer,shapelygeoms)
        return csg

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(design,design.operations,currentop)
        return dialog

    def buildeditdialog(self,design):
        try:
            selectedindex = design.operation_index(self.operation_link1)
        except NoOperation:
            selectedindex = None
        operations = design.prioroperations(self)
        dialog = Dialog(design,operations,selectedindex,outputref = self.getoutputref())
        return dialog

