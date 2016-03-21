# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3


class Simplify2(MultiValueOperation3):
    name = 'Simplify'
    show = []
#    function = 'buffer'
    valuenames = ['Tolerance']
    defaults = [0.01, 1]

    def operate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg
        return popupcad.algorithms.morphology.simplify(
            ls1,
            self.values[0] *
            popupcad.csg_processing_scaling)
