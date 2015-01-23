# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation2 import Operation2
import popupcad.geometry.customshapely as customshapely
from popupcad.widgets.listmanager import SketchListManager

class Dialog(qg.QDialog):
    def __init__(self,cls,design,sketch = None):
        super(Dialog,self).__init__()
        self.design = design
        self.cls = cls

        self.sketchwidget = SketchListManager(self.design)
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
        sketch_links = {'sketch':[self.sketch().id]}
        return sketch_links,

class LocateOperation3(Operation2):
    name = 'Locate Operation'

    def copy(self):
        new = type(self)(self.sketch_links)
        new.id = self.id
        return new

    def __init__(self,*args):
        super(LocateOperation3,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,sketch_links):        
        super(LocateOperation3,self).editdata({},sketch_links,{})

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(cls,design)
        return dialog
        
    def buildeditdialog(self,design):
        sketchid = self.sketch_links['sketch'][0]
        sketch = design.sketches[sketchid]
        dialog = Dialog(self,design,sketch)
        return dialog

    def operate(self,design):
        sketchid = self.sketch_links['sketch'][0]
        sketch = design.sketches[sketchid]
        operationgeom = customshapely.unary_union_safe([item.outputshapely() for item in sketch.operationgeometry])
        lsout = Laminate(design.return_layer_definition())
        for layer in design.return_layer_definition().layers:
            lsout.replacelayergeoms(layer,customshapely.multiinit(operationgeom))
        return lsout

    def locationgeometry(self):
        sketchid = self.sketch_links['sketch'][0]
        return sketchid

