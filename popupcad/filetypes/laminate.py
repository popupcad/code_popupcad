# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import shapely.ops as so
import popupcad.geometry.customshapely as customshapely
from popupcad.filetypes.genericshapebase import GenericShapeBase
import shapely.geometry as sg
from popupcad.filetypes.layer import Layer
import popupcad

class IterableLaminate(object):
    def __getitem__(self,index):
        if isinstance(index,int):
            return self.layer_sequence[self.layerdef.layers[index]]
        elif isinstance(index,slice):
            return [self.layer_sequence[layer] for layer in self.layerdef.layers[index]]
    def __setitem__(self,index,v):
        if isinstance(index,int):
            if isinstance(v,Layer):
                v = v.geoms
            self.layer_sequence[self.layerdef.layers[index]] = Layer(v)
        elif isinstance(index,slice):
            for value,layer in zip(v,self.layerdef.layers[index]):
                if isinstance(value,Layer):
                    value = value.geoms
                self.layer_sequence[layer] = Layer(value)
    def __iter__(self):
        for layer in self.layerdef.layers:
            yield self.layer_sequence[layer]

    def __len__(self):
        return len(self.layerdef.layers)
    def flip(self):
        '''flip a laminate'''
        laminateout = Laminate(self.layerdef)
        laminateout[:] = self[::-1]
        return laminateout
        

class Laminate(IterableLaminate):
    def __init__(self,layerdef):
        self.layerdef = layerdef
        self.layer_sequence={}
        for layer in self.layerdef.layers:
            self.replacelayergeoms(layer,[])
    def copy(self):
        new = type(self)(self.layerdef)
        new.layer_sequence = self.layer_sequence.copy()
    def isEmpty(self):
        return all([layer.isEmpty() for layer in self.layer_sequence.values()])
    def replacelayergeoms(self,layer,geoms):
        self.layer_sequence[layer] = Layer(geoms)
    def insertlayergeoms(self,layer,geoms):
        self.layer_sequence[layer].add_geoms(geoms)
    def getlayer(self,ref):
        return self.layerdef.getlayer(ref)

    def union(self,ls2):
        return self.binaryoperation(ls2,'union')        
    def difference(self,ls2):
        return self.binaryoperation(ls2,'difference')        
    def intersection(self,ls2):
        return self.binaryoperation(ls2,'intersection')        
    def symmetric_difference(self,ls2):
        return self.binaryoperation(ls2,'symmetric_difference') 
    def buffer(self,value,**kwargs):
        if not kwargs.has_key('resolution'):
            kwargs['resolution'] = popupcad.default_buffer_resolution
        return self.valueoperation('buffer',value,**kwargs) 
    def cleanup(self,value):
        return popupcad.algorithms.morphology.cleanup(self,value,resolution = 1)
        
    def binaryoperation(self,ls2,function):
        self = self
        lsout = Laminate(self.layerdef)
        layers = self.layerdef.layers
        if self.layerdef!=ls2.layerdef:
            raise(Exception('layerdef must be the same'))
        for layer in layers:
            layer1 = self.layer_sequence[layer]
            layer2 = ls2.layer_sequence[layer]
            layerout = layer1.binaryoperation(layer2,function)
            lsout.replacelayergeoms(layer,layerout.geoms)
        return lsout

    @staticmethod
    def unaryoperation(laminates,function):
        lsout = laminates.pop(0)
        while not not laminates:
            lsout = lsout.binaryoperation(laminates.pop(0),function)
        return lsout

    def valueoperation(self,functionname,value,**kwargs):
        lsout = Laminate(self.layerdef)
        layers = self.layerdef.layers
        for layer in layers:
            layer1 = self.layer_sequence[layer]
            result = layer1.valueoperation(functionname,value,**kwargs)
            lsout.replacelayergeoms(layer,result.geoms)
        return lsout
    
    def unarylayeroperation(self,functionname,selectedinputlayers,selectedoutputlayers):   
        selectedinputlayers = selectedinputlayers[:]
        layer1 = self.layer_sequence[selectedinputlayers.pop(0)]
        for layer in selectedinputlayers:
            layer2 = self.layer_sequence[layer]
            layer1 = layer1.binaryoperation(layer2,functionname)
        result = customshapely.unary_union_safe(layer1.geoms)
        geoms1 = customshapely.multiinit(result)
        lsout = Laminate(self.layerdef)
        for layer in selectedoutputlayers:
            lsout.replacelayergeoms(layer,geoms1)
        return lsout

    def binarylayeroperation2(self,function,layers1,layers2,outputlayers):
        layer1 = self.layer_sequence[layers1.pop(0)]
        for layer in layers1:
            layer2 = self.layer_sequence[layer]
            layer1 = layer1.union(layer2)
        layer3 = self.layer_sequence[layers2.pop(0)]

        for layer in layers2:
            layer2 = self.layer_sequence[layer]
            layer3 = layer3.union(layer2)
        layerout = layer1.binaryoperation(layer3,function)       
        
        lsout = Laminate(self.layerdef)
        for layer in outputlayers:
            lsout.replacelayergeoms(layer,layerout.geoms)
        return lsout    

    def select(self,layer):
        return self.layer_sequence[layer]

    def genericfromls(self):
        genericgeometry = {}
        for layer in self.layerdef.layers:
            geometry = self.layer_sequence[layer].geoms
            genericgeoms = []
            for geom in geometry:
                genericgeoms.append(GenericShapeBase.genfromshapely(geom))
            genericgeometry[layer] = genericgeoms
        return genericgeometry
        
