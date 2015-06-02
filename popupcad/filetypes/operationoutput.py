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
            self._generic_geometry_2d = self.csg.to_generic_laminate().geoms
            return self._generic_geometry_2d

    def controlpoints(self):
        try:
            return self._controlpoints
        except AttributeError:
            self.update_controls()
            return self._controlpoints

    def controllines(self):
        try:
            return self._controllines
        except AttributeError:
            self.update_controls()
            return self._controllines

    def controlpolygons(self):
        try:
            return self._control_polygons
        except AttributeError:
            self.update_controls()
            return self._control_polygons

    def update_controls(self):
        self._controlpoints, self._controllines,self._control_polygons = self.getcontrols(self.generic_geometry_2d())
        
    @staticmethod
    def getcontrols(genericgeometry):
        from popupcad.geometry.line import ReferenceLine
        from popupcad.geometry.vertex import ReferenceVertex
        vertices = []
        unique_geoms = []
        all_geoms = []
        lines = []
        for layer, geoms in genericgeometry.items():
            all_geoms.extend(geoms)
            for geom in geoms:
                p = geom.points()
                vertices.extend(p)
                lines.extend(geom.segmentpoints())

        for geom in all_geoms:
            is_unique = True
            for geom2 in unique_geoms:
                if geom.shape_is_equal(geom2):
                    is_unique = False
                    break
            if is_unique:
                unique_geoms.append(geom)
            

        vertices = list(set(vertices))
        controlpoints = [ReferenceVertex(position = p) for p in vertices]

        lines = list(set(lines))
        lines2 = [(vertices.index(p1),vertices.index(p2)) for p1,p2 in lines]
        controllines = [ReferenceLine(controlpoints[ii],controlpoints[jj]) for ii,jj in lines2]
        return controlpoints, controllines, unique_geoms
            
    def edit(self,*args,**kwargs):
        if self.parent !=None:
            self.parent.edit(*args,**kwargs)

    def display_geometry_2d(self):
        try:
            return self._display_geometry_2d
        except AttributeError:
            self._display_geometry_2d = {}
            for layer,geometry in self.generic_geometry_2d().items():
                displaygeometry = [geom.outputstatic(brush_color = layer.color) for geom in geometry]
                self._display_geometry_2d[layer] = displaygeometry
            return self._display_geometry_2d

    def tris(self):
        import popupcad.algorithms.points as points
        try:
            return self.alltriangles
        except AttributeError:
            self.alltriangles = {}
            for layer,geoms in self.generic_geometry_2d().items():
                triangles = []
                for geom in geoms:
                    try:
                        triangles.extend(geom.triangles3())
                    except AttributeError:
                        pass
                self.alltriangles[layer] = triangles
            return self.alltriangles
