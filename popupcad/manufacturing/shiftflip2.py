# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.materials.laminatesheet import Laminate
from popupcad.filetypes.operation import Operation
from popupcad.widgets.dragndroptree import DraggableTreeWidget
#import PySide.QtCore as qc
import PySide.QtGui as qg

class Dialog(qg.QDialog):
    def __init__(self,operations,index,shift=0,flip=False,rotate = False,outputref = 0):
        super(Dialog,self).__init__()

        self.operations = operations
        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations) 
        self.le1.selectIndeces([(index,outputref)])
#        self.le1.addItems([str(op) for op in operations])
        

        layout5 = qg.QHBoxLayout()
        layout5.addWidget(qg.QLabel('Flip Layers'))
        self.flip = qg.QCheckBox()
        self.flip.setChecked(flip)
        layout5.addWidget(self.flip)

        layout6 = qg.QHBoxLayout()
        layout6.addWidget(qg.QLabel('Rotate Layers'))
        self.rotate = qg.QCheckBox()
        self.rotate.setChecked(rotate)
        layout6.addWidget(self.rotate)

        layout4 = qg.QHBoxLayout()
        layout4.addWidget(qg.QLabel('Shift Layers'))
        self.sb = qg.QSpinBox()
        self.sb.setRange(-100,100)
        self.sb.setSingleStep(1)
        self.sb.setValue(shift)
        layout4.addWidget(self.sb)

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)
        
        layout = qg.QVBoxLayout()
        layout.addWidget(self.le1)
        layout.addLayout(layout5)
        layout.addLayout(layout6)
        layout.addLayout(layout4)
        layout.addLayout(layout2)

        self.setLayout(layout)    

        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)
        
#        self.le1.setCurrentIndex(index)

    def acceptdata(self):
#        ii = self.le1.currentIndex()
        ref,ii = self.le1.currentRefs()[0]
        return ref,self.sb.value(),self.flip.isChecked(),self.rotate.isChecked(),ii

class ShiftFlip2(Operation):
    name = 'Shift/Flip'

    attr_init = 'operation_link1','shift','flip','rotate','outputref'
    attr_init_k = tuple()
    attr_copy = 'id','customname'
    
    def __init__(self,*args):
        super(ShiftFlip2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,operation_link1,shift,flip,rotate,outputref):
        super(ShiftFlip2,self).editdata()
        self.operation_link1 = operation_link1
        self.shift = shift
        self.flip = flip
        self.rotate = rotate
        self.outputref = outputref

    def f_rotate(self):
        try:
            return self.rotate
        except AttributeError:
            self.rotate = False
            return self.rotate
    
    def parentrefs(self):
        return [self.operation_link1]

    @classmethod
    def buildnewdialog(cls,design,currentop):
        return Dialog(design.operations,currentop)

    def buildeditdialog(self,design):
        selectedindex = design.operation_index(self.operation_link1)
        return Dialog(design.prioroperations(self),selectedindex,self.shift,self.flip,self.f_rotate(),self.outputref)

    def operate(self,design):
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        lsout = Laminate(ls1.layerdef)
        layers = ls1.layerdef.layers
        step = 1

        if self.flip:
            step=-1

        if self.rotate:
            for layerout,layerin in zip(layers[self.shift:]+layers[:self.shift],layers[::step]):
                lsout.replacelayergeoms(layerout,ls1.layer_sequence[layerin].geoms)

        else:
            if self.shift > 0:
                outshift = self.shift
                inshift = 0
            elif self.shift <0:
                outshift = 0
                inshift = -self.shift
            else:
                outshift = 0
                inshift = 0
            for layerout,layerin in zip(layers[outshift:],layers[::step][inshift:]):
                lsout.replacelayergeoms(layerout,ls1.layer_sequence[layerin].geoms)
        return lsout
