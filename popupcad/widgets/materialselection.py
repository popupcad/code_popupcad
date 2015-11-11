# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
#import popupcad.materials.materials as materials
from popupcad.filetypes.layerdef import LayerDef

import qt.QtCore as qc
import qt.QtGui as qg

class ClassItem(qg.QListWidgetItem):

    def __init__(self, *args, **kwargs):
        super(ClassItem, self).__init__(*args, **kwargs)

    def setClass(self, class1):
        self.class1 = class1

    def getClass(self):
        return self.class1


class MaterialSelection(qg.QDialog):

    def __init__(self, initialleft, initialright, *args, **kwargs):
        super(MaterialSelection, self).__init__(*args, **kwargs)

        self.layerdef = LayerDef(*initialleft)
        self.lw = qg.QListWidget(self)
        self.lw.itemDoubleClicked.connect(self.remove_item)

        self.rw = qg.QListWidget(self)
        self.rw.itemDoubleClicked.connect(self.add_item)

        self.ok_button = qg.QPushButton('&Ok', self)
        self.cancel_button = qg.QPushButton('&Cancel', self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        l1 = qg.QHBoxLayout()
        l1.addWidget(self.lw)
        l1.addWidget(self.rw)

        l3 = qg.QHBoxLayout()
        l3.addStretch(1)
        l3.addWidget(self.ok_button)
        l3.addWidget(self.cancel_button)
        l3.addStretch(1)

        l2 = qg.QVBoxLayout()
        l2.addLayout(l1)
        l2.addLayout(l3)

        self.setLayout(l2)
        self.setWindowTitle('Material Selection')
        self.initialize_right(initialright)
        self.update_left()

    def add_item(self, item):
        self.layerdef.addlayer(item.class1.copy())
        self.update_left()

    def update_left(self):
        self.lw.clear()
        for item in self.layerdef.layers:
            ci = ClassItem(item.name)
            ci.setClass(item)
            self.lw.addItem(ci)

    def remove_item(self, item):
        ii = self.lw.row(item)
        self.layerdef.layers.pop(ii)
        self.update_left()

    def initialize_right(self, items):
        self.lw.clear()
        for item in items:
            ci = ClassItem(item.name)
            ci.setClass(item)
            self.rw.addItem(ci)

    def initialize_left(self, items):
        self.lw.clear()
        for item in items:
            ci = ClassItem(item.name)
            ci.setClass(item)
            self.lw.addItem(ci)

if __name__ == '__main__':
    import sys

    app = qg.QApplication(sys.argv)

    window = MaterialSelection([], [])
    a = window.exec_()
