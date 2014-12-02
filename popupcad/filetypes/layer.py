# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import shapely.ops as so
import popupcad.geometry.customshapely as customshapely
import shapely.geometry as sg

class Layer(object):
    def __init__(self,geoms):
        self.geoms = geoms

    def union(self,layer):
        return self.binaryoperation(layer,'union')        
    def difference(self,layer):
        return self.binaryoperation(layer,'difference')        
    def intersection(self,layer):
        return self.binaryoperation(layer,'intersection')        
    def symmetric_difference(self,layer):
        return self.binaryoperation(layer,'symmetric_difference') 
    def buffer(self,value,**kwargs):
        if not 'resolution' in kwargs:
            kwargs['resolution'] = popupcad.default_buffer_resolution
        return self.valueoperation('buffer',value,**kwargs) 

    def add_geoms(self,geoms):
        self.geoms.extend(geoms)

    def promote(self,layerdef):
        lsout = Laminate(layerdef)
        for layer in layerdef.layers:
            lsout.replacelayergeoms(layer,self.geoms)
        return lsout
        
    def binaryoperation(self,layer2,functionname):
        sourcegeoms = self.geoms
        operationgeoms = layer2.geoms

        if sourcegeoms ==[]:
            sourcegeom = sg.Polygon()
        else:
            sourcegeom = customshapely.unary_union_safe(sourcegeoms)

        if operationgeoms ==[]:
            operationgeom = sg.Polygon()
        else:
            operationgeom = customshapely.unary_union_safe(operationgeoms)

        function = getattr(sourcegeom,functionname)
        newgeom = function(operationgeom)

        result = customshapely.unary_union_safe([newgeom])
        return type(self)(customshapely.multiinit(result))

    def valueoperation(self,functionname,*args,**kwargs):
        sourcegeoms  = self.geoms

        if sourcegeoms ==[]:
            sourcegeom = sg.Polygon()
        else:
            sourcegeom = customshapely.unary_union_safe(sourcegeoms)

        function = getattr(sourcegeom,functionname)
        newgeom = function(*args,**kwargs)
        result = customshapely.unary_union_safe([newgeom])
        return type(self)(customshapely.multiinit(result))

    def isEmpty(self):
        return len(self.geoms)==0