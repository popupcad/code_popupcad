# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3


class OuterSheet3(MultiValueOperation3):
    name = 'Sheet'
    show = []
    valuenames = ['Buffer']
    defaults = [0.]

    def operate(self, design):
        import popupcad.algorithms.web as web
        operation_ref, output_index = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg
        ls, dummy = web.supportsheet(design.return_layer_definition(), ls1, self.values[0] *popupcad.csg_processing_scaling)
        return ls
