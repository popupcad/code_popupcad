# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.operationoutput import OperationOutput
from .. import algorithms

class SupportCandidate4(MultiValueOperation3):
    name = 'Support Candidate'
    valuenames = ['Support Gap','Keep-out Distance']
    defaults = [0.,0.]

    def generate(self,design):
        operation_ref,output_index = self.operation_links['parent'][0]
        import popupcad
        ls1 = design.op_from_ref(operation_ref).output[output_index].csg

        if self.keepout_type == self.keepout_types.laser_keepout:
            keepout = popupcad.algorithms.keepout.laserkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_keepout:
            keepout = popupcad.algorithms.keepout.millkeepout(ls1)
        elif self.keepout_type == self.keepout_types.mill_flip_keepout:
            keepout = popupcad.algorithms.keepout.millflipkeepout(ls1)
        else:
            raise(Exception('keepout type'))
            
        support=algorithms.web.autosupport(ls1,keepout,design.return_layer_definition(),self.values[0]*popupcad.internal_argument_scaling,self.values[1]*popupcad.internal_argument_scaling)
        k2 = keepout.buffer(1e-5*popupcad.internal_argument_scaling)
        k3 = k2.difference(keepout)
#        return support
        a = OperationOutput(support,'support',self)
        b = OperationOutput(keepout,'cut line',self)
        c = OperationOutput(k3,'cut area',self)
#        d = OperationOutput(up_support ,'up_support',self)
#        e = OperationOutput(down_support ,'down_support',self)
#        self.output = [a,a,b,c,d,e]
        self.output = [a,a,b,c]                
    

