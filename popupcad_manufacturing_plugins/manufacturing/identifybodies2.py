# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operationoutput import OperationOutput
import popupcad_manufacturing_plugins


class IdentifyBodies2(MultiValueOperation3):
    name = 'Identify Bodies'
    show = []
    valuenames = []
    defaults = []

    def generate(self,design):
        operation_ref,output_index = self.operation_links['parent'][0]
        operation_output= design.op_from_ref(operation_ref).output[output_index]
#        lam_in = operation_output.csg
        generic = operation_output.generic_geometry_2d()
        layerdef = design.return_layer_definition()

        laminates = popupcad_manufacturing_plugins.algorithms.bodydetection.find(generic,layerdef)            
        
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])
                