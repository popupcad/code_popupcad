# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.laminate import Laminate


def laserkeepout(laminatein):
    '''calculate the keepout for an input laminate assuming laser cutting'''
    layers = laminatein.layerdef.layers
    laminateout = laminatein.unarylayeroperation('union', layers, layers)
    return laminateout


def millkeepout(laminatein):
    '''calculate the keepout for an input laminate assuming milling'''
    l = Layer([])
    laminateout = Laminate(laminatein.layerdef)
    for ii, geoms in enumerate(laminatein[::-1]):
        l = l.union(geoms)
        laminateout[-1 - ii] = l
    return laminateout


def millflipkeepout(laminatein):
    '''calculate the keepout for an input laminate assuming milling & part flipping'''
    l1 = millkeepout(laminatein)
    l2 = millkeepout(laminatein.flip()).flip()
    lout = l1.intersection(l2)
    return lout
