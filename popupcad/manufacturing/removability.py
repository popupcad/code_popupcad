# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from .multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation
import popupcad.filetypes.enum as enum

class Removability(MultiValueOperation2):
    name = 'Removability KeepOut'
    valuenames = []
    defaults = []
    keepout_types = enum.enum(one_way_up = 'one_way_up', one_way_down = 'one_way_down',two_way = 'two_way')
    keepout_type_default = keepout_types.one_way_up
    def operate(self,design):
        import popupcad
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg

        if self.keepout_type == self.keepout_types.one_way_up:
            keepout = popupcad.algorithms.removability.one_way_up(ls1)
        elif self.keepout_type == self.keepout_types.one_way_down:
            keepout = popupcad.algorithms.removability.one_way_down(ls1)
        elif self.keepout_type == self.keepout_types.two_way:
            keepout = popupcad.algorithms.removability.two_way(ls1)
        else:
            raise(Exception('keepout type'))
        return keepout

