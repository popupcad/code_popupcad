# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.laminate import Laminate
from popupcad.algorithms.keepout import laserkeepout, millkeepout, millflipkeepout


def laserclearance(laminatein):
    return laserkeepout(laminatein)


def millclearance(laminatein):
    l1 = laserkeepout(laminatein)
    l2 = millkeepout(laminatein)
    l3 = l1.difference(l2)
    return l3


def millflipclearance(laminatein):
    l1 = laserkeepout(laminatein)
    l2 = millflipkeepout(laminatein)
    l3 = l1.difference(l2)
    return l3
