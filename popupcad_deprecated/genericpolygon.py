# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""


import numpy
from popupcad.filetypes.genericshapebase import GenericShapeBase
from popupcad.filetypes.genericshapes import GenericCircle, GenericLine, GenericPoly, GenericPolyline, GenericTwoPointRect


class GenericShape(GenericShapeBase):

    def __init__(
            self,
            exterior,
            interiors,
            shapetype,
            construction=False,
            test_shapely=False):
        from popupcad.filetypes.genericshapebase import NotSimple, ShapeInvalid
        self.id = id(self)
        self.exterior = exterior
        self.interiors = interiors
        self.shapetype = shapetype
        self._basename = self.genbasename()

        self.exterior = self.remove_redundant_points(self.exterior)
        self.interiors = [self.remove_redundant_points(interior) for interior in self.interiors]

        self.construction = construction
        if test_shapely:
            shapely = self.to_shapely()
            if not shapely.is_simple:
                raise(NotSimple)
            if not shapely.is_valid:
                raise(ShapeInvalid)

    def copy(self, identical=True):
        exterior = [vertex.copy(identical) for vertex in self.exterior]
        interiors = [
            [vertex.copy(identical) for vertex in interior] for interior in self.interiors]
        try:
            self.construction
        except AttributeError:
            self.construction = False
        new = type(self)(
            exterior,
            interiors,
            self.shapetype,
            self.construction)
        if identical:
            new.id = self.id
        return new

    def upgrade(self, identical=True):
        exterior = [vertex.upgrade(identical) for vertex in self.exterior]
        interiors = [
            [vertex.upgrade(identical) for vertex in interior] for interior in self.interiors]
        try:
            self.construction
        except AttributeError:
            self.construction = False

        if self.shapetype == self.shapetypes.line:
            newtype = GenericLine
        elif self.shapetype == self.shapetypes.polyline:
            newtype = GenericPolyline
        elif self.shapetype == self.shapetypes.polygon:
            newtype = GenericPoly
        elif self.shapetype == self.shapetypes.circle:
            newtype = GenericCircle
        elif self.shapetype == self.shapetypes.rect2point:
            newtype = GenericTwoPointRect

        new = newtype(exterior, interiors, self.construction)
        if identical:
            new.id = self.id
        return new

    def pickpainterpathfunction(self):
        if (self.shapetype == self.shapetypes.line) or (
                self.shapetype == self.shapetypes.polyline):
            return self.generatelinepath
        elif (self.shapetype == self.shapetypes.polygon):
            return self.generateholeypolypath
        elif (self.shapetype == self.shapetypes.circle):
            return self.generatecirclepath
        elif (self.shapetype == self.shapetypes.rect2point):
            return self.generaterect2pointpath
        else:
            raise Exception

    def addvertex_exterior(self, vertex):
        self.exterior.append(vertex)
        self.update_handles()

    @classmethod
    def gengenericpoly(cls, exterior_p, interiors_p, **kwargs):
        from popupcad.geometry.vertex import ShapeVertex

        exterior = [ShapeVertex(point) for point in exterior_p]
        interiors= [[ShapeVertex(point) for point in interior] for interior in interiors_p]
        shapetype = cls.shapetypes.polygon

        return cls(exterior, interiors, shapetype, **kwargs)

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePath, InteractivePoly, InteractiveLine, InteractiveCircle, InteractiveRect2Point

        if self.shapetype == self.shapetypes.line:
            drawableclass = InteractiveLine
        elif self.shapetype == self.shapetypes.polyline:
            drawableclass = InteractivePath
        elif self.shapetype == self.shapetypes.polygon:
            drawableclass = InteractivePoly
        elif self.shapetype == self.shapetypes.circle:
            drawableclass = InteractiveCircle
        elif self.shapetype == self.shapetypes.rect2point:
            drawableclass = InteractiveRect2Point
        else:
            raise Exception

        drawable = drawableclass(self)
        return drawable

    def outputstatic(self, color=None):
        from popupcad.graphics2d.static import StaticPoly, StaticPath, StaticLine, StaticCircle, StaticRect2Point
        if self.shapetype == self.shapetypes.line:
            staticclass = StaticLine
        elif self.shapetype == self.shapetypes.polyline:
            staticclass = StaticPath
        elif self.shapetype == self.shapetypes.polygon:
            staticclass = StaticPoly
        elif self.shapetype == self.shapetypes.circle:
            staticclass = StaticCircle
        elif self.shapetype == self.shapetypes.rect2point:
            staticclass = StaticRect2Point
        else:
            raise Exception

        drawable = staticclass(self, color=color)
        return drawable

    def to_shapely(self):
        import shapely.geometry
        import shapely.geometry as sg        

        exterior_p = self.exteriorpoints()
        interiors_p = self.interiorpoints()

        if self.shapetype == self.shapetypes.line:
            obj = sg.LineString(exterior_p)
        elif self.shapetype == self.shapetypes.polyline:
            obj = sg.LineString(exterior_p)
        elif self.shapetype == self.shapetypes.polygon:
            obj = sg.Polygon(exterior_p, interiors_p)
        elif self.shapetype == self.shapetypes.circle:
            exterior = numpy.array(exterior_p)
            center = exterior[0]
            v = exterior[1] - exterior[0]
            r = v.dot(v)**.5
            obj = sg.Point(*center).buffer(r)
            obj = sg.Polygon(obj.boundary)
        elif self.shapetype == self.shapetypes.rect2point:
            corner1 = exterior_p[0]
            corner2 = (exterior_p[0][0], exterior_p[1][1])
            corner3 = exterior_p[1]
            corner4 = (exterior_p[1][0], exterior_p[0][1])
            corners = [corner1, corner2, corner3, corner4]
            obj = sg.Polygon(corners)
        else:
            raise Exception

        return obj

    def triangles3(self):
        from pypoly2tri.shapes import Point
        from pypoly2tri.cdt import CDT

        exterior = [Point(*point) for point in self.exteriorpoints()]
        interiors = [[Point(*point) for point in interior]
                     for interior in self.interiorpoints()]
        cdt = CDT(exterior)
        [cdt.AddHole(interior) for interior in interiors]
        cdt.Triangulate()
        tris = [tri.toList() for tri in cdt.GetTriangles()]
        return tris

    def lines(self):
        lines = []
        poly = self.exteriorpoints()
        lines.extend(zip(poly, poly[1:] + poly[:1]))
        for poly in self.interiorpoints():
            lines.extend(zip(poly, poly[1:] + poly[0:1]))
        return lines

GenericDrawable = GenericShape
GenericPolygon = GenericShape
