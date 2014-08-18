# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.layer import Layer
from popupcad.materials.laminatesheet import Laminate
import popupcad.materials.materials as mat


def one_way_up(laminatein):
    l = Layer([])
    laminateout = Laminate(laminatein.layerdef)
    for ii,geoms in enumerate(laminatein):
        l = l.union(geoms)
        laminateout[ii] =l
    laminateout = modify_up(laminateout)
    return laminateout

def one_way_down(laminatein):
    return one_way_up(laminatein.flip()).flip()

def two_way(laminatein):
    layers = laminatein.layerdef.layers
    laminateout = laminatein.unarylayeroperation('union',layers,layers)
    return laminateout

def modify_up(removabilityin):
#    layers = removabilityin.layerdef.layers
#    for layer1,layer2 in zip(layers[:-1],layers[1:]):
#        if isinstance(layer1,mat.Adhesive) or isinstance(layer2,mat.Adhesive):
#            removabilityin.layer_sequence[layer1] = removabilityin.layer_sequence[layer1].union(removabilityin.layer_sequence[layer2])
    return removabilityin
    