# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry import customshapely
from popupcad.geometry.vertex import ShapeVertex

import shapely.geometry
import numpy
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.enum import enum
from popupcad.filetypes.genericfile import popupCADFile
import popupcad

class ShapeInvalid(Exception):
    pass

class NotSimple(Exception):
    pass
    
class GenericShapeBase(popupCADFile):
    filetypes = {'shape':'Shape File'}
    defaultfiletype = 'shape'
    filters,filterstring,selectedfilter = popupCADFile.buildfilters(filetypes,defaultfiletype)

    display = ['construction','exterior','interiors']
    editable = ['construction']
    roundvalue = 5
    tolerance = 10.**-(roundvalue-1)
    shapetypes = enum(line = 'line',polyline = 'polyline',polygon = 'polygon',circle = 'circle',rect2point = 'rect2point')
    deletable = []

    @classmethod
    def lastdir(cls):
        return popupcad.lastshapedir

    @classmethod
    def setlastdir(cls,directory):
        popupcad.lastshapedir = directory

    def isValid(self):
        notempty = len(self.exterior)>0
        return notempty

    def copy(self,identical = True):
        exterior = [vertex.copy(identical) for vertex in self.exterior]
        interiors = [[vertex.copy(identical) for vertex in interior] for interior in self.interiors]
        new = type(self)(exterior,interiors,self.is_construction())
        new.setmoveable(self.is_moveable())
        if identical:
            new.id = self.id

        self.copy_file_params(new,identical)
        
        return new

    def setmoveable(self,test):
        self.moveable = test

    def is_moveable(self):
        try:
            return self.moveable
        except AttributeError:
            self.moveable = True
            return self.moveable

    def is_construction(self):
        try:
            return self.construction
        except AttributeError:
            self.construction = False
            return self.construction

    def exteriorpoints(self):
        return [vertex.getpos() for vertex in self.exterior]        
        
    def interiorpoints(self):
        return [[vertex.getpos() for vertex in interior] for interior in self.interiors]
        
    def vertices(self):
        vertices = self.exterior[:]
        [vertices.extend(interior) for interior in self.interiors]
        return vertices

    def points(self):
        vertices = self.vertices()
        return [vertex.getpos() for vertex in vertices]        

    def loopsegments(self):
        points = self.exterior
        segments = zip(points,points[1:]+points[:1])
        for points in self.interiors:
            segments.extend(zip(points,points[1:]+points[:1]))
        return segments

    def linesegments(self):
        points = self.exterior
        segments = zip(points[:-1],points[1:])
        return segments
        
    def segmentpoints(self):
        segments = self.segments()
        segmentpoints = [(point1.getpos(),point2.getpos()) for point1,point2 in segments]
        return segmentpoints

    def painterpath(self):
        exterior = self.exteriorpoints()
        interiors = self.interiorpoints()
        return self.gen_painterpath(exterior,interiors)
            
    def gen_painterpath(self,exterior,interiors):
        path = qg.QPainterPath()
        return path

    def properties(self):
        from popupcad.widgets.propertyeditor import PropertyEditor
        return PropertyEditor(self)
        
    def __init__(self,exterior,interiors,construction = False,test_shapely = False):
        self.id = id(self)
        self.exterior = exterior
        self.interiors = interiors
        self._basename = self.genbasename()
        self.setmoveable(True)
        
        self.exterior, self.interiors = self.condition_points(self.exterior, self.interiors )

        self.construction = construction
        if test_shapely:
            shapely = self.outputshapely()
            if not shapely.is_simple:
                raise(NotSimple)
            if not shapely.is_valid:
                raise(ShapeInvalid)
        
    def addvertex_exterior(self,vertex,special = False):
        self.exterior.append(vertex)
        self.update_handles()
        
    def removevertex(self,vertex):
        if vertex in self.exterior:
            ii = self.exterior.index(vertex)
            self.exterior.pop(ii)
        for interior in self.interiors:
            if vertex in self.interior:
                ii = interior.index(vertex)
                interior.pop(ii)
        self.update_handles()
    
    def checkedge(self,edge):
        import popupcad.algorithms.points as points
        for pt1,pt2 in zip(edge[:-1],edge[1:]):
            if points.twopointsthesame(pt1,pt2,self.tolerance):
                raise(Exception('points too close together'))

    @classmethod
    def condition_points(cls,exterior,interiors):
        exterior = cls.remove_redundant_points(exterior)
        interiors = [cls.remove_redundant_points(interior) for interior in interiors]
        return exterior,interiors
        
    @classmethod
    def remove_redundant_points(cls,points):
        tests = zip(points,points[1:]+points[0:1])
        newpoints = []
        for point1,point2 in tests:
            if not cls.samepoint(point1.getpos(),point2.getpos()):
                newpoints.append(point1)
        return newpoints

    @classmethod
    def samepoint(cls,point1,point2):
        v = numpy.array(point2)-numpy.array(point1)
        l = v.dot(v)**.5
        return l<cls.tolerance

    @staticmethod
    def buildvertices(exterior_p,interiors_p):
        exterior = GenericShapeBase.buildvertexlist(exterior_p)
        interiors = []
        for interior_p in interiors_p:
            interiors.append(GenericShapeBase.buildvertexlist(interior_p))
        return exterior,interiors

    @staticmethod
    def buildvertexlist(points):
        exterior = []
        for point in points:
            v=ShapeVertex()
            v.setpos(point)
            exterior.append(v)
        return exterior

    @classmethod
    def genfromshapely(cls,obj):
        from popupcad.filetypes.genericshapes import GenericPoly,GenericPolyline
        exterior_p,interiors_p = obj.genpoints_generic()
        exterior,interiors = cls.buildvertices(exterior_p,interiors_p) 
        if isinstance(obj,customshapely.ShapelyPolygon):
            subclass = GenericPoly
        elif isinstance(obj,customshapely.ShapelyLineString):
            subclass= GenericPolyline
        elif isinstance(obj,customshapely.ShapelyPoint):
            from popupcad.geometry.vertex import ShapeVertex, DrawnPoint
            s = DrawnPoint()
            s.setpos(exterior_p[0])
            return s
        else:
            raise(Exception('unknown type'))

        return subclass(exterior,interiors)
        
    @classmethod
    def gengenericpoly(cls,exterior_p,interiors_p,**kwargs):
        from popupcad.filetypes.genericshapes import GenericPoly
        exterior,interiors = cls.buildvertices(exterior_p,interiors_p) 
        return GenericPoly(exterior,interiors,**kwargs)

    def genInteractiveVertices(self):
        try:
            return self._exteriorhandles,self._interiorhandles
        except AttributeError:
            self.update_handles()
            return self._exteriorhandles,self._interiorhandles
        
    def update_handles(self):
        import popupcad.graphics2d.interactivevertex

        try:
            for handle in self._handles:
                handle.harddelete()
        except AttributeError:
            pass

        exterior = [vertex.gen_interactive() for vertex in self.exterior]
        interiors = [[vertex.gen_interactive() for vertex in interior] for interior in self.interiors]

        handles = exterior[:]
        [handles.extend(interior) for interior in interiors]
        self._exteriorhandles = exterior        
        self._interiorhandles = interiors
        self._handles = handles

    def get_handles(self):
        try:
            return self._handles
        except AttributeError:
            self.update_handles()
            return self._handles

    def get_exterior_handles(self):
        try:
            return self._exteriorhandles
        except AttributeError:
            self.update_handles()
            return self._exteriorhandles

    def toCDT3(self):
        from pypoly2tri import Point,CDT
        exterior = [Point(*point) for point in self.exteriorpoints()]
        interiors = [[Point(*point) for point in interior] for interior in self.interiorpoints()]
        cdt = CDT(exterior)
        [cdt.AddHole(interior) for interior in interiors]
        return cdt
    
    def triangles3(self):
        return []

    def lines(self):
        lines = []
        poly = self.exteriorpoints()
        lines.extend(zip(poly,poly[1:]+poly[:1]))
        for poly in self.interiorpoints():
            lines.extend(zip(poly,poly[1:]+poly[0:1]))  
        return lines

    @staticmethod
    def generateQPolygon(points):
        poly = qg.QPolygonF([qc.QPointF(*(point)) for point in numpy.array(points)])
        return poly
            
    def shape_is_equal(self,other):
        if type(self)==type(other):
            if len(self.exterior)==len(other.exterior) and len(self.interiors)==len(other.interiors):
                for point1,point2 in zip(self.exterior,other.exterior):
                    if not point1.is_equal(point2,self.tolerance):
                        return False
                for interior1,interior2 in zip(self.interiors,other.interiors):
                    if len(interior1)!=len(interior2):
                        return False
                    for point1,point2 in zip(interior1,interior2):
                        if not point1.is_equal(point2,self.tolerance):
                            return False
                return True
        return False

    def shift(self,dxdy):
        [item.shift(dxdy) for item in self.exterior]
        [item.shift(dxdy) for interior in self.interiors for item in interior]
