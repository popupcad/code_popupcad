# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from . import customshapely
from .vertex import Vertex

import shapely.geometry
import numpy
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.enum import enum

from .genericshapebase import GenericShapeBase

class GenericLine(GenericShapeBase):
    
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveLine
        return InteractiveLine(self)
    def outputstatic(self,color=None):
        from popupcad.graphics2d.static import StaticLine
        return StaticLine(self,color = color)
    def pickpainterpathfunction(self):
        return self.generatelinepath
    def outputshapely(self):
#        import shapely.geometry
        exterior_p = self.exteriorpoints()
#        interiors_p = self.interiorpoints()
        obj = customshapely.ShapelyLineString(exterior_p)
        return obj
        
class GenericPolyline(GenericShapeBase):
    
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePath
        return InteractivePath(self)
    def outputstatic(self,color=None):
        from popupcad.graphics2d.static import StaticPath
        return StaticPath(self,color = color)
    def pickpainterpathfunction(self):
        return self.generatelinepath
    def outputshapely(self):
#        import shapely.geometry
        exterior_p = self.exteriorpoints()
#        interiors_p = self.interiorpoints()
        obj = customshapely.ShapelyLineString(exterior_p)
        return obj        

class GenericPoly(GenericShapeBase):
    
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePoly
        return InteractivePoly(self)
    def outputstatic(self,color=None):
        from popupcad.graphics2d.static import StaticPoly
        return StaticPoly(self,color = color)
    def pickpainterpathfunction(self):
        return self.generateholeypolypath
    def triangles3(self):
        import popupcad
        cdt = self.toCDT3()
        cdt.Triangulate()
        return [tri.toList() for tri in cdt.GetTriangles()]
#        a = numpy.array([tri.toList() for tri in cdt.GetTriangles()]) /  popupcad.internal_argument_scaling
#        return a.tolist()
    def outputshapely(self):
#        import shapely.geometry
        exterior_p = self.exteriorpoints()
        interiors_p = self.interiorpoints()
        obj = customshapely.ShapelyPolygon(exterior_p,interiors_p)
        return obj
    def addvertex_exterior(self,vertex,special = False):
        if len(self.exterior)>2:
            if special:
                a = [v.getpos() for v in self.exterior]
                b = zip(a,a[1:]+a[:1])
                c = numpy.array(b)
                d = numpy.array(vertex.getpos())
                e = c - d
                f = e.reshape(-1,4)
                g = (f**2).sum(1)
                h = g.argmin()
                self.exterior.insert(h+1,vertex)
                self.update_handles()
                return
        self.exterior.append(vertex)
        self.update_handles()

class GenericCircle(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveCircle
        return InteractiveCircle(self)
    def outputstatic(self,color=None):
        from popupcad.graphics2d.static import StaticCircle
        return StaticCircle(self,color = color)
    def pickpainterpathfunction(self):
        return self.generatecirclepath
    def outputshapely(self):
#        import shapely.geometry
        exterior_p = self.exteriorpoints()
#        interiors_p = self.interiorpoints()
        exterior = numpy.array(exterior_p)
        center = exterior[0]
        v = exterior[1]-exterior[0]
        r = v.dot(v)**.5
        obj = shapely.geometry.Point(*center).buffer(r)
        obj = customshapely.ShapelyPolygon(obj.boundary)
        return obj
        
class GenericTwoPointRect(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveRect2Point
        return InteractiveRect2Point(self)
    def outputstatic(self,color=None):
        from popupcad.graphics2d.static import StaticRect2Point
        return StaticRect2Point(self,color = color)
    def pickpainterpathfunction(self):
        return self.generaterect2pointpath
    def outputshapely(self):
#        import shapely.geometry
        exterior_p = self.exteriorpoints()
#        interiors_p = self.interiorpoints()
        corner1 = exterior_p[0]
        corner2 = (exterior_p[0][0],exterior_p[1][1])
        corner3 = exterior_p[1]
        corner4 = (exterior_p[1][0],exterior_p[0][1])
        corners = [corner1,corner2,corner3,corner4]
        obj = customshapely.ShapelyPolygon(corners)
        return obj