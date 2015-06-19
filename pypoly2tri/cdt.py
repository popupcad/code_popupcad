# -*- coding: utf-8 -*-
'''
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
'''

from pypoly2tri.sweep_context import SweepContext
from pypoly2tri.sweep import Sweep


class CDT(object):

    def __init__(self, polyline):
        self.sweep_context_ = SweepContext(polyline)
        self.sweep_ = Sweep()

    def AddHole(self, polyline):
        self.sweep_context_.AddHole(polyline)

    def AddPoint(self, point):
        self.sweep_context_.AddPoint(point)

    def Triangulate(self):
        self.sweep_.Triangulate(self.sweep_context_)

    def GetTriangles(self):
        return self.sweep_context_.GetTriangles()

    def GetMap(self):
        return self.sweep_context_.GetMap()
