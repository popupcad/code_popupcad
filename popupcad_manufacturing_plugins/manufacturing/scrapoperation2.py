# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

from popupcad.filetypes.operation2 import Operation2
from popupcad.filetypes.operationoutput import OperationOutput


import qt.QtCore as qc
import qt.QtGui as qg
import dev_tools.enum as enum
from popupcad.widgets.dragndroptree import DraggableTreeWidget
import popupcad
from popupcad.filetypes.validators import StrictDoubleValidator
class Dialog(qg.QDialog):

    def __init__(
            self,
            keepouttypes,
            valuenames,
            defaults,
            operations,
            show,
            operationindeces=None,
            values=None,
            keepouttype=None):
        super(Dialog, self).__init__()

        self.operations = operations

        self.le1 = DraggableTreeWidget()
        self.le1.linklist(self.operations)

        self.le3 = DraggableTreeWidget()
        self.le3.linklist(self.operations)
        if operationindeces is not None:
            self.le1.selectIndeces(operationindeces[0:1])
            self.le3.selectIndeces(operationindeces[1:2])

        if values is None:
            values = defaults[:]

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Sheet'))
        layout.addWidget(self.le1)
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.le3)

        self.valueboxes = []
        for valuename, v in zip(valuenames, values):
            templayout = qg.QHBoxLayout()
            valueedit = qg.QLineEdit()
            valueedit.setAlignment(qc.Qt.AlignRight)
            valueedit.setText(str(v))

    #        self.valueedit.setInputMask('#009.0')
            valueedit.setValidator(StrictDoubleValidator(popupcad.gui_negative_infinity, popupcad.gui_positive_infinity, popupcad.gui_default_decimals, valueedit))
            templayout.addStretch()
            templayout.addWidget(qg.QLabel(valuename))
            templayout.addWidget(valueedit)
            self.valueboxes.append(valueedit)
            layout.addLayout(templayout)

        self.radiobuttons = []
        if 'keepout' in show:
            for key, value2 in keepouttypes.dict.items():
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

        button1.clicked.connect(self.accept)
        button2.clicked.connect(self.reject)

    def acceptdata(self):
        option = None
        for b in self.radiobuttons:
            if b.isChecked():
                option = b.uservalue

        operation_links = {
            'sheet': self.le1.currentRefs(),
            'device': self.le3.currentRefs()}
        values = [float(valueedit.text()) for valueedit in self.valueboxes]
        return operation_links, values, option


class ScrapOperation2(Operation2):
    name = 'Scrap'
    valuenames = ['device buffer']
    show = []
    defaults = [1.]

    def copy(self):
        new = type(self)(self.operation_links, self.values, self.keepout_type)
        new.customname = self.customname
        new.id = self.id
        return new

    keepout_types = enum.enum(
        laser_keepout=301,
        mill_keepout=302,
        mill_flip_keepout=303)

    def __init__(self, *args):
        super(ScrapOperation2, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, operation_links, values, keepout_type):
        super(ScrapOperation2, self).editdata(operation_links, {}, {})
        self.values = values
        self.keepout_type = keepout_type

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(
            cls.keepout_types,
            cls.valuenames,
            cls.defaults,
            design.operations,
            cls.show,
            keepouttype=cls.keepout_types.laser_keepout)
        return dialog

    def buildeditdialog(self, design):
        sheet_id, sheet_output = self.operation_links['sheet'][0]
        device_id, device_output = self.operation_links['device'][0]

        sheet_index = design.operation_index(sheet_id)
        device_index = design.operation_index(device_id)
        operationindeces = [
            [sheet_index, sheet_output], [device_index, device_output]]

        dialog = Dialog(
            self.keepout_types,
            self.valuenames,
            self.defaults,
            design.prioroperations(self),
            self.show,
            operationindeces,
            self.values,
            self.keepout_type)
        return dialog

    def generate(self, design):
        import popupcad
        import popupcad.algorithms.removability as removability

        sheet_id, sheet_output = self.operation_links['sheet'][0]
        device_id, device_output = self.operation_links['device'][0]

        sheet = design.op_from_ref(sheet_id).output[sheet_output].csg
        device = design.op_from_ref(device_id).output[device_output].csg

        removable_both, removable_up, removable_down = removability.generate_removable_scrap(
            device, sheet, device_buffer=self.values[0] *popupcad.csg_processing_scaling)

        a = OperationOutput(removable_both, 'removable_both', self)
        b = OperationOutput(removable_up, 'removable_up', self)
        c = OperationOutput(removable_down, 'removable_down', self)
        self.output = [a, a, b, c]
