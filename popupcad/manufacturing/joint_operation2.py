# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 14:41:02 2014

@author: danaukes
"""

from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.genericlaminate import GenericLaminate
from popupcad.filetypes.operation2 import Operation2
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer
import numpy
import math
import operator
import popupcad_manufacturing_plugins
from popupcad.widgets.joint_op_dialog import MainWidget

class JointDef(object):
    def __init__(self,sketch,joint_layer,sublaminate_layers,width):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width

class JointOperation2(Operation2):
    name = 'Joint Definition'
#    hinge_gap = .01*popupcad.internal_argument_scaling
#    safe_buffer1 = .5*hinge_gap
#    safe_buffer2 = .5*hinge_gap
#    safe_buffer3 = .5*hinge_gap
#    split_buffer = .1*hinge_gap
    resolution = 2
    
    name = 'Joint Operation'
    def copy(self):
        new = type(self)(self.operation_links,self.joint_defs)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(JointOperation2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,operation_links,joint_defs):  
        self.operation_links = operation_links
        self.joint_defs = joint_defs
        self.clear_output()

    def operate(self,design):
        joint_def = self.joint_defs[0]
        operationgeom = design.sketches[joint_def.sketch].output_csg()
        layers = [design.return_layer_definition().getlayer(joint_def.joint_layer)]
#        operationgeom = popupcad.geometry.customshapely.multiinit(operationgeom)
        laminate = Laminate(design.return_layer_definition())
        for layer in layers:
            laminate.replacelayergeoms(layer,operationgeom)
        return laminate


    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.prioroperations(self),self)
        return dialog

    def sketchrefs(self):
        return [item.sketch for item in self.joint_defs]
    
    def subdesignrefs(self):
        return []
    
    def generate(self,design):
        layerdef = design.return_layer_definition()
        sublaminate_layers = layerdef.layers
        sketch_result = self.operate(design)


        for joint_def in self.joint_defs:
        
            hinge_gap = joint_def.width*popupcad.internal_argument_scaling
            safe_buffer1 = .5*hinge_gap
            safe_buffer2 = .5*hinge_gap
            safe_buffer3 = .5*hinge_gap
            split_buffer = .1*hinge_gap
            
            
            hingelayer = layerdef.getlayer(joint_def.joint_layer)        
            hingelines = sketch_result.genericfromls()[hingelayer]
            hingelayer_ii = layerdef.getlayer_ii(joint_def.joint_layer)
    
    #        holes,allgeoms,hingelayer = popupcad.algorithms.points.jointholes(sketch_result,layerdef)
            safe_sections = []
            allgeoms2 = [geom.outputshapely() for geom in hingelines]
            allgeoms3 = [Laminate(layerdef) for item in allgeoms2]
            allgeoms4 = []
            for laminate,geom in zip(allgeoms3,allgeoms2):
                laminate[hingelayer_ii] = [geom]
                allgeoms4.append(laminate.buffer(hinge_gap,resolution = self.resolution))
                
            for ii,lam in enumerate(allgeoms4):
                unsafe = Laminate.unaryoperation(allgeoms4[:ii]+allgeoms4[ii+1:],'union')
                safe_sections.append(lam.difference(unsafe.buffer(safe_buffer1,resolution = self.resolution)))
            safe = Laminate.unaryoperation(safe_sections,'union')
    #        safe = safe_sections[0]
            unsafe = Laminate.unaryoperation(allgeoms4,'union').difference(safe.buffer(safe_buffer2,resolution = self.resolution))
            unsafe2 = unsafe.unarylayeroperation('union',[hingelayer],sublaminate_layers).buffer(safe_buffer3,resolution = self.resolution)
    
            
    #        buffered = sketch_result.buffer(hinge_gap,resolution = self.resolution)
            buffered2 = sketch_result.buffer(split_buffer,resolution = self.resolution)
    #        self_index = design.operation_index(self.id)
    #        last = design.operations[self_index-1].output[0].csg
            parent_id,parent_output_index = self.operation_links['parent'][0]
            parent_index = design.operation_index(parent_id)
            last = design.operations[parent_index].output[parent_output_index].csg
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
        
        self.connections = [(key,connections[key]) for key in hingelines]
        
        laminates = [sketch_result,safe,unsafe2,split1,split2]+bodies+list(connections2.values())
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])

