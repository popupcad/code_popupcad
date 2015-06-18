# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.operation2 import Operation2
from popupcad.filetypes.laminate import Laminate


class NullOp(Operation2):
    name = 'None'

    def __init__(self):
        super(NullOp, self).__init__()
        self.editdata({}, {}, {})
        self.id = id(self)

    def copy(self):
        new = type(self)()
        new.id = self.id
        new.customname = self.customname
        return new

    def operate(self, design):
        laminate = Laminate(design.return_layer_definition())
        return laminate

    @classmethod
    def new(cls, parent, design, currentop, newsignal):
        operation = cls()
        newsignal.emit(operation)

    def edit(self, parent, design, editedsignal):
        pass
