# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation

class Cleanup(MultiValueOperation2):
    name = 'Cleanup'
    show = []
#    function = 'buffer'
    valuenames = ['Buffer','Resolution']
    defaults = [0.0001,1]

    def operate(self,design):
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        return popupcad.algorithms.morphology.cleanup(ls1,self.values[0]*popupcad.internal_argument_scaling,int(self.values[1]))
        