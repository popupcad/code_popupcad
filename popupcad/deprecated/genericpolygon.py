# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry import customshapely

import numpy
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.enum import enum
from popupcad.filetypes.genericshapebase import GenericShapeBase
    
class GenericShape(GenericShapeBase):


    def copy(self,identical = True):
        exterior = [vertex.copy(identical) for vertex in self.exterior]
        interiors = [[vertex.copy(identical) for vertex in interior] for interior in self.interiors]
        try:
            self.construction
        except AttributeError:
            self.construction = False
        new = type(self)(exterior,interiors,self.shapetype,self.construction)
        if identical:
            new.id = self.id
        return new

        
    def pickpainterpathfunction(self):
        if (self.shapetype == self.shapetypes.line) or (self.shapetype == self.shapetypes.polyline):
            return self.generatelinepath
        elif (self.shapetype == self.shapetypes.polygon):
            return self.generateholeypolypath
        elif (self.shapetype == self.shapetypes.circle):
            return self.generatecirclepath
        elif (self.shapetype == self.shapetypes.rect2point):
            return self.generaterect2pointpath
        else:
            raise(Exception('no path defined for this type'))        
    
    def __init__(self,exterior,interiors,shapetype,construction = False,test_shapely = False):
        from popupcad.filetypes.genericshapebase import NotSimple,ShapeInvalid
        self.id = id(self)
        self.exterior = exterior
        self.interiors = interiors
        self.shapetype = shapetype
        self._basename = self.genbasename()

        self.exterior, self.interiors = self.condition_points(self.exterior, self.interiors )

        self.construction = construction
        if test_shapely:
            shapely = self.outputshapely()
            if not shapely.is_simple:
                raise(NotSimple)
            if not shapely.is_valid:
                raise(ShapeInvalid)
        
    def addvertex_exterior(self,vertex):
        self.exterior.append(vertex)
        self.update_handles()
        

    @staticmethod
    def buildvertices(exterior_p,interiors_p):
        exterior = GenericShape.buildvertexlist(exterior_p)
        interiors = []
        for interior_p in interiors_p:
            interiors.append(GenericShape.buildvertexlist(interior_p))
        return exterior,interiors


    @classmethod
    def genfromshapely(cls,obj):
        exterior_p,interiors_p = obj.genpoints_generic()
        exterior,interiors = cls.buildvertices(exterior_p,interiors_p) 
        if isinstance(obj,customshapely.ShapelyPolygon):
            shapetype = cls.shapetypes.polygon
        elif isinstance(obj,customshapely.ShapelyLineString):
            shapetype = cls.shapetypes.polyline
        else:
            raise(Exception('unknown type'))

        return cls(exterior,interiors,shapetype)
        
    @classmethod
    def gengenericpoly(cls,exterior_p,interiors_p,**kwargs):
        exterior,interiors = cls.buildvertices(exterior_p,interiors_p) 
        shapetype = cls.shapetypes.polygon
        return cls(exterior,interiors,shapetype,**kwargs)

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePath,InteractivePoly,InteractiveLine,InteractiveCircle,InteractiveRect2Point
        
        if self.shapetype==self.shapetypes.line:
            drawableclass = InteractiveLine
        elif self.shapetype==self.shapetypes.polyline:
            drawableclass = InteractivePath
        elif self.shapetype==self.shapetypes.polygon:
            drawableclass = InteractivePoly
        elif self.shapetype==self.shapetypes.circle:
            drawableclass = InteractiveCircle
        elif self.shapetype==self.shapetypes.rect2point:
            drawableclass = InteractiveRect2Point
        else:
            raise(Exception('unknown type'))
        
        drawable = drawableclass(self)
        return drawable

    def outputstatic(self,color=None):
        from popupcad.graphics2d.static import StaticPoly,StaticPath,StaticLine,StaticCircle,StaticRect2Point
        if self.shapetype==self.shapetypes.line:
            staticclass = StaticLine
        elif self.shapetype==self.shapetypes.polyline:
            staticclass = StaticPath
        elif self.shapetype==self.shapetypes.polygon:
            staticclass = StaticPoly
        elif self.shapetype==self.shapetypes.circle:
            staticclass = StaticCircle
        elif self.shapetype==self.shapetypes.rect2point:
            staticclass = StaticRect2Point            
        else:
            raise(Exception('unknown type'))

        drawable = staticclass(self,color = color)
        return drawable    

    def outputshapely(self):
        import shapely.geometry

        exterior_p = self.exteriorpoints()
        interiors_p = self.interiorpoints()

        if self.shapetype==self.shapetypes.line:
            obj = customshapely.ShapelyLineString(exterior_p)
        elif self.shapetype==self.shapetypes.polyline:
            obj = customshapely.ShapelyLineString(exterior_p)
        elif self.shapetype==self.shapetypes.polygon:
            obj = customshapely.ShapelyPolygon(exterior_p,interiors_p)
        elif self.shapetype==self.shapetypes.circle:
            exterior = numpy.array(exterior_p)
            center = exterior[0]
            v = exterior[1]-exterior[0]
            r = v.dot(v)**.5
            obj = shapely.geometry.Point(*center).buffer(r)
            obj = customshapely.ShapelyPolygon(obj.boundary)
        elif self.shapetype==self.shapetypes.rect2point:
            corner1 = exterior_p[0]
            corner2 = (exterior_p[0][0],exterior_p[1][1])
            corner3 = exterior_p[1]
            corner4 = (exterior_p[1][0],exterior_p[0][1])
            corners = [corner1,corner2,corner3,corner4]
            obj = customshapely.ShapelyPolygon(corners)
        else:
            raise(Exception('unknown type'))

        return obj

    def toCDT2(self):
        from p2t import Point,CDT
        exterior = [Point(*point) for point in self.exteriorpoints()]
        interiors = [[Point(*point) for point in interior] for interior in self.interiorpoints()]
        cdt = CDT(exterior)
        [cdt.add_hole(interior) for interior in interiors]
        return cdt

    def toCDT3(self):
        from pypoly2tri import Point,CDT
        exterior = [Point(*point) for point in self.exteriorpoints()]
        interiors = [[Point(*point) for point in interior] for interior in self.interiorpoints()]
        cdt = CDT(exterior)
        [cdt.AddHole(interior) for interior in interiors]
        return cdt
        
    def triangles3(self):
        if self.shapetype==self.shapetypes.polygon:
            cdt = self.toCDT3()
            cdt.Triangulate()
            return [tri.toList() for tri in cdt.GetTriangles()]
        else:
            return []
            
    def lines(self):
        lines = []
        poly = self.exteriorpoints()
        lines.extend(zip(poly,poly[1:]+poly[:1]))
        for poly in self.interiorpoints():
            lines.extend(zip(poly,poly[1:]+poly[0:1]))  
        return lines


GenericDrawable = GenericShape
GenericPolygon = GenericShape

