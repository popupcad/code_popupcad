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
            self._controlpoints = self.getcontrolpoints(self.generic_geometry_2d())
            return self._controlpoints

    def controllines(self):
        try:
            return self._controllines
        except AttributeError:
            self._controllines = self.getcontrollines(self.generic_geometry_2d())        
            return self._controllines

    @staticmethod
    def getcontrolpoints(genericgeometry):
        from popupcad.geometry.vertex import TemporaryVertex
        vertices = []
        for layer, geoms in genericgeometry.items():
            for geom in geoms:
                vertices.extend(geom.exteriorpoints())
                [vertices.extend(interior) for interior in geom.interiorpoints()]
        vertices = list(set(vertices))
        controlpoints = []
        for p in vertices:
            v = TemporaryVertex()
            v.setpos(p)
            v.setstatic(True)
            v.set_persistent(True)
            controlpoints.append(v)
        return controlpoints
    
    @staticmethod
    def getcontrollines(genericgeometry):
        lines = []
        from popupcad.geometry.line import Line
        from popupcad.geometry.vertex import TemporaryVertex
        for layer, geoms in genericgeometry.items():
            for geom in geoms:
                newlines = zip(geom.exteriorpoints(),geom.exteriorpoints()[1:]+geom.exteriorpoints()[:1])
                lines.extend(newlines)
                for interior in geom.interiorpoints():
                    newlines = zip(interior,interior[1:]+interior[:1])
                    lines.extend(newlines)
        lines = list(set(lines))
        controllines = []
        for p1,p2 in lines:
            v1 = TemporaryVertex()
            v2 = TemporaryVertex()
            v1.setpos(p1)
            v2.setpos(p2)
            v1.setstatic(True)
            v1.set_persistent(True)
            v2.setstatic(True)
            v2.set_persistent(True)
            controllines.append(Line(v1,v2))
        return controllines
            
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
