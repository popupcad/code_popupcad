# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.listmanager import SketchListManager
import popupcad
from popupcad.widgets.dragndroptree import DraggableTreeWidget

class Dialog(qg.QDialog):

    def __init__(self, cls, design, selectedop,outputref=0):
        super(Dialog, self).__init__()
        
        self.design = design
        self.cls = cls

        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations)
        self.le1.selectIndeces([(selectedop, outputref)])
        
        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')
        buttonlayout = qg.QHBoxLayout()
        buttonlayout.addWidget(button1)
        buttonlayout.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.le1)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)

        button1.clicked.connect(self.accept)
        button2.clicked.connect(self.reject)

    def acceptdata(self):
        ref, ii = self.le1.currentRefs()[0]
        operation_links = {}
        operation_links['parent'] = [(ref, ii)]
        return operation_links


class Hollow(Operation2):
    name = 'Hollow'

    def copy(self):
        new = type(self)(self.operation_links.copy())
        new.id = self.id
        return new

    def __init__(self, *args):
        super(Hollow, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, operation_links):
        super(Hollow, self).editdata(operation_links, {}, {})

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(cls.keepout_types,cls.valuenames,cls.defaults,
            design.operations,currentop,cls.show,
            keepouttype=cls.keepout_type_default)
        return dialog

    def buildeditdialog(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        operation_index = design.operation_index(operation_ref)
        dialog = Dialog(self.keepout_types,self.valuenames,self.defaults,
            design.prioroperations(self),operation_index,self.show,self.values,
            self.keepout_type,output_index)
        return dialog

    def operate(self, design):
        sketchid = self.sketch_links['sketch'][0]
        sketch = design.sketches[sketchid]
        operationgeom = popupcad.algorithms.csg_shapely.unary_union_safe(
            [item.to_shapely() for item in sketch.operationgeometry])
        lsout = Laminate(design.return_layer_definition())
        for layer in design.return_layer_definition().layers:
            lsout.replacelayergeoms(
                layer,
                popupcad.algorithms.csg_shapely.condition_shapely_entities(operationgeom))
        return lsout

    def locationgeometry(self):
        sketchid = self.sketch_links['sketch'][0]
        return sketchid
