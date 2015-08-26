# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
import PySide.QtGui as qg
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation import Operation
from popupcad.widgets.listmanager import SketchListManager


class Dialog(qg.QDialog):

    def __init__(self, cls, design, sketch=None):
        super(Dialog, self).__init__()
        self.design = design
        self.cls = cls

        self.sketchwidget = SketchListManager(self.design)
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value == sketch:
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

        button1.clicked.connect(self.accept)
        button2.clicked.connect(self.reject)

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        sketchid = self.sketch().id
        return sketchid,


class LocateOperation2(Operation):
    name = 'Locate Operation'

    def copy(self):
        new = type(self)(self.sketchid)
        new.id = self.id
        return new

    def __init__(self, *args):
        super(LocateOperation2, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, sketchid):
        super(LocateOperation2, self).editdata()
        self.sketchid = sketchid

    def sketchrefs(self):
        return [self.sketchid]

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(cls, design)
        return dialog

    def buildeditdialog(self, design):
        sketch = design.sketches[self.sketchid]
        dialog = Dialog(self, design, sketch)
        return dialog

    def operate(self, design):
        sketch = design.sketches[self.sketchid]
        operationgeom = popupcad.algorithms.csg_shapely.unary_union_safe(
            [item.to_shapely() for item in sketch.operationgeometry])
        lsout = Laminate(design.return_layer_definition())
        for layer in design.return_layer_definition().layers:
            lsout.replacelayergeoms(
                layer,
                popupcad.algorithms.csg_shapely.condition_shapely_entities(operationgeom))
        return lsout

    def locationgeometry(self):
        return self.sketchid

    def upgrade(self, *args, **kwargs):
        from popupcad.manufacturing.locateoperation3 import LocateOperation3
        sketch_links = {'sketch': [self.sketchid]}
        new = LocateOperation3(sketch_links)
        new.id = self.id
        return new
