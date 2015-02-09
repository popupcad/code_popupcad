# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 14:41:02 2014

@author: danaukes
"""

from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.manufacturing.simplesketchoperation import SimpleSketchOp
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer

class JointOp(SimpleSketchOp):
    name = 'Joint Definition'
    pass
    
    def generate(self,design):
        layerdef = design.return_layer_definition()
        sketch_result = self.operate(design)
        generic = sketch_result.genericfromls()
        for key,value in generic.items():
            if not not value:
                allgeoms = value
                layer = key
        allpoints = []
        for geom in allgeoms:
            allpoints.extend(geom.exteriorpoints())
        allpoints.sort()
        commonpoints = []
        lastpoint = (0,0)
        for ii,point1 in enumerate(allpoints[1:-1]):
            point0 = allpoints[ii]
            point2 = allpoints[ii+2]
            a = popupcad.algorithms.points.twopointsthesame(point1,point2,1e-5)
            b = popupcad.algorithms.points.twopointsthesame(point0,point1,1e-5)
            if ii==0:
                if b:
                    commonpoints.append(point1)
                elif a:
                    commonpoints.append(point1)
            else:
                if (a and (not b)):
                    commonpoints.append(point1)

        generics = [popupcad.geometry.vertex.DrawnPoint(position = point) for point in commonpoints]
        shapelys = [item.outputshapely() for item in generics]
#        layer = Layer(shapelys)
        laminate = Laminate(layerdef)
        laminate.replacelayergeoms(layer,shapelys)
        
        
        buffered = sketch_result.buffer(.99*popupcad.internal_argument_scaling)
        buffered2 = sketch_result.buffer(1.1*popupcad.internal_argument_scaling)
        self_index = design.operation_index(self.id)
        last = design.operations[self_index-1].output[0].csg
        separated = last.difference(buffered)
        sep2 = Laminate(layerdef)
        sep2.layer_sequence[layer]=separated.layer_sequence[layer]
        
        laminates = [sketch_result,buffered,sep2,laminate]
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])

