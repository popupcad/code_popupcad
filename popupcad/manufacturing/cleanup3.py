# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from .multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operation import Operation

class Cleanup3(MultiValueOperation3):
    name = 'Cleanup'
    show = []
#    function = 'buffer'
    valuenames = ['Buffer','Resolution']
    defaults = [0.0001,1]

    def operate(self,design):
        operation_ref,output_index = self.operation_links['parent'][0]
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg
        
        value = self.values[0]*popupcad.internal_argument_scaling
        res = int(self.values[1])       
        
        ls2 = ls1.buffer(-value,resolution = res)        
        ls3 = ls2.buffer(2*value,resolution = res)
        ls4 = ls1.intersection(ls3)
        
        ls5 = ls1.buffer(value*10,resolution = res)
        ls6 = ls5.difference(ls1)
        ls7 = ls6.buffer(-value,resolution = res)        
        ls8 = ls7.buffer(2*value,resolution = res)
        ls9 = ls6.intersection(ls8)
        ls9_1 = ls5.difference(ls9)
        ls10 = ls4.symmetric_difference(ls9_1)
        ls11 = ls1.symmetric_difference(ls10)
        
        return ls11

        