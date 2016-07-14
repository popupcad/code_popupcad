# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import popupcad
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.dragndroptree import DraggableTreeWidget

import qt.QtCore as qc
import qt.QtGui as qg


class Dialog(qg.QDialog):

    def __init__(
            self,
            operations,
            index,
            shift=0,
            flip=False,
            rotate=False,
            outputref=0):
        super(Dialog, self).__init__()

        self.operations = operations
        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations)
        self.le1.selectIndeces([(index, outputref)])
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
        self.sb.setRange(popupcad.gui_negative_infinity, popupcad.gui_positive_infinity)
        self.sb.setSingleStep(1)
        self.sb.setValue(shift)
        layout4.addWidget(self.sb)

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Parent Operation'))
        layout.addWidget(self.le1)
        layout.addLayout(layout5)
        layout.addLayout(layout6)
        layout.addLayout(layout4)
        layout.addLayout(layout2)

        self.setLayout(layout)

        button1.clicked.connect(self.accept)
        button2.clicked.connect(self.reject)

#        self.le1.setCurrentIndex(index)

    def acceptdata(self):
        operation_links = {'parent': [self.le1.currentRefs()[0]]}
        return operation_links, self.sb.value(
        ), self.flip.isChecked(), self.rotate.isChecked()


class ShiftFlip3(Operation2):
    name = 'Shift-Flip'

    def __init__(self, *args):
        super(ShiftFlip3, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, operation_links, shift, flip, rotate):
        super(ShiftFlip3, self).editdata(operation_links, {}, {})
        self.shift = shift
        self.flip = flip
        self.rotate = rotate

    def copy(self, *args, **kwargs):
        new = type(self)(
            self.operation_links,
            self.shift,
            self.flip,
            self.rotate)
        new.customname = self.customname
        new.id = self.id
        return new

    def f_rotate(self):
        try:
            return self.rotate
        except AttributeError:
            self.rotate = False
            return self.rotate

    @classmethod
    def buildnewdialog(cls, design, currentop):
        return Dialog(design.operations, currentop)

    def buildeditdialog(self, design):
        operation_link1, outputref = self.operation_links['parent'][0]
        selectedindex = design.operation_index(operation_link1)
        return Dialog(
            design.prioroperations(self),
            selectedindex,
            self.shift,
            self.flip,
            self.f_rotate(),
            outputref)

    def operate(self, design):
        operation_link1, outputref = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_link1).output[outputref].csg
        return popupcad.algorithms.manufacturing_functions.shift_flip_rotate(
            ls1,
            self.shift,
            self.flip,
            self.rotate)
