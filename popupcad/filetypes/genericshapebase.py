
# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry import customshapely
from popupcad.geometry.vertex import ShapeVertex

import numpy
import PySide.QtCore as qc
import PySide.QtGui as qg
from dev_tools.enum import enum
from popupcad.filetypes.popupcad_file import popupCADFile
import popupcad


class ShapeInvalid(Exception):
    pass


class NotSimple(Exception):
    pass


class GenericShapeBase(popupCADFile):
    filetypes = {'shape': 'Shape File'}
    defaultfiletype = 'shape'

    display = ['construction', 'exterior', 'interiors']
    editable = ['construction']
    roundvalue = 5
    tolerance = 10.**-(roundvalue - 1)
    shapetypes = enum(
        line='line',
        polyline='polyline',
        polygon='polygon',
        circle='circle',
        rect2point='rect2point')
    deletable = []

    def __init__(
            self,
            exterior,
            interiors,
            construction=False,
            test_shapely=False):
        super(GenericShapeBase, self).__init__()
        self.exterior = exterior
        self.interiors = interiors

        self.exterior, self.interiors = self.condition_points(
            self.exterior, self.interiors)

        self.construction = construction

    def is_valid(self):
        shapely = self.outputshapely()
        if not shapely.is_simple:
            raise(NotSimple)
        if not shapely.is_valid:
            raise(ShapeInvalid)

    @classmethod
    def lastdir(cls):
        return popupcad.lastshapedir

    @classmethod
    def setlastdir(cls, directory):
        popupcad.lastshapedir = directory

    def isValid(self):
        notempty = len(self.get_exterior()) > 0
        return notempty

    def copy_data(self, new_type, identical=True):
        exterior = [vertex.copy(identical) for vertex in self.get_exterior()]
        interiors = [[vertex.copy(identical) for vertex in interior]
                     for interior in self.get_interiors()]
        new = new_type(exterior, interiors, self.is_construction())
        if identical:
            new.id = self.id
        self.copy_file_params(new, identical)
        return new

    def copy(self, identical=True):
        return self.copy_data(type(self), identical)

    def upgrade(self, identical=True):
        exterior = [vertex.upgrade(identical)
                    for vertex in self.get_exterior()]
        interiors = [[vertex.upgrade(
            identical) for vertex in interior] for interior in self.get_interiors()]
        new = type(self)(exterior, interiors, self.is_construction())
        if identical:
            new.id = self.id
        self.copy_file_params(new, identical)
        return new

    def get_exterior(self):
        return self.exterior

    def get_interiors(self):
        return self.interiors

    def is_construction(self):
        try:
            return self.construction
        except AttributeError:
            self.construction = False
            return self.construction

    def exteriorpoints(self, scaling=1):
        return [vertex.getpos(scaling) for vertex in self.get_exterior()]

    def interiorpoints(self, scaling=1):
        return [[vertex.getpos(scaling) for vertex in interior]
                for interior in self.get_interiors()]

    def vertices(self):
        vertices = self.get_exterior()[:]
        [vertices.extend(interior) for interior in self.get_interiors()]
        return vertices

    def points(self, scaling=1):
        return [vertex.getpos(scaling) for vertex in self.vertices()]

    def segments_closed(self):
        points = self.get_exterior()
        segments = list(zip(points, points[1:] + points[:1]))
        for points in self.get_interiors():
            segments.extend(list(zip(points, points[1:] + points[:1])))
        return segments

    def segments_open(self):
        points = self.get_exterior()
        segments = list(zip(points[:-1], points[1:]))
        for points in self.get_interiors():
            segments.extend(list(zip(points[:-1], points[1:])))
        return segments

    def segmentpoints(self, scaling=1):
        segments = self.segments()
        segmentpoints = [
            (point1.getpos(scaling),
             point2.getpos(scaling)) for point1,
            point2 in segments]
        return segmentpoints

    def painterpath(self):
        exterior = self.exteriorpoints(scaling=popupcad.view_scaling)
        interiors = self.interiorpoints(scaling=popupcad.view_scaling)
        return self.gen_painterpath(exterior, interiors)

    def gen_painterpath(self, exterior, interiors):
        path = qg.QPainterPath()
        return path

    def properties(self):
        from dev_tools.propertyeditor import PropertyEditor
        return PropertyEditor(self)

    def addvertex_exterior(self, vertex, special=False):
        self.exterior.append(vertex)
        self.update_handles()

    def removevertex(self, vertex):
        if vertex in self.exterior:
            ii = self.exterior.index(vertex)
            self.exterior.pop(ii)
        for interior in self.interiors:
            if vertex in self.interior:
                ii = interior.index(vertex)
                interior.pop(ii)
        self.update_handles()

    def checkedge(self, edge):
        import popupcad.algorithms.points as points
        for pt1, pt2 in zip(edge[:-1], edge[1:]):
            if points.twopointsthesame(pt1, pt2, self.tolerance):
                raise Exception

    @classmethod
    def condition_points(cls, exterior, interiors):
        exterior = cls.remove_redundant_points(exterior)
        interiors = [
            cls.remove_redundant_points(interior) for interior in interiors]
        return exterior, interiors

    @classmethod
    def remove_redundant_points(cls, points, scaling=1):
        newpoints = []
        for point1, point2 in zip(points, points[1:] + points[0:1]):
            if not cls.samepoint(
                    point1.getpos(scaling),
                    point2.getpos(scaling)):
                newpoints.append(point1)
        return newpoints

    @classmethod
    def samepoint(cls, point1, point2):
        v = numpy.array(point2) - numpy.array(point1)
        l = v.dot(v)**.5
        return l < cls.tolerance

    @staticmethod
    def buildvertices(exterior_p, interiors_p):
        exterior = GenericShapeBase.buildvertexlist(exterior_p)
        interiors = []
        for interior_p in interiors_p:
            interiors.append(GenericShapeBase.buildvertexlist(interior_p))
        return exterior, interiors

    @staticmethod
    def buildvertexlist(points):
        exterior = []
        for point in points:
            v = ShapeVertex()
            v.setpos(point)
            exterior.append(v)
        return exterior

    @classmethod
    def genfromshapely(cls, obj):
        from popupcad.filetypes.genericshapes import GenericPoly, GenericPolyline
        exterior_p, interiors_p = obj.genpoints_generic()
        exterior, interiors = cls.buildvertices(exterior_p, interiors_p)
        if isinstance(obj, customshapely.ShapelyPolygon):
            subclass = GenericPoly
        elif isinstance(obj, customshapely.ShapelyLineString):
            subclass = GenericPolyline
        elif isinstance(obj, customshapely.ShapelyPoint):
            from popupcad.geometry.vertex import DrawnPoint
            s = DrawnPoint()
            s.setpos(exterior_p[0])
            return s
        else:
            raise Exception

        return subclass(exterior, interiors)

    @classmethod
    def gen_from_point_lists(cls, exterior_p, interiors_p, **kwargs):
        exterior, interiors = cls.buildvertices(exterior_p, interiors_p)
        return cls(exterior, interiors, **kwargs)

    def genInteractiveVertices(self):
        try:
            return self._exteriorhandles, self._interiorhandles
        except AttributeError:
            self.update_handles()
            return self._exteriorhandles, self._interiorhandles

    def update_handles(self):
        try:
            for handle in self._handles:
                handle.harddelete()
        except AttributeError:
            pass

        exterior = [vertex.gen_interactive() for vertex in self.get_exterior()]
        interiors = [[vertex.gen_interactive() for vertex in interior]
                     for interior in self.get_interiors()]

        handles = exterior[:]
        [handles.extend(interior) for interior in interiors]
        self._exteriorhandles = exterior
        self._interiorhandles = interiors
        self._handles = handles

    def len_exterior(self):
        return len(self.get_exterior())

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

    def triangles3(self):
        return []

    @staticmethod
    def generateQPolygon(points):
        poly = qg.QPolygonF([qc.QPointF(*(point))
                             for point in numpy.array(points)])
        return poly

    def shape_is_equal(self, other):
        if isinstance(self, type(other)):
            if len(
                self.get_exterior()) == len(
                other.get_exterior()) and len(
                self.get_interiors()) == len(
                    other.get_interiors()):
                for point1, point2 in zip(
                        self.get_exterior(), other.get_exterior()):
                    if not point1.is_equal(point2, self.tolerance):
                        return False
                for interior1, interior2 in zip(
                        self.get_interiors(), other.get_interiors()):
                    if len(interior1) != len(interior2):
                        return False
                    for point1, point2 in zip(interior1, interior2):
                        if not point1.is_equal(point2, self.tolerance):
                            return False
                return True
        return False

    def shift(self, dxdy):
        [item.shift(dxdy) for item in self.get_exterior()]
        [item.shift(dxdy) for interior in self.get_interiors()
         for item in interior]

    def constrained_shift(self, dxdy, constraintsystem):
        a = [(item, dxdy) for item in self.get_exterior()]
        a.extend([(item, dxdy) for interior in self.get_interiors()
                  for item in interior])
        constraintsystem.constrained_shift(a)

    def flip(self):
        self.exterior = self.get_exterior()[::-1]
        self.interiors = [interior[::-1] for interior in self.get_interiors()]

    def hollow(self):
        return self

    def fill(self):
        return self

    def insert_exterior_vertex(self, ii, vertex):
        self.exterior.insert(ii, vertex)

    def append_exterior_vertex(self, vertex):
        self.exterior.append(vertex)
