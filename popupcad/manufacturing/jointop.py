# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 14:41:02 2014

@author: danaukes
"""

from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.genericlaminate import GenericLaminate
from popupcad.manufacturing.simplesketchoperation import SimpleSketchOp
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer
import numpy
import math
import operator
import popupcad_manufacturing_plugins

class JointOp(SimpleSketchOp):
    name = 'Joint Definition'
    hinge_gap = 1*popupcad.internal_argument_scaling
    safe_buffer1 = .5*popupcad.internal_argument_scaling
    safe_buffer2 = .5*popupcad.internal_argument_scaling
    safe_buffer3 = .5*popupcad.internal_argument_scaling
    split_buffer = .1*popupcad.internal_argument_scaling
    resolution = 2
    
    pass
    
    def generate(self,design):
        layerdef = design.return_layer_definition()
        sublaminate_layers = layerdef.layers
        sketch_result = self.operate(design)

        hingelayer = layerdef.getlayer(self.layer_links[0])        
        hingelines = sketch_result.genericfromls()[hingelayer]
        hingelayer_ii = layerdef.getlayer_ii(self.layer_links[0])

#        holes,allgeoms,hingelayer = popupcad.algorithms.points.jointholes(sketch_result,layerdef)
        safe_sections = []
        allgeoms2 = [geom.outputshapely() for geom in hingelines]
        allgeoms3 = [Laminate(layerdef) for item in allgeoms2]
        allgeoms4 = []
        for laminate,geom in zip(allgeoms3,allgeoms2):
            laminate[hingelayer_ii] = [geom]
            allgeoms4.append(laminate.buffer(self.hinge_gap,resolution = self.resolution))
            
        for ii,lam in enumerate(allgeoms4):
            unsafe = Laminate.unaryoperation(allgeoms4[:ii]+allgeoms4[ii+1:],'union')
            safe_sections.append(lam.difference(unsafe.buffer(self.safe_buffer1,resolution = self.resolution)))
        safe = Laminate.unaryoperation(safe_sections,'union')
#        safe = safe_sections[0]
        unsafe = Laminate.unaryoperation(allgeoms4,'union').difference(safe.buffer(self.safe_buffer2,resolution = self.resolution))
        unsafe2 = unsafe.unarylayeroperation('union',[hingelayer],sublaminate_layers).buffer(self.safe_buffer3,resolution = self.resolution)

        
#        buffered = sketch_result.buffer(self.hinge_gap,resolution = self.resolution)
        buffered2 = sketch_result.buffer(self.split_buffer,resolution = self.resolution)
        self_index = design.operation_index(self.id)
        last = design.operations[self_index-1].output[0].csg
#        separated = last.difference(buffered)
#        sep2 = Laminate(layerdef)
#        sep2[hingelayer_ii]=separated[hingelayer_ii]
        
        split1 = last.difference(unsafe2)
        split2 = split1.difference(buffered2)
        bodies= popupcad_manufacturing_plugins.algorithms.bodydetection.find(split2.genericfromls(),layerdef)
        
        bodies_generic = [item.genericfromls() for item in bodies]
        bodies_generic = [GenericLaminate(layerdef,item) for item in bodies_generic]
        
        connections = {}
        connections2 = {}
        for line,geom in zip(hingelines,safe_sections):
            connections[line]=[]
            connections2[line]=[]
            for body,body_generic in zip(bodies,bodies_generic):
                if not geom.intersection(body).isEmpty():
                    connections[line].append(body_generic)
                    connections2[line].append(body)
#                if not not connections2[line]:
#                    connections2[line].append(geom)
        for line,geoms in connections2.items():
            connections2[line]=Laminate.unaryoperation(geoms,'union')
        
        self.connections = connections
        
        laminates = [sketch_result,safe,unsafe2,split1,split2]+bodies+connections2.values()
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])

