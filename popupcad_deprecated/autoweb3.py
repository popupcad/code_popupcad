# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operationoutput import OperationOutput
import popupcad_manufacturing_plugins.algorithms as algorithms
from popupcad_manufacturing_plugins.manufacturing.autoweb4 import AutoWeb4


class AutoWeb3(MultiValueOperation2):
    name = 'Web'
    valuenames = ['Outer Buffer', 'Support Gap']
    defaults = [0., 0.]
    upgradeclass = AutoWeb4

    def generate(self, design):
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

        sheet, outer_web, inner_elements, buffered_keepout = algorithms.web.generate_web(ls1, keepout, design.return_layer_definition(
        ), (self.values[0] + self.values[1]) * popupcad.internal_argument_scaling*popupcad.csg_processing_scaling, self.values[1] * popupcad.internal_argument_scaling*popupcad.csg_processing_scaling)

        a = OperationOutput(outer_web, 'Web', self)
        b = OperationOutput(sheet, 'Sheet', self)
        c = OperationOutput(inner_elements, 'Inner Scrap', self)
        d = OperationOutput(buffered_keepout, 'Removed Material', self)
        self.output = [a, b, c, d]
