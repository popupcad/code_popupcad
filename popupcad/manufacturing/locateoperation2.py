# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
import shapely.ops as ops
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.sketch import Sketch
import popupcad.widgets
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.design import NoOperation
import popupcad.geometry.customshapely as customshapely
import popupcad.widgets.listmanager as listmanager
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.manufacturing.nulloperation import NullOp


class Dialog(qg.QDialog):
    def __init__(self,cls,design,sketch = None):
        super(Dialog,self).__init__()
        self.design = design
        self.cls = cls

        self.sketchwidget = listmanager.build_sketchlist(self.design)
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value==sketch:
                item.setSelected(True)
        
        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')
        buttonlayout = qg.QHBoxLayout()
        buttonlayout.addWidget(button1)
        buttonlayout.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.sketchwidget)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)        

        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        sketchid =  self.sketch().id
        return sketchid,

class LocateOperation2(Operation):
    name = 'Locate Operation'

    def copy(self):
        new = type(self)(self.sketchid)
        new.id = self.id
        return new

    def __init__(self,*args):
        super(LocateOperation2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,sketchid):        
        super(LocateOperation2,self).editdata()
        self.sketchid = sketchid

    def sketchrefs(self):
        return [self.sketchid]

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(cls,design)
        return dialog
        
    def buildeditdialog(self,design):
        sketch = design.sketches[self.sketchid]
        dialog = Dialog(self,design,sketch)
        return dialog

    def operate(self,design):
        sketch = design.sketches[self.sketchid]
        operationgeom = customshapely.unary_union_safe([item.outputshapely() for item in sketch.operationgeometry])
        lsout = Laminate(design.return_layer_definition())
        for layer in design.return_layer_definition().layers:
            lsout.replacelayergeoms(layer,customshapely.multiinit(operationgeom))
        return lsout

    def locationgeometry(self):
        return self.sketchid
