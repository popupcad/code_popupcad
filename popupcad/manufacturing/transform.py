# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
import numpy
from math import cos,sin,pi

class TransformOperation(MultiValueOperation3):
    name = 'Transform'
    show = []
#    function = 'buffer'
    valuenames = ['Rotate', 'X Shift', 'Y Shift']
    defaults = [0,0,0]

    def operate(self, design):
        link, output = self.operation_links['parent'][0]
        generic = design.op_from_ref(link).output[output].generic_laminate()
        
        cq = cos(self.values[0]*pi/180)
        sq = sin(self.values[0]*pi/180)

        T = numpy.array([[cq,-sq,self.values[1]],[sq,cq,self.values[2]],[0,0,1]])
        generic2 = generic.transform(T)
        csg2 = generic2.to_csg()

        return csg2