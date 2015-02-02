# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtGui as qg
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.listmanager import SketchListManager
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.filetypes.laminate import Laminate

class Dialog(qg.QDialog):
    def __init__(self,design,operations):
        super(Dialog,self).__init__()
        SketchListManager(design)
        self.optree = DraggableTreeWidget()
        self.optree.linklist(operations)
        self.sketchwidget = SketchListManager(design)

        button1 = qg.QPushButton('Ok')
        button1.pressed.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.pressed.connect(self.reject)
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)


        layout=qg.QVBoxLayout()
        layout.addWidget(self.optree)        
        layout.addWidget(self.sketchwidget)        
        layout.addLayout(layout2)

        self.setLayout(layout)

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        operation_links = {}
        operation_links['source'] = [self.optree.currentRefs()[0]]
        

        sketch_links= {}
        try:
            sketch_links['cross_section'] = [self.sketchwidget.itemlist.selectedItems()[0].value.id]
        except IndexError:
            pass
        
        return operation_links,sketch_links

class CrossSection(Operation2):
    name='Cross-Section'
    def __init__(self,*args,**kwargs):
        super(CrossSection,self).__init__()
        self.id = id(self)
        self.editdata(*args,**kwargs)

    def copy(self,identical = True):
        new = type(self)(self.operation_links,self.sketch_links)
        if identical:        
            new.id = self.id
        new.customname = self.customname
        return new

    def editdata(self,operation_links,sketch_links):
        super(CrossSection,self).editdata(operation_links,sketch_links,{})

    def operate(self,design):
        parent_ref,parent_index  = self.operation_links['source'][0]
        parent = design.op_from_ref(parent_ref).output[parent_index].csg
        
        sketch = design.sketches[self.sketch_links['cross_section'][0]]
        sketch_csg = sketch.output_csg()
        
        layerdef = design.return_layer_definition()
        laminate = Laminate(layerdef)
        for layer in layerdef.layers:
            laminate.replacelayergeoms(layer,sketch_csg)
        
        return parent.intersection(laminate)

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(design,design.operations)
        return dialog
    def buildeditdialog(self,design):
#        sketch = design.sketches[self.sketch_links['place'][0]]
#        subdesign = design.subdesigns[self.design_links['subdesign'][0]]
        dialog = Dialog(design,design.prioroperations(self))
        return dialog
