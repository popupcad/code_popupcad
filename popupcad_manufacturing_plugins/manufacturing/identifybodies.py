# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation
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

class IdentifyBodies(MultiValueOperation2):
    name = 'Identify Bodies'
    show = []
    valuenames = []
    defaults = []

    def generate(self,design):
        from ..algorithms import bodydetection as bd
        
        generic = design.op_from_ref(self.operation_link1).output[self.getoutputref()].generic_geometry_2d()
        layerdef = design.layerdef()

        layer_dict = dict([(geom.id,layer) for layer,geoms in generic.items() for geom in geoms])
        geom_dict = dict([(geom.id,geom) for layer,geoms in generic.items() for geom in geoms])
        geom_dict_whole = geom_dict.copy()
        
        laminates = []
        values = []
        while len(geom_dict)>0:
            laminate = Laminate(layerdef)
            g = geom_dict.values()[0]
            gs = bd.findallconnectedneighborgeoms(design,g.id,generic_geometry = generic)
            geom_mins = numpy.array([find_minimum_xy(geom_dict_whole[geom_id]) for geom_id in gs])
            values.append(tuple(geom_mins.min(0)))
            for item_id in gs:
                geom = geom_dict.pop(item_id)
                laminate.insertlayergeoms(layer_dict[item_id], [geom.outputshapely()])
            laminates.append(laminate)
            
        laminates = sort_lams(laminates,values)
        
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])
                