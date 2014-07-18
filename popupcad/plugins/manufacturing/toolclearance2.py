# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation

class ToolClearance2(MultiValueOperation2):
    name = 'ToolClearance'
    valuenames = []
    defaults = []

    def operate(self,design):
        import popupcad
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            toolclearance = popupcad.algorithms.toolclearance.laserclearance(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            toolclearance = popupcad.algorithms.toolclearance.millclearance(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            toolclearance = popupcad.algorithms.toolclearance.millflipclearance(ls1)
        else:
            raise(Exception('keepout type'))
            
        return toolclearance

