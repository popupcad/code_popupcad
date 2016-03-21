# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operationoutput import OperationOutput

class SupportCandidate4(MultiValueOperation3):
    name = 'Support'
    valuenames = ['Support Gap', 'Keep-out Distance']
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
        else:
            raise Exception

        support, k3 = popupcad.algorithms.web.autosupport(ls1, keepout, design.return_layer_definition(), self.values[
                                                 0] *popupcad.csg_processing_scaling, self.values[1] *popupcad.csg_processing_scaling, 1e-5 *popupcad.csg_processing_scaling)
        a = OperationOutput(support, 'support', self)
        b = OperationOutput(keepout, 'cut line', self)
        c = OperationOutput(k3, 'cut area', self)
        self.output = [a, a, b, c]
