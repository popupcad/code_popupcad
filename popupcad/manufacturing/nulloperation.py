# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.operation import Operation
from popupcad.materials.laminatesheet import Laminate

class NullOp(Operation):
    name = 'None'

    attr_init = tuple()
    attr_init_k = tuple()
    attr_copy = 'id','customname'

    def __init__(self,*args):
        super(NullOp,self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def operate(self,design):
        laminate = Laminate(design.layerdef())
        return laminate
        
    @classmethod
    def new(cls,parent,design,currentop,newsignal):
        operation = cls()
        newsignal.emit(operation)

    def edit(self,parent,design,editedsignal):
        pass
        