# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.manufacturing.cleanup2 import Cleanup2


class Cleanup(MultiValueOperation2):
    name = 'Cleanup'
    show = []
#    function = 'buffer'
    valuenames = ['Buffer', 'Resolution']
    defaults = [0.0001, 1]
    upgradeclass = Cleanup2

    def operate(self, design):
        ls1 = design.op_from_ref(
            self.operation_link1).output[
            self.getoutputref()].csg
        return popupcad.algorithms.morphology.cleanup(
            ls1, self.values[0] * popupcad.csg_processing_scaling, int(self.values[1]))
