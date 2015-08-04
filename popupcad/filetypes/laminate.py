# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.layer import Layer
import popupcad


class IterableLaminate(object):

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.layer_sequence[self.layerdef.layers[index]]
        elif isinstance(index, slice):
            return [self.layer_sequence[layer]
                    for layer in self.layerdef.layers[index]]

    def __setitem__(self, index, v):
        if isinstance(index, int):
            if isinstance(v, Layer):
                v = v.geoms
            self.layer_sequence[self.layerdef.layers[index]] = Layer(v)
        elif isinstance(index, slice):
            for value, layer in zip(v, self.layerdef.layers[index]):
                if isinstance(value, Layer):
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

    def __init__(self, layerdef):
        self.layerdef = layerdef
        self.layer_sequence = {}
        for layer in self.layerdef.layers:
            self.replacelayergeoms(layer, [])

    def copy(self):
        new = type(self)(self.layerdef)
        new.layer_sequence = self.layer_sequence.copy()

    def upgrade(self, *args, **kwargs):
        return self

    def layers(self):
        return self.layerdef.layers

    def isEmpty(self):
        return all([layer.isEmpty() for layer in self.layer_sequence.values()])

    def replacelayergeoms(self, layer, geoms):
        self.layer_sequence[layer] = Layer(geoms)

    def insertlayergeoms(self, layer, geoms):
        self.layer_sequence[layer].add_geoms(geoms)

    def getlayer(self, ref):
        return self.layerdef.getlayer(ref)

    def union(self, ls2):
        return self.binaryoperation(ls2, 'union')

    def difference(self, ls2):
        return self.binaryoperation(ls2, 'difference')

    def intersection(self, ls2):
        return self.binaryoperation(ls2, 'intersection')

    def symmetric_difference(self, ls2):
        return self.binaryoperation(ls2, 'symmetric_difference')

    def buffer(self, value, **kwargs):
        if not 'resolution' in kwargs:
            kwargs['resolution'] = popupcad.default_buffer_resolution
        return self.valueoperation('buffer', value, **kwargs)

    def cleanup(self, value):
        return popupcad.algorithms.morphology.cleanup(
            self,
            value,
            resolution=1)

    def simplify(self, tolerance, **kwargs):
        return self.valueoperation('simplify',tolerance,preserve_topology=True)

    def binaryoperation(self, ls2, function):
        self = self
        lsout = Laminate(self.layerdef)
        layers = self.layerdef.layers
        if self.layerdef != ls2.layerdef:
            raise Exception
        for layer in layers:
            layer1 = self.layer_sequence[layer]
            layer2 = ls2.layer_sequence[layer]
            layerout = layer1.binaryoperation(layer2, function)
            lsout.replacelayergeoms(layer, layerout.geoms)
        return lsout

    @staticmethod
    def unaryoperation(laminates, function):
        laminates = laminates[:]
        lsout = laminates.pop(0)
        while not not laminates:
            lsout = lsout.binaryoperation(laminates.pop(0), function)
        return lsout

    def valueoperation(self, functionname, value, **kwargs):
        lsout = Laminate(self.layerdef)
        layers = self.layerdef.layers
        for layer in layers:
            layer1 = self.layer_sequence[layer]
            result = layer1.valueoperation(functionname, value, **kwargs)
            lsout.replacelayergeoms(layer, result.geoms)
        return lsout

    def unarylayeroperation(
            self,
            functionname,
            selectedinputlayers,
            selectedoutputlayers):
        selectedinputlayers = selectedinputlayers[:]
        layer1 = self.layer_sequence[selectedinputlayers.pop(0)]
        for layer in selectedinputlayers:
            layer2 = self.layer_sequence[layer]
            layer1 = layer1.binaryoperation(layer2, functionname)
        result = popupcad.algorithms.csg_shapely.unary_union_safe(layer1.geoms)
        geoms1 = popupcad.algorithms.csg_shapely.condition_shapely_entities(result)
        lsout = Laminate(self.layerdef)
        for layer in selectedoutputlayers:
            lsout.replacelayergeoms(layer, geoms1)
        return lsout

    def binarylayeroperation2(self, function, layers1, layers2, outputlayers):
        layer1 = self.layer_sequence[layers1.pop(0)]
        for layer in layers1:
            layer2 = self.layer_sequence[layer]
            layer1 = layer1.union(layer2)
        layer3 = self.layer_sequence[layers2.pop(0)]

        for layer in layers2:
            layer2 = self.layer_sequence[layer]
            layer3 = layer3.union(layer2)
        layerout = layer1.binaryoperation(layer3, function)

        lsout = Laminate(self.layerdef)
        for layer in outputlayers:
            lsout.replacelayergeoms(layer, layerout.geoms)
        return lsout

    def select(self, layer):
        return self.layer_sequence[layer]

    def to_generic_laminate(self):
        from popupcad.filetypes.genericlaminate import GenericLaminate
        genericgeometry = {}
        for layer in self.layerdef.layers:
            geometry = self.layer_sequence[layer].geoms
            genericgeoms = []
            for geom in geometry:
                genericgeoms.append(popupcad.algorithms.csg_shapely.to_generic(geom))
            genericgeometry[layer] = genericgeoms
        new = GenericLaminate(self.layerdef, genericgeometry)
        return new

    def switch_layer_defs(self,layerdef_to):
        new = Laminate(layerdef_to)
        for layer_from, layer_to in zip(self.layerdef.layers,layerdef_to.layers):
            new.layer_sequence[layer_to] = self.layer_sequence[layer_from]
        return new
        
    def all_geoms(self):
        allgeoms = []
        for layer in self.layerdef.layers:
            allgeoms.extend(self.layer_sequence[layer])
        return allgeoms
        
    def __lt__(self,other):
        return self.all_geoms()[0]<other.all_geoms()[1]
        