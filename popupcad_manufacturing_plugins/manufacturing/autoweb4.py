# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operationoutput import OperationOutput
import popupcad_manufacturing_plugins.algorithms as algorithms


class AutoWeb4(MultiValueOperation3):
    name = 'Web'
    valuenames = ['Outer Buffer', 'Support Gap']
    defaults = [0., 0.]

    def generate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]

        import popupcad
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            keepout = popupcad.algorithms.keepout.laserkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            keepout = popupcad.algorithms.keepout.millkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            keepout = popupcad.algorithms.keepout.millflipkeepout(ls1)

        sheet, outer_web, inner_elements, buffered_keepout = algorithms.web.generate_web(ls1, keepout, design.return_layer_definition(
        ), (self.values[0] + self.values[1]) *popupcad.csg_processing_scaling, self.values[1] *popupcad.csg_processing_scaling)

        a = OperationOutput(outer_web, 'Web', self)
        b = OperationOutput(sheet, 'Sheet', self)
        c = OperationOutput(inner_elements, 'Inner Scrap', self)
        d = OperationOutput(buffered_keepout, 'Removed Material', self)
        self.output = [a, b, c, d]
