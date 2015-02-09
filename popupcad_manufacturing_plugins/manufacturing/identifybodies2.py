# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.laminate import Laminate
import numpy

def find_minimum_xy(geom):
    points = numpy.array(geom.exteriorpoints())
    min_x,min_y = points.min(0)
    return min_x,min_y
    
def sort_lams(lams,values):
    dtype = [('x',float),('y',float)]
    mins = numpy.array(values,dtype)
    ii_mins = mins.argsort(order=['x','y'])
    lam_out = [lams[ii] for ii in ii_mins]
    return lam_out

class IdentifyBodies2(MultiValueOperation3):
    name = 'Identify Bodies'
    show = []
    valuenames = []
    defaults = []

    def generate(self,design):
        import popupcad_manufacturing_plugins.algorithms.bodydetection as bodydetection

        operation_ref,output_index = self.operation_links['parent'][0]
        operation_output= design.op_from_ref(operation_ref).output[output_index]
        lam_in = operation_output.csg
        generic = lam_in.generic_geometry_2d()
        layerdef = design.return_layer_definition()

        layer_dict = dict([(geom.id,layer) for layer,geoms in generic.items() for geom in geoms])
        geom_dict = dict([(geom.id,geom) for layer,geoms in generic.items() for geom in geoms])
        geom_dict_whole = geom_dict.copy()
        
        laminates = []
        values = []
        layerdef = design.return_layer_definition()
        while len(geom_dict)>0:
            laminate = Laminate(layerdef)
            key = list(geom_dict.keys())[0]
            gs = bodydetection.findallconnectedneighborgeoms(key,generic,geom_dict,layerdef)
            geom_mins = numpy.array([find_minimum_xy(geom_dict_whole[geom_id]) for geom_id in gs])
            values.append(tuple(geom_mins.min(0)))
            for item_id in gs:
                geom = geom_dict_whole[item_id]
                laminate.insertlayergeoms(layer_dict[item_id], [geom.outputshapely()])
            laminates.append(laminate)
            
        laminates = sort_lams(laminates,values)
        
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])
                