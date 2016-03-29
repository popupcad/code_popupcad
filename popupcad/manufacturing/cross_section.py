# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


import qt.QtCore as qc
import qt.QtGui as qg
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.listmanager import SketchListManager
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.filetypes.design import NoOperation
import popupcad


class Dialog(qg.QDialog):

    def __init__(self, design, operations, operation_index, sketch=None):
        super(Dialog, self).__init__()
        SketchListManager(design)
        self.optree = DraggableTreeWidget()
        self.optree.linklist(operations)
        self.sketchwidget = SketchListManager(design)

        button1 = qg.QPushButton('Ok')
        button1.clicked.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.clicked.connect(self.reject)
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.optree)
        layout.addWidget(self.sketchwidget)
        layout.addLayout(layout2)

        self.setLayout(layout)

        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value == sketch:
                item.setSelected(True)

        try:
            self.optree.selectIndeces([operation_index])
        except NoOperation:
            pass

    def acceptdata(self):
        operation_links = {}
        operation_links['source'] = [self.optree.currentRefs()[0]]

        sketch_links = {}
        try:
            sketch_links['cross_section'] = [
                self.sketchwidget.itemlist.selectedItems()[0].value.id]
        except IndexError:
            pass

        return operation_links, sketch_links, 100


class CrossSection(Operation2):
    name = 'Cross-Section'

    def __init__(self, *args, **kwargs):
        super(CrossSection, self).__init__()
        self.id = id(self)
        self.editdata(*args, **kwargs)

    def copy(self):
        new = type(self)(
            self.operation_links,
            self.sketch_links,
            self.scale_value)
        new.id = self.id
        new.customname = self.customname
        return new

    def editdata(self, operation_links, sketch_links, scale_value):
        super(CrossSection, self).editdata(operation_links, sketch_links, {})
        self.scale_value = scale_value

    def operate(self, design):
        parent_ref, parent_index = self.operation_links['source'][0]
        parent = design.op_from_ref(parent_ref).output[parent_index].csg
        sketch = design.sketches[self.sketch_links['cross_section'][0]]
        layerdef = design.return_layer_definition()
        return popupcad.algorithms.manufacturing_functions.cross_section(
            layerdef,
            sketch,
            parent,
            self.scale_value)

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(design, design.operations, (currentop, 0))
        return dialog

    def buildeditdialog(self, design):
        op_ref, output_index = self.operation_links['source'][0]
        try:
            op_index = design.operation_index(op_ref)
        except NoOperation:
            op_index = None

        sketch = design.sketches[self.sketch_links['cross_section'][0]]
        dialog = Dialog(
            design,
            design.prioroperations(self),
            (op_index,
             output_index),
            sketch)
        return dialog
