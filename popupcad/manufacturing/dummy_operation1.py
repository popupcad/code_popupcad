# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from popupcad.filetypes.operation2 import Operation2

class DummyOp1(Operation2):
    name = 'None'

    def __init__(self,laminate):
        super(DummyOp1, self).__init__()
        self.editdata({}, {}, {})
        self.id = id(self)
        self.laminate = laminate
        
    def copy(self):
        new = type(self)()
        new.id = self.id
        new.customname = self.customname
        return new

    def operate(self, design):
        return self.laminate

