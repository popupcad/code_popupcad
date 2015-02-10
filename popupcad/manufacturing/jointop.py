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
import numpy
import math
import operator

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
                layer_ii = layerdef.layers.index(layer)
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

        shapelys = []
        for point in commonpoints:
            lineset = {}
            for item in allgeoms:
                points = numpy.array(item.exteriorpoints())
                points -= point
                l = (points[:,0]**2+points[:,1]**2)**.5
                test = l<1e-5
                if True in test:
                    ii = 1-test.nonzero()[0][0]
                    lineset[item] = math.atan2(points[ii,1],points[ii,0])
            q_s = sorted(lineset.items(),key = operator.itemgetter(1))
            gaps = [item1[1]-item0[1] for item0,item1 in zip(q_s[:-1],q_s[1:])] + [2*math.pi+q_s[0][1]-q_s[-1][1]]
            min_gap = min(gaps)
            bufferval = 1.1/math.sin(min_gap/2)
#            print(gaps,min_gap,bufferval)
            shapely = popupcad.geometry.vertex.DrawnPoint(position = point).outputshapely()
            shapely = shapely.buffer(bufferval*popupcad.internal_argument_scaling)
            shapelys.append(shapely)
        shapelys = popupcad.geometry.customshapely.multiinit(*shapelys)
#        generics = [popupcad.geometry.vertex.DrawnPoint(position = point) for point in commonpoints]
#        shapelys = [item.outputshapely() for item in generics]
#        layer = Layer(shapelys)
        holes = Laminate(layerdef)
        holes.replacelayergeoms(layer,shapelys)
        
        safe_sections = []
        allgeoms2 = [geom.outputshapely() for geom in allgeoms]
        allgeoms3 = [Laminate(layerdef) for item in allgeoms2]
        allgeoms4 = []
        for laminate,geom in zip(allgeoms3,allgeoms2):
            laminate[layer_ii] = [geom]
            allgeoms4.append(laminate.buffer(1*popupcad.internal_argument_scaling))
            
        for ii,lam in enumerate(allgeoms4):
            unsafe_lams = allgeoms4[:ii]+allgeoms4[ii+1:]
            b = Laminate.unaryoperation(unsafe_lams,'union')
            safe_sections.append(lam.difference(b.buffer(.5*popupcad.internal_argument_scaling)))
        safe = Laminate.unaryoperation(safe_sections,'union')
#        safe = safe_sections[0]
        unsafe = Laminate.unaryoperation(allgeoms4,'union').difference(safe.buffer(.25*popupcad.internal_argument_scaling))
        

        
        buffered = sketch_result.buffer(.99*popupcad.internal_argument_scaling)
        buffered2 = sketch_result.buffer(1.1*popupcad.internal_argument_scaling)
        self_index = design.operation_index(self.id)
        last = design.operations[self_index-1].output[0].csg
        separated = last.difference(buffered)
        sep2 = Laminate(layerdef)
        sep2.layer_sequence[layer]=separated.layer_sequence[layer]
        
        
        laminates = [sketch_result,buffered,sep2,holes,safe,unsafe]
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])

