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
import scipy.linalg

try: #Hack to ensure Python 2 & 3 support
    import itertools.izip as zip
except ImportError:
    pass


from popupcad.filetypes.genericshapebase import GenericShapeBase


class GenericLine(GenericShapeBase):
    def condition_loop(self,loop):
        return self._condition_loop(loop,remove_loop_reduncancy=False,remove_forward_redundancy=False)

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
        model_space.add_lwpolyline(self.exteriorpoints(),dxfattribs = dxfattribs)
        
class GenericPolyline(GenericShapeBase):
    def condition_loop(self,loop):
        return self._condition_loop(loop,remove_loop_reduncancy=False)

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
        model_space.add_lwpolyline(self.exteriorpoints(),dxfattribs = dxfattribs)

    def addvertex_exterior(self, vertex, special=False):
        self.addvertex_exterior_special(vertex,special)

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
        from pypoly2tri.shapes import Point
        from pypoly2tri.cdt import CDT

#        if you have poly2tri installed
#        from p2t import Point
#        from p2t import CDT

        new = self.copy(identical = False)
        new._condition(round_vertices=False,
                       test_rounded_vertices = True,
                       remove_forward_redundancy = True,
                       remove_loop_reduncancy = True,
                       terminate_with_start = False,
                       decimal_places = popupcad.geometry_round_value)

        exterior = [Point(*point) for point in new.exteriorpoints(scaling = popupcad.triangulation_scaling)]
        interiors = [[Point(*point) for point in interior]
                     for interior in new.interiorpoints(scaling = popupcad.triangulation_scaling)]
        cdt = CDT(exterior)
        [cdt.AddHole(interior) for interior in interiors]

#        pypoly2tri code
        cdt.Triangulate()
        tris = [tri.toList() for tri in cdt.GetTriangles()]

#        poly2tri code
#        triangles = cdt.triangulate()
#        tris = [[(tri.a.x, tri.a.y), (tri.b.x, tri.b.y), (tri.c.x, tri.c.y)]
#                for tri in triangles]

        tris = (numpy.array(tris)/popupcad.triangulation_scaling).tolist()
        return tris

    def outputshapely(self):
        exterior_p = self.exteriorpoints(scaling = popupcad.csg_processing_scaling)
        interiors_p = self.interiorpoints(scaling = popupcad.csg_processing_scaling)
        obj = customshapely.ShapelyPolygon(exterior_p, interiors_p)
        return obj

    def addvertex_exterior(self, vertex, special=False):
        self.addvertex_exterior_special(vertex,special)
        
    def segments(self):
        return self.segments_closed()
        
    def mass_properties(self,density,z_lower,z_upper,length_scaling = 1):
        z_lower = z_lower*length_scaling/popupcad.SI_length_scaling
        z_upper = z_upper*length_scaling/popupcad.SI_length_scaling
        tris = numpy.array(self.triangles3())*length_scaling/popupcad.SI_length_scaling
        shape = list(tris.shape)
        shape[2]+=1
        z_center = (z_lower+z_upper)/2
        tris2 = numpy.ones(shape)
        tris2[:,:,:2] = tris
        areas = abs(numpy.array([scipy.linalg.det(tri) for tri in tris2])/2)
        area = areas.sum()
        tris2[:,:,2] = z_center
        centroids = tris2.sum(1)/3
        centroid = (areas*centroids.T).sum(1)/areas.sum()

        thickness = z_upper - z_lower
        volume = area*thickness
        mass = volume*density
        return area,centroid,volume,mass,tris

    def inertia_tensor(self,about_point,density,z_lower,z_upper,tris):
        z_lower = z_lower/popupcad.SI_length_scaling
        z_upper = z_upper/popupcad.SI_length_scaling
        import popupcad.algorithms.triangle as triangle
        tris3 = [triangle.Triangle(*tri) for tri in tris]
        tets = [tet for tri in tris3 for tet in tri.extrude(z_lower,z_upper)]
        Is = numpy.array([tet.I(density,about_point) for tet in tets])
        I = Is.sum(0)
        return I

    def hollow(self):
        polylines = []
        for loop in [self.get_exterior()]+self.get_interiors():
            newloop = [vertex.copy(identical = False) for vertex in loop+loop[0:1]]
            polylines.append(GenericPolyline(newloop,[],self.is_construction()))
        return polylines
            
    #Returns the area scaled to match the appropiate size of the mesh
    def trueArea(self):
        p = self.exteriorpoints()
        p = [[float(x)/popupcad.SI_length_scaling for x in point] for point in p]#scales appropiately 
        return 0.5 * abs(sum(x0*y1 - x1*y0
                             for ((x0, y0), (x1, y1)) in zip(p, p[1:] + [p[0]])))
   
    def output_dxf(self,model_space,layer = None):
        exterior = self.exteriorpoints()
        dxfattribs = {'closed':True}
        if layer is not None:
            dxfattribs['layer']=layer
        model_space.add_lwpolyline(exterior,dxfattribs=dxfattribs)
        for interior in self.interiorpoints():
            dxfattribs = {'closed':True}
            if layer is not None:
                dxfattribs['layer']=layer
            model_space.add_lwpolyline(interior,dxfattribs=dxfattribs)
        

    #Gets the center
    def get_center(self):
        points = self.exteriorpoints()
        x_values = [point[0]/popupcad.SI_length_scaling for point in points]
        y_values = [point[1]/popupcad.SI_length_scaling for point in points]
        x = float(sum(x_values)) / len(x_values)
        y = float(sum(y_values)) / len(y_values)
        return (x, y)
    
    def exterior_points_from_center(self):
        center = self.get_center()
        points = self.exteriorpoints()
        x_values = [point[0]/popupcad.SI_length_scaling - center[0] for point in points]
        y_values = [point[1]/popupcad.SI_length_scaling - center[1] for point in points]
        return list(zip(x_values, y_values))
        
class GenericCircle(GenericShapeBase):

    def condition_loop(self,loop):
        return self._condition_loop(loop,remove_loop_reduncancy=False,remove_forward_redundancy=False)

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
    def condition_loop(self,loop):
        return self._condition_loop(loop,remove_loop_reduncancy=False,remove_forward_redundancy=False)

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

if __name__=='__main__':
    a = GenericPoly.gen_from_point_lists([[0,0],[0,1],[1,2],[2,1],[2,-1],[1,-2],[0,-1]],[])
#`    area,centroid,I= a.mass_props(1,-.1,.1)\
    z_lower = -.1
    z_upper = .1
    length_scaling = 1
    density = 1
    area,centroid,volume,mass,tris = a.mass_properties(density,z_lower ,z_upper,length_scaling)
    about_point = centroid
    I = a.inertia_tensor(about_point,density,z_lower,z_upper,tris)
    area2 = a.trueArea()
    print(area,area2)
