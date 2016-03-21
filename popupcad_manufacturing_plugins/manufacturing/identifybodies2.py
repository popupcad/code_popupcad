# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operationoutput import OperationOutput
import popupcad


class IdentifyBodies2(MultiValueOperation3):
    name = 'Identify Bodies'
    show = []
    valuenames = []
    defaults = []

    def generate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        operation_output = design.op_from_ref(
            operation_ref).output[output_index]
        generic = operation_output.generic_laminate()
        laminates = popupcad.algorithms.body_detection.find(generic)
        self.output = []
        for ii, item in enumerate(laminates):
            self.output.append(
                OperationOutput(
                    item,
                    'Body {0:d}'.format(ii),
                    self))
        self.output.insert(0, self.output[0])
