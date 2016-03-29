# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

#import popupcad
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3

class Fill(MultiValueOperation3):
    name = 'Fill'
    show = []
    valuenames = []
    defaults = []

    def operate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        generic = design.op_from_ref(operation_ref).output[output_index].generic_laminate()
        generic2 = generic.fill()
        return generic2.to_csg()
