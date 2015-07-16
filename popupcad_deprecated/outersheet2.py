# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
import popupcad_manufacturing_plugins.algorithms as algorithms
from popupcad_manufacturing_plugins.manufacturing.outersheet3 import OuterSheet3


class OuterSheet2(MultiValueOperation2):
    name = 'Sheet'
    show = []
    valuenames = ['Buffer']
    defaults = [0.]
    upgradeclass = OuterSheet3

    def operate(self, design):
        ls1 = design.op_from_ref(
            self.operation_link1).output[
            self.getoutputref()].csg
        ls, dummy = algorithms.web.supportsheet(design.return_layer_definition(
        ), ls1, self.values[0] * popupcad.internal_argument_scaling*popupcad.csg_processing_scaling)
        return ls
