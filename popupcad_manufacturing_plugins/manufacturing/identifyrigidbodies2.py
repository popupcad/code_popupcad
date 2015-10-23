# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operationoutput import OperationOutput
import popupcad

class IdentifyRigidBodies2(MultiValueOperation3):
    name = 'Identify Rigid Bodies'
    show = []
    valuenames = []
    defaults = []

    def generate(self, design):
        operation_ref, output_index = self.operation_links['parent'][0]
        generic = design.op_from_ref(
            operation_ref).output[output_index].generic_laminate()
        layerdef = design.return_layer_definition()
        new_csgs = popupcad.algorithms.manufacturing_functions.find_rigid(
            generic,
            layerdef)
        self.output = []
        for ii, item in enumerate(new_csgs):
            self.output.append(
                OperationOutput(
                    item,
                    'Rigid Body {0:d}'.format(ii),
                    self))
        self.output.insert(0, self.output[0])
