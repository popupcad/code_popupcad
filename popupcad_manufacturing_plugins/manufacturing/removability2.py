# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
import dev_tools.enum as enum
import popupcad

class Removability2(MultiValueOperation3):
    name = 'Removability'
    valuenames = []
    defaults = []
    keepout_types = enum.enum(
        one_way_up='one_way_up',
        one_way_down='one_way_down',
        two_way='two_way')
    keepout_type_default = keepout_types.one_way_up

    def operate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg

        if self.keepout_type == self.keepout_types.one_way_up:
            keepout = popupcad.algorithms.removability.one_way_up(ls1)
        elif self.keepout_type == self.keepout_types.one_way_down:
            keepout = popupcad.algorithms.removability.one_way_down(ls1)
        elif self.keepout_type == self.keepout_types.two_way:
            keepout = popupcad.algorithms.removability.two_way(ls1)
        else:
            raise Exception
        return keepout
