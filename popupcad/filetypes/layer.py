# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import shapely.geometry as sg
import popupcad


class Layer(object):

    def __init__(self, geoms):
        self.geoms = geoms

    def union(self, layer):
        return self.binaryoperation(layer, 'union')

    def difference(self, layer):
        return self.binaryoperation(layer, 'difference')

    def intersection(self, layer):
        return self.binaryoperation(layer, 'intersection')

    def symmetric_difference(self, layer):
        return self.binaryoperation(layer, 'symmetric_difference')

    def buffer(self, value, **kwargs):
        if not 'resolution' in kwargs:
            kwargs['resolution'] = popupcad.default_buffer_resolution
        return self.valueoperation('buffer', value, **kwargs)

    def add_geoms(self, geoms):
        self.geoms.extend(geoms)

    def promote(self, layerdef):
        from popupcad.filetypes.laminate import Laminate
        lsout = Laminate(layerdef)
        for layer in layerdef.layers:
            lsout.replacelayergeoms(layer, self.geoms)
        return lsout

    @classmethod
    def unary_union(cls, layers):
        geoms = [geom for layer in layers for geom in layer.geoms]
        result1 = popupcad.algorithms.csg_shapely.unary_union_safe(geoms)
        result2 = popupcad.algorithms.csg_shapely.condition_shapely_entities(result1)
        return cls(result2)

    def binaryoperation(self, layer2, functionname):
        sourcegeoms = self.geoms
        operationgeoms = layer2.geoms

        if sourcegeoms == []:
            sourcegeom = sg.Polygon()
        else:
            sourcegeom = popupcad.algorithms.csg_shapely.unary_union_safe(sourcegeoms)

        if operationgeoms == []:
            operationgeom = sg.Polygon()
        else:
            operationgeom = popupcad.algorithms.csg_shapely.unary_union_safe(operationgeoms)

        function = getattr(sourcegeom, functionname)
        newgeom = function(operationgeom)

        result1 = popupcad.algorithms.csg_shapely.unary_union_safe([newgeom])
        result2 = popupcad.algorithms.csg_shapely.condition_shapely_entities(result1)
        return type(self)(result2)

    def valueoperation(self, functionname, *args, **kwargs):
        sourcegeoms = self.geoms

        if sourcegeoms == []:
            sourcegeom = sg.Polygon()
        else:
            sourcegeom = popupcad.algorithms.csg_shapely.unary_union_safe(sourcegeoms)

        function = getattr(sourcegeom, functionname)
        newgeom = function(*args, **kwargs)
        result1 = popupcad.algorithms.csg_shapely.unary_union_safe([newgeom])
        result2 = popupcad.algorithms.csg_shapely.condition_shapely_entities(result1)
        return type(self)(result2)

    def isEmpty(self):
        return len(self.geoms) == 0
