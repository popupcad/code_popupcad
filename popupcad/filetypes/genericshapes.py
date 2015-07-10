# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry import customshapely

import popupcad
import shapely.geometry
import numpy
import PySide.QtCore as qc
import PySide.QtGui as qg

try: #Hack to ensure Python 2 & 3 support
    import itertools.izip as zip
except ImportError:
    pass


from popupcad.filetypes.genericshapebase import GenericShapeBase


class GenericLine(GenericShapeBase):

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveLine
        return InteractiveLine(self)

    def outputstatic(self, *args, **kwargs):
        from popupcad.graphics2d.static import StaticLine
        return StaticLine(self, *args, **kwargs)

    def gen_painterpath(self, exterior, interiors):
        path = qg.QPainterPath()
        path.addPolygon(self.generateQPolygon(exterior))
        return path

    def outputshapely(self):
        exterior_p = self.exteriorpoints(scaling = popupcad.csg_processing_scaling)
        obj = customshapely.ShapelyLineString(exterior_p)
        return obj

    def segments(self):
        return self.segments_open()

    def output_dxf(self,model_space,layer = None):
        dxfattribs = {}
        if layer is not None:
            dxfattribs['layer']=layer
        model_space.add_lwpolyline(self.exteriorpoints(scaling = 1./popupcad.internal_argument_scaling),dxfattribs = dxfattribs)
        
class GenericPolyline(GenericShapeBase):
    @classmethod
    def remove_redundant_points(cls, points, scaling=1):
        return GenericShapeBase.remove_redundant_points(points,scaling,loop_test = False)

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePath
        return InteractivePath(self)

    def outputstatic(self, *args, **kwargs):
        from popupcad.graphics2d.static import StaticPath
        return StaticPath(self, *args, **kwargs)

    def gen_painterpath(self, exterior, interiors):
        path = qg.QPainterPath()
        path.addPolygon(self.generateQPolygon(exterior))
        return path

    def outputshapely(self):
        exterior_p = self.exteriorpoints(scaling = popupcad.csg_processing_scaling)
        obj = customshapely.ShapelyLineString(exterior_p)
        return obj

    def segments(self):
        return self.segments_open()

    def fill(self):
        polygons = []
        for loop in [self.get_exterior()]+self.get_interiors():
            newloop = [vertex.copy(identical = False) for vertex in loop]
            polygons.append(GenericPoly(newloop,[],self.is_construction()))
        return polygons

    def output_dxf(self,model_space,layer = None):
        dxfattribs = {}
        if layer is not None:
            dxfattribs['layer']=layer
        model_space.add_lwpolyline(self.exteriorpoints(scaling = 1./popupcad.internal_argument_scaling),dxfattribs = dxfattribs)


class GenericPoly(GenericShapeBase):

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractivePoly
        return InteractivePoly(self)

    def outputstatic(self, *args, **kwargs):
        from popupcad.graphics2d.static import StaticPoly
        return StaticPoly(self, *args, **kwargs)

    def gen_painterpath(self, exterior, interiors):
        path = qg.QPainterPath()
        for item in [exterior] + interiors:
            path.addPolygon(self.generateQPolygon(item))
            path.closeSubpath()
        return path

    def triangles3(self):
        try:
            from pypoly2tri.shapes import Point
            from pypoly2tri.cdt import CDT
            use_poly2tri = False
        except ImportError:
            try:
                use_poly2tri = True
                from p2t import Point
                from p2t import CDT
            except ImportError:
                return []
        exterior = [Point(*point) for point in self.exteriorpoints()]
        interiors = [[Point(*point) for point in interior]
                     for interior in self.interiorpoints()]
        cdt = CDT(exterior)
        [cdt.AddHole(interior) for interior in interiors]
        if not use_poly2tri:
            cdt.Triangulate()
            tris = [tri.toList() for tri in cdt.GetTriangles()]
        else:
            triangles = cdt.triangulate()
            tris = [[(tri.a.x, tri.a.y), (tri.b.x, tri.b.y), (tri.c.x, tri.c.y)]
                    for tri in triangles]
        return tris

    def outputshapely(self):
        exterior_p = self.exteriorpoints(scaling = popupcad.csg_processing_scaling)
        interiors_p = self.interiorpoints(scaling = popupcad.csg_processing_scaling)
        obj = customshapely.ShapelyPolygon(exterior_p, interiors_p)
        return obj

    def addvertex_exterior(self, vertex, special=False):
        if len(self.get_exterior()) > 2:
            if special:
                a = [v.getpos() for v in self.get_exterior()]
                b = list(zip(a, a[1:] + a[:1]))
                c = numpy.array(b)
                d = numpy.array(vertex.getpos())
                e = c - d
                f = e.reshape(-1, 4)
                g = (f**2).sum(1)
                h = g.argmin()
                self.insert_exterior_vertex(h + 1, vertex)
                self.update_handles()
                return
        self.append_exterior_vertex(vertex)
        self.update_handles()

    def segments(self):
        return self.segments_closed()

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
            a = range(c, c + len(vertices))
            b = zip(a, a[1:] + a[:1])
            segments.extend(b)
            c += d

        for loop in ip:
            p = sg.Polygon(loop)
            e = p.representative_point()
            holes.append((e.x, e.y))
        tri = {}
        tri['vertices'] = numpy.array(vertices)
        tri['segments'] = numpy.array(segments)
        if len(holes) > 0:
            tri['holes'] = numpy.array(holes)
        return tri

    def triangles4(self):
        import triangle
        a = self.toTriangleFormat()
        t = triangle.triangulate(a)
        b = t['vertices'][t['triangles']]
        return [tri.tolist() for tri in b]

    def hollow(self):
        polylines = []
        for loop in [self.get_exterior()]+self.get_interiors():
            newloop = [vertex.copy(identical = False) for vertex in loop] + [loop[0].copy(identical = False)]
            polylines.append(GenericPolyline(newloop,[],self.is_construction()))
        return polylines
            
    #Returns the area scaled to match the appropiate size of the mesh
    def trueArea(self):
        p = self.exteriorpoints()
        p = [[float(x)/popupcad.internal_argument_scaling/popupcad.SI_length_scaling for x in point] for point in p]#scales appropiately 
        return 0.5 * abs(sum(x0*y1 - x1*y0
                             for ((x0, y0), (x1, y1)) in zip(p, p[1:] + [p[0]])))
   
    def output_dxf(self,model_space,layer = None):
        dxfattribs = {'closed':True}
        if layer is not None:
            dxfattribs['layer']=layer
        model_space.add_lwpolyline(self.exteriorpoints(scaling = 1./popupcad.internal_argument_scaling),dxfattribs=dxfattribs)

    #Gets the center
    def get_center(self):
        scaling_factor = popupcad.internal_argument_scaling*popupcad.SI_length_scaling
        points = self.exteriorpoints()
        x_values = [point[0]/scaling_factor for point in points]
        y_values = [point[1]/scaling_factor for point in points]
        x = float(sum(x_values)) / len(x_values)
        y = float(sum(y_values)) / len(y_values)
        return (x, y)
    
    def exterior_points_from_center(self):
        scaling_factor = popupcad.internal_argument_scaling*popupcad.SI_length_scaling
        center = self.get_center()
        points = self.exteriorpoints()
        x_values = [point[0]/scaling_factor - center[0] for point in points]
        y_values = [point[1]/scaling_factor - center[1] for point in points]
        return list(zip(x_values, y_values))
        
class GenericCircle(GenericShapeBase):

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveCircle
        return InteractiveCircle(self)

    def outputstatic(self, *args, **kwargs):
        from popupcad.graphics2d.static import StaticCircle
        return StaticCircle(self, *args, **kwargs)

    def gen_painterpath(self, exterior, interiors):
        path = qg.QPainterPath()
        center = numpy.array(exterior[0])
        edge = numpy.array(exterior[1])
        v = edge - center
        r = v.dot(v)**.5
        point1 = center - r
        point2 = center + r
        point1 = qc.QPointF(*point1)
        point2 = qc.QPointF(*point2)
        rect = qc.QRectF(point1, point2)
        path.addEllipse(rect)
        return path

    def outputshapely(self):
        exterior_p = self.exteriorpoints(scaling = popupcad.csg_processing_scaling)
        exterior = numpy.array(exterior_p)
        center = exterior[0]
        v = exterior[1] - exterior[0]
        r = v.dot(v)**.5
        obj = shapely.geometry.Point(*center).buffer(r)
        obj = customshapely.ShapelyPolygon(obj.boundary)
        return obj

    def segments(self):
        return self.segments_closed()


class GenericTwoPointRect(GenericShapeBase):

    def outputinteractive(self):
        from popupcad.graphics2d.interactive import InteractiveRect2Point
        return InteractiveRect2Point(self)

    def outputstatic(self, *args, **kwargs):
        from popupcad.graphics2d.static import StaticRect2Point
        return StaticRect2Point(self, *args, **kwargs)

    def gen_painterpath(self, exterior, interiors):
        path = qg.QPainterPath()
        points = [qc.QPointF(*point) for point in exterior]
        rect = qc.QRectF(*points)
        path.addRect(rect)
        return path

    def outputshapely(self):
        exterior_p = self.exteriorpoints(scaling = popupcad.csg_processing_scaling)
        corner1 = exterior_p[0]
        corner2 = (exterior_p[0][0], exterior_p[1][1])
        corner3 = exterior_p[1]
        corner4 = (exterior_p[1][0], exterior_p[0][1])
        corners = [corner1, corner2, corner3, corner4]
        obj = customshapely.ShapelyPolygon(corners)
        return obj

    def segments(self):
        return self.segments_closed()
