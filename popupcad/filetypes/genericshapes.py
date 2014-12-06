# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry import customshapely

import shapely.geometry
import numpy
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.enum import enum

from popupcad.filetypes.genericshapebase import GenericShapeBase

class GenericLine(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveLine
        return InteractiveLine(self)
    def outputstatic(self,*args,**kwargs):
        from popupcad.graphics2d.static import StaticLine
        return StaticLine(self,*args,**kwargs)
    def gen_painterpath(self,exterior,interiors):
        path = qg.QPainterPath()
        path.addPolygon(self.generateQPolygon(exterior))
        return path    
    def outputshapely(self):
        exterior_p = self.exteriorpoints()
        obj = customshapely.ShapelyLineString(exterior_p)
        return obj
    def segments(self):
        return self.linesegments()
        
class GenericPolyline(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePath
        return InteractivePath(self)
    def outputstatic(self,*args,**kwargs):
        from popupcad.graphics2d.static import StaticPath
        return StaticPath(self,*args,**kwargs)
    def gen_painterpath(self,exterior,interiors):
        path = qg.QPainterPath()
        path.addPolygon(self.generateQPolygon(exterior))
        return path    
    def outputshapely(self):
        exterior_p = self.exteriorpoints()
        obj = customshapely.ShapelyLineString(exterior_p)
        return obj        
    def segments(self):
        return self.linesegments()

class GenericPoly(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePoly
        return InteractivePoly(self)
    def outputstatic(self,*args,**kwargs):
        from popupcad.graphics2d.static import StaticPoly
        return StaticPoly(self,*args,**kwargs)
    def gen_painterpath(self,exterior,interiors):
        path = qg.QPainterPath()
        for item in [exterior]+interiors:
            path.addPolygon(self.generateQPolygon(item))
            path.closeSubpath()
        return path        
    def triangles3(self):
        import popupcad
        cdt = self.toCDT3()
        cdt.Triangulate()
        return [tri.toList() for tri in cdt.GetTriangles()]
    def outputshapely(self):
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
    def segments(self):
        return self.loopsegments()
    def toTriangleFormat(self):
        import shapely.geometry as sg
        import numpy
        vertices = []
        segments = []
        holes = []
        loops = [self.exteriorpoints()]
        ip = self.interiorpoints()
        loops.extend(ip)
        c = 0        
        for loop in loops:
            d = len(vertices)
            vertices.extend(loop)
            a = range(c,c+len(vertices))
            b = zip(a,a[1:]+a[:1])
            segments.extend(b)
            c+=d
            
        for loop in ip:
            p = sg.Polygon(loop)
            e = p.representative_point()
            holes.append((e.x,e.y))            
        tri = {}
        tri['vertices']=numpy.array(vertices)
        tri['segments']=numpy.array(segments)
        if len(holes)>0:
            tri['holes']=numpy.array(holes)
        return tri
    def triangles4(self):
        import triangle
        a = self.toTriangleFormat()
        t = triangle.triangulate(a)
        b = t['vertices'][t['triangles']]        
        return [tri.tolist() for tri in b]

class GenericCircle(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveCircle
        return InteractiveCircle(self)
    def outputstatic(self,*args,**kwargs):
        from popupcad.graphics2d.static import StaticCircle
        return StaticCircle(self,*args,**kwargs)
    def gen_painterpath(self,exterior,interiors):
        path = qg.QPainterPath()
        center = numpy.array(exterior[0])
        edge = numpy.array(exterior[1])
        v = edge- center
        r = v.dot(v)**.5
        point1 = center - r
        point2 = center + r
        point1 = qc.QPointF(*point1)
        point2 = qc.QPointF(*point2)
        rect = qc.QRectF(point1,point2)
        path.addEllipse(rect)        
        return path
    def outputshapely(self):
        exterior_p = self.exteriorpoints()
        exterior = numpy.array(exterior_p)
        center = exterior[0]
        v = exterior[1]-exterior[0]
        r = v.dot(v)**.5
        obj = shapely.geometry.Point(*center).buffer(r)
        obj = customshapely.ShapelyPolygon(obj.boundary)
        return obj
    def segments(self):
        return self.loopsegments()
        
class GenericTwoPointRect(GenericShapeBase):
    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveRect2Point
        return InteractiveRect2Point(self)
    def outputstatic(self,*args,**kwargs):
        from popupcad.graphics2d.static import StaticRect2Point
        return StaticRect2Point(self,*args,**kwargs)
    def gen_painterpath(self,exterior,interiors):
        path = qg.QPainterPath()
        points = [qc.QPointF(*point) for point in exterior]
        rect = qc.QRectF(*points)
        path.addRect(rect)
        return path        
    def outputshapely(self):
        exterior_p = self.exteriorpoints()
        corner1 = exterior_p[0]
        corner2 = (exterior_p[0][0],exterior_p[1][1])
        corner3 = exterior_p[1]
        corner4 = (exterior_p[1][0],exterior_p[0][1])
        corners = [corner1,corner2,corner3,corner4]
        obj = customshapely.ShapelyPolygon(corners)
        return obj
    def segments(self):
        return self.loopsegments()
        