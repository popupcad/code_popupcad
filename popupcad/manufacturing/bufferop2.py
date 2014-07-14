# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation

class BufferOperation2(MultiValueOperation2):
    name = 'Buffer'
    show = []
#    function = 'buffer'
    valuenames = ['Buffer','Resolution']
    defaults = [0.,popupcad.default_buffer_resolution]

    def operate(self,design):
        ls1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        return ls1.buffer(self.values[0]*popupcad.internal_argument_scaling,resolution = int(self.values[1]))