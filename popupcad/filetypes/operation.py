# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from dev_tools.acyclicdirectedgraph import Node
from popupcad.filetypes.userdata import UserData
from popupcad.filetypes.classtools import ClassTools
from popupcad.filetypes.operationoutput import OperationOutput


class Operation(Node, UserData, ClassTools):
    name = 'Operation'
    attr_init = tuple()
    attr_init_k = tuple()
    attr_copy = tuple()

    def __init__(self):
        Node.__init__(self)
        UserData.__init__(self)

    def editdata(self):
        try:
            del self.output
        except AttributeError:
            pass

    def get_design(self):
        return self._design
    def set_design(self,design):
        self._design = design
    def del_design(self):
        del self._design
    design = property(get_design,set_design,del_design)

    def parentrefs(self):
        return []

    def subdesignrefs(self):
        return []

    def sketchrefs(self):
        return []

    def copy(self):
        newop = self.init_copy(self.attr_init, self.attr_init_k)
        newop.copyattrs(self, self.attr_copy)
        return newop

#    def copy(self, *args, **kwargs):
#        return self

    def upgrade(self, *args, **kwargs):
        return self

    def getoutputref(self):
        try:
            return self._outputref
        except AttributeError:
            self._outputref = 0
            return self._outputref

    def generate_outer1(self):
        design = self.design
        self.generate(design)

    def generate(self, design):
        result = self.operate(design)
        output = OperationOutput(result, 'default', self)
        self.output = [output]

    @classmethod
    def new(cls, parent, design, currentop, newsignal):
        dialog = cls.buildnewdialog(design, currentop)
        if dialog.exec_() == dialog.Accepted:
            operation = cls(*dialog.acceptdata())
            newsignal.emit(operation)

    def edit(self, parent, design, editedsignal):
        dialog = self.buildeditdialog(design)
        if dialog.exec_() == dialog.Accepted:
            self.editdata(*dialog.acceptdata())
            editedsignal.emit(self)

    def description_get(self):
        try:
            return self._description
        except AttributeError:
            self._description = ''
            return self._description

    def description_set(self, value):
        self._description = value

    description = property(description_get, description_set)

    def edit_description(self):
        import qt
        qc = qt.QtCore
        qg = qt.QtGui
        result, ok = qg.QInputDialog.getText(
            None, 'description', 'label', text=self.description)
        if ok:
            self.description = result

    def copy_internals(self, new):
        new.id = self.id
        new.customname = self.customname
        new.description = self.description
        return new

    def copy_wrapper(self):
        new = self.copy()
        self.copy_internals(new)
        return new

    def upgrade_wrapper(self):
        new = self.upgrade()
        self.copy_internals(new)
        return new
