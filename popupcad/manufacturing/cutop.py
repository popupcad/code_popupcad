# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from .multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operationoutput import OperationOutput
import popupcad
from popupcad.filetypes.operation import Operation

class CutOperation(MultiValueOperation2):
    name = 'Cuts'
    valuenames = []
    defaults = []
    
    def generate(self,design):
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            keepout = popupcad.algorithms.keepout.laserkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            keepout = popupcad.algorithms.keepout.millkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            keepout = popupcad.algorithms.keepout.millflipkeepout(ls1)

        firstpass = keepout.difference(ls1)
        a = OperationOutput(firstpass,'first pass',self)
        b = OperationOutput(keepout,'second pass',self)
        self.output = [a,a,b]
        
