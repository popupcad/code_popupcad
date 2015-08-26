# -*- coding: utf-8 -*-
'''
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
'''

#from enum import Enum
import math


def enum(**enums):
    return type('Enum', (), enums)

PI_3div4 = 3 * math.pi / 4
EPSILON = 1e-12
Orientation = enum(CW=101, CCW=102, COLLINEAR=103)


def Orient2d(pa, pb, pc):
    detleft = (pa.x - pc.x) * (pb.y - pc.y)
    detright = (pa.y - pc.y) * (pb.x - pc.x)
    val = detleft - detright

    if val > -EPSILON and val < EPSILON:
        return Orientation.COLLINEAR
    elif val > 0:
        return Orientation.CCW

    return Orientation.CW


def InScanArea(pa, pb, pc, pd):
    pdx = pd.x
    pdy = pd.y
    adx = pa.x - pdx
    ady = pa.y - pdy
    bdx = pb.x - pdx
    bdy = pb.y - pdy

    adxbdy = adx * bdy
    bdxady = bdx * ady
    oabd = adxbdy - bdxady
    if oabd <= EPSILON:
        return False

    cdx = pc.x - pdx
    cdy = pc.y - pdy
    cdxady = cdx * ady
    adxcdy = adx * cdy
    ocad = cdxady - adxcdy

    if ocad <= EPSILON:
        return False

    return True
