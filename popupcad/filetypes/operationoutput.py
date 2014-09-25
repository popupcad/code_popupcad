# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.userdata import UserData
import popupcad
import numpy

class OperationOutput(UserData):
    def __init__(self,csg,name,parent = None):
        super(OperationOutput,self).__init__()
        self.csg = csg
        self.name = name
        self.parent = parent
        
    def generic_geometry_2d(self):        
        try:
            return self._generic_geometry_2d
        except AttributeError:
            self._generic_geometry_2d = self.csg.genericfromls()
            return self._generic_geometry_2d

    def controlpoints(self):
        try:
            return self._controlpoints
        except AttributeError:
            self._controlpoints, self._controllines = self.getcontrols(self.generic_geometry_2d())
            return self._controlpoints

    def controllines(self):
        try:
            return self._controllines
        except AttributeError:
            self._controlpoints, self._controllines = self.getcontrols(self.generic_geometry_2d())
            return self._controllines

    @staticmethod
    def getcontrols(genericgeometry):
        lines = []
        from popupcad.geometry.line import ReferenceLine
        from popupcad.geometry.vertex import ReferenceVertex
        vertices = []
        for layer, geoms in genericgeometry.items():
            for geom in geoms:
                p = geom.exteriorpoints()
                vertices.extend(p)
                lines.extend(zip(p,p[1:]+p[:1]))
                for interior in geom.interiorpoints():
                    vertices.extend(interior)
                    lines.extend(zip(interior,interior[1:]+interior[:1]))

        vertices = list(set(vertices))
        controlpoints = [ReferenceVertex(position = p) for p in vertices]

        lines = list(set(lines))
        lines2 = [(vertices.index(p1),vertices.index(p2)) for p1,p2 in lines]
        controllines = [ReferenceLine(controlpoints[ii],controlpoints[jj]) for ii,jj in lines2]
        return controlpoints, controllines
            
    def edit(self,*args,**kwargs):
        if self.parent !=None:
            self.parent.edit(*args,**kwargs)

    def display_geometry_2d(self):
        try:
            return self._display_geometry_2d
        except AttributeError:
            self._display_geometry_2d = {}
            for layer,geometry in self.generic_geometry_2d().items():
                displaygeometry = [geom.outputstatic(color = layer.color) for geom in geometry]
                self._display_geometry_2d[layer] = displaygeometry
            return self._display_geometry_2d

    def tris(self):
        import popupcad.algorithms.points as points
        try:
            return self.alltriangles
        except AttributeError:
            self.alltriangles = {}
            for layer,geoms in self.generic_geometry_2d().items():
                triangles = [tri for geom in geoms for tri in geom.triangles3()]
                self.alltriangles[layer] = triangles
            return self.alltriangles

    def lines(self):
        import popupcad.algorithms.points as points
        try:
            return self.allines
        except AttributeError:
            self.allines = {}
            for layer,geoms in self.generic_geometry_2d().items():
                linesegments = [item for geom in geoms for item in geom.lines()]
                glformat = [point for segment in linesegments for point in segment]
                self.allines[layer] = glformat
            return self.allines
