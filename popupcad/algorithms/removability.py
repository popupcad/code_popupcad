# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.layer import Layer
from popupcad.materials.laminatesheet import Laminate


def one_way_up(laminatein):
    l = Layer([])
    laminateout = Laminate(laminatein.layerdef)
    for ii,geoms in enumerate(laminatein):
        l = l.union(geoms)
        laminateout[ii] =l
    return laminateout

def one_way_down(laminatein):
    return one_way_up(laminatein.flip()).flip()

def two_way(laminatein):
    layers = laminatein.layerdef.layers
    laminateout = laminatein.unarylayeroperation('union',layers,layers)
    return laminateout
