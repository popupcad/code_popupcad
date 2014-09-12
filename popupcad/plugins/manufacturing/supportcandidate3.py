# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation
from .. import algorithms

class SupportCandidate3(MultiValueOperation2):
    name = 'Support Candidate'
    valuenames = ['Support Gap','Keep-out Distance']
    defaults = [0.,0.]

    def operate(self,design):
        import popupcad
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            keepout = popupcad.algorithms.keepout.laserkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            keepout = popupcad.algorithms.keepout.millkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            keepout = popupcad.algorithms.keepout.millflipkeepout(ls1)
        else:
            raise(Exception('keepout type'))
            
        support=algorithms.web.autosupport(ls1,keepout,design.layerdef(),self.values[0]*popupcad.internal_argument_scaling,self.values[1]*popupcad.internal_argument_scaling)
        return support

