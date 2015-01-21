# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.manufacturing.simplify2 import Simplify2

class Simplify(MultiValueOperation2):
    name = 'Simplify'
    show = []
#    function = 'buffer'
    valuenames = ['Tolerance']
    defaults = [0.01,1]
    upgradeclass = Simplify2

    def operate(self,design):
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        return popupcad.algorithms.morphology.simplify(ls1,self.values[0]*popupcad.internal_argument_scaling)

