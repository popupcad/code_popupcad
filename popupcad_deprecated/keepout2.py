# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad_manufacturing_plugins.manufacturing.keepout3 import KeepOut3


class KeepOut2(MultiValueOperation2):
    name = 'KeepOut'
    valuenames = []
    defaults = []
    upgradeclass = KeepOut3

    def operate(self, design):
        import popupcad
        ls1 = design.op_from_ref(
            self.operation_link1).output[
            self.getoutputref()].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            keepout = popupcad.algorithms.keepout.laserkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            keepout = popupcad.algorithms.keepout.millkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            keepout = popupcad.algorithms.keepout.millflipkeepout(ls1)
        else:
            raise Exception
        return keepout
