# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry import customshapely
from popupcad.geometry.vertex import Vertex

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
        try:
            self.construction
        except AttributeError:
            self.construction = False
        new = type(self)(exterior,interiors,self.construction)
        if identical:
            new.id = self.id

        self.copy_file_params(new,identical)
        
        return new

    def exteriorpoints(self):
        return [vertex.getpos() for vertex in self.exterior]        
        
    def interiorpoints(self):
        return [[vertex.getpos() for vertex in interior] for interior in self.interiors]
            
    def painterpath(self):
        exterior_p = self.exteriorpoints()
        interiors_p = self.interiorpoints()
        f = self.pickpainterpathfunction()
        return f(exterior_p,interiors_p)

    def properties(self):
        from popupcad.widgets.propertyeditor import PropertyEditor
        return PropertyEditor(self)
        
    def __init__(self,exterior,interiors,construction = False,test_shapely = False):
        self.id = id(self)
        self.exterior = exterior
        self.interiors = interiors
        self._basename = self.genbasename()

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

    def upgrade(self):
        if type(self.exterior[0])!=Vertex:
            self.exterior,self.interiors = self.buildvertices(self.exterior,self.interiors)
                
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
            v=Vertex()
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

        exterior = []
        for vertex in self.exterior:
            iv = popupcad.graphics2d.interactivevertex.InteractiveVertex(vertex)
            iv.updatefromsymbolic()
            exterior.append(iv)

        interiors = []
        for interior in self.interiors:
            interior_out = []
            for vertex in interior:
                iv = popupcad.graphics2d.interactivevertex.InteractiveVertex(vertex)
                iv.updatefromsymbolic()
                interior_out.append(iv)
            interiors.append(interior_out)

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
            
    def generatelinepath(self,exterior,interiors):
        path = qg.QPainterPath()
        path.addPolygon(self.generateQPolygon(exterior))
        return path    

    def generateholeypolypath(self,exterior,interiors):
        path = qg.QPainterPath()
        for item in [exterior]+interiors:
            path.addPolygon(self.generateQPolygon(item))
            path.closeSubpath()
        return path        

    def generatecirclepath(self,exterior,interiors):
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
    
    def generaterect2pointpath(self,exterior,interiors):
        path = qg.QPainterPath()
        points = [qc.QPointF(*point) for point in exterior]
        rect = qc.QRectF(*points)
        path.addRect(rect)
        return path        
    
