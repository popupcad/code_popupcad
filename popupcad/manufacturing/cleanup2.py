# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from .multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operation import Operation

class Cleanup2(MultiValueOperation3):
    name = 'Cleanup'
    show = []
#    function = 'buffer'
    valuenames = ['Buffer','Resolution']
    defaults = [0.0001,1]

    def operate(self,design):
        operation_ref,output_index = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg
        return popupcad.algorithms.morphology.cleanup(ls1,self.values[0]*popupcad.internal_argument_scaling,int(self.values[1]))

        