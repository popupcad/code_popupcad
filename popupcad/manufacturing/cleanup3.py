# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3


class Cleanup3(MultiValueOperation3):
    name = 'New Cleanup'
    show = []
#    function = 'buffer'
    valuenames = ['Buffer', 'Resolution']
    defaults = [0.0001, 1]

    def operate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg

        value = self.values[0] *popupcad.csg_processing_scaling
        res = int(self.values[1])

        ls11 = popupcad.algorithms.manufacturing_functions.cleanup3(ls1,value,res)
        return ls11
