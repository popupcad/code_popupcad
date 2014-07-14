# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation

class OuterSheet2(MultiValueOperation2):
    name = 'Sheet'
    show = []
    valuenames = ['Buffer']
    defaults = [0.]

    def operate(self,design):
        import popupcad.algorithms.web as web
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        ls,dummy = web.supportsheet(design.layerdef(),ls1,2.*self.values[0]*popupcad.internal_argument_scaling)
        return ls
                