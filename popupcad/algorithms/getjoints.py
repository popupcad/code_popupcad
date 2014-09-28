# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 14:49:18 2014

@author: danaukes
"""
import popupcad.algorithms.points as points
import numpy
import math

def getjoints(geoms):
    lines = []
    from popupcad.geometry.vertex import ShapeVertex
    from popupcad.filetypes.genericshapes import GenericLine
    vertices = []
    
    
    for geom in geoms:
        p = geom.exteriorpoints()
        vertices.extend(p)
        lines.extend(zip(p,p[1:]+p[:1]))
        for interior in geom.interiorpoints():
            vertices.extend(interior)
            lines.extend(zip(interior,interior[1:]+interior[:1]))
    
    vertices = list(set(vertices))

#    vertices2 = numpy.array(vertices)
#    vertices3 = vertices2.round(4)
#    vertices4 = [tuple(item) for item in vertices3]
#    vertices5 = list(set(vertices4))
    controlpoints = [ShapeVertex(position = p) for p in vertices]

#    lines = list(set(lines))

#    lines2 = []
#    for point1,point2 in lines:
#        if point1[0]<point2[0]:
#            lines2.append((point1,point2))
#        else:
#            lines2.append((point2,point1))

    lines2 = numpy.array(lines)
    rise = lines2[:,1,1] - lines2[:,0,1]
    run = lines2[:,1,0] - lines2[:,0,0]
    v1 = lines2[:,1,:] - lines2[:,0,:]
    l1 = (v1**2).sum(1)**.5
    v2 = lines2[:,0,:]
    v3 = numpy.cross(v1,v2)
    l3 = v3/l1
    
    l3.round(3)

    l3_unique = numpy.unique(l3)
    ii = l3_unique.argsort()
    l3_unique_sorted = l3_unique[ii]
    jj = numpy.searchsorted(l3_unique_sorted,l3)
    
#    sorted_x = x[index]
#    sorted_index = np.searchsorted(sorted_x, y)

    q = numpy.arctan2(rise,run)*180/math.pi

    return []
#    return controlpoints, controllines