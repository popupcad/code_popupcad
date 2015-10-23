# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad_deprecated.toolclearance3 import ToolClearance3


class ToolClearance2(MultiValueOperation2):
    name = 'ToolClearance'
    valuenames = []
    defaults = []
    upgradeclass = ToolClearance3

    def operate(self, design):
        import popupcad.algorithms.toolclearance as toolclearance
        ls1 = design.op_from_ref(
            self.operation_link1).output[
            self.getoutputref()].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            toolclearance = toolclearance.laserclearance(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            toolclearance = toolclearance.millclearance(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            toolclearance = toolclearance.millflipclearance(ls1)
        else:
            raise Exception

        return toolclearance
