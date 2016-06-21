# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg

import numpy
from popupcad.filetypes.genericshapes import GenericPoly

def quadratic(t,p0,p1,p2):
    b = p0*(1-t)**2 + 2*p1*t*(1-t) + p2*t**2
    return b
    
def cubic(t,p0,p1,p2,p3):
    b = p0*(1-t)**3+3*p1*t*(1-t)**2+3*p2*t**2*(1-t)+p3*t**3
    return b
    
def interp_2d(function,points,SUBDIVISION):
    points_x = [point.x for point in points]
    points_y = [point.y for point in points]
    t = numpy.r_[1/SUBDIVISION:1:SUBDIVISION*1j]
    interp_x = [function(t_i,*points_x) for t_i in t]
    interp_y = [function(t_i,*points_y) for t_i in t]
    interp = [(x,y) for x,y in zip(interp_x,interp_y)]
    return interp

def painterpath_to_generics(p,subdivision):
    
    elements = [p.elementAt(ii) for ii in range(p.elementCount())]
#    element_types = [str(item.type).split('.')[-1] for item in elements]
    
    vertex_lists = []
    vertex_list = []
    lastelement = elements[0]

    while not not elements:
        element = elements.pop(0)
        if element.type == qg.QPainterPath.MoveToElement:
#            print('moveto',element.x,element.y)
            if len(vertex_list)>0:
                vertex_lists.append(vertex_list)
                vertex_list = [(element.x,element.y)]
            lastelement = element
                
        elif element.type == qg.QPainterPath.LineToElement:
#            print('lineto',element.x,element.y)
            vertex_list.append((element.x,element.y))
            lastelement = element
        elif element.type == qg.QPainterPath.CurveToElement:
#            print('curveto',element.x,element.y)

            subelements = []
            next_is_data = True
            while next_is_data:
                subelements.append(elements.pop(0))
                if len(elements)>0:
                    next_is_data = elements[0].type==qg.QPainterPath.CurveToDataElement
                else:
                    next_is_data = False
    
            if len(subelements)==1:
                points = [lastelement,element,subelements[0]]
                vertex_list.extend(interp_2d(quadratic,points,subdivision))
                lastelement = subelements[0]
            elif len(subelements)==2:
                points = [lastelement,element,subelements[0],subelements[1]]
                vertex_list.extend(interp_2d(cubic,points,subdivision))
                lastelement = subelements[1]
           
            else:
                raise(Exception('Wrong number of subelements'))

    vertex_lists.append(vertex_list)
    polys = []
    for vertex_list in vertex_lists:
        polys.append(GenericPoly.gen_from_point_lists(vertex_list,[]))
    
    return polys