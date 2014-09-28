# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 14:49:18 2014

@author: danaukes
"""

import popupcad
import popupcad.algorithms.points as points
import numpy
import math

roundvalue = -1
tolerance = 1*10**(-roundvalue)
def getjoints(geoms):
    from popupcad.geometry.vertex import ShapeVertex
    from popupcad.filetypes.genericshapes import GenericLine
    
    lines = []
    
    for geom in geoms:
        p = geom.exteriorpoints()
        lines.extend(zip(p,p[1:]+p[:1]))
        for interior in geom.interiorpoints():
            lines.extend(zip(interior,interior[1:]+interior[:1]))
    
    l3 = popupcad.algorithms.points.distance_of_lines(lines,[0,0])
    l4 = popupcad.algorithms.points.distance_of_lines(lines,[10*tolerance,0])
    l5 = popupcad.algorithms.points.distance_of_lines(lines,[0,10*tolerance])
    m=numpy.c_[l3,l4,l5]
    m = m.round(roundvalue)
    m2 = [tuple(items) for items in m.tolist()]
    m3 = list(set(m2))
#    jj = numpy.searchsorted(m3,m2)   
    index_to_unique = [m3.index(item) for item in m2]
    indeces_to_orig = [[] for item in m3]
    [indeces_to_orig[item].append(ii) for ii,item in enumerate(index_to_unique)]

    newsegments = []
    for segments in indeces_to_orig:
        if len(segments)>1:
            a = [lines[ii] for ii in segments]
            vertices = []
            [vertices.extend(item) for item in a[1:]]
            ordered_vertices = popupcad.algorithms.points.order_vertices(vertices,a[0],tolerance = tolerance)
            segs = [(v1,v2) for v1,v2 in zip(ordered_vertices[:-1],ordered_vertices[1:])]
            midpoints = popupcad.algorithms.points.segment_midpoints(segs)
            count = [0 for item in midpoints]
            for ii in segments:
                for jj,point in enumerate(midpoints):
                    if popupcad.algorithms.points.point_within_line(point,lines[ii],tolerance = tolerance):
                        count[jj]+=1
            newsegments.extend([seg for count_ii,seg in zip(count,segs) if count_ii>1])
#            newsegments.extend(segs)

    newsegments2 = [GenericLine([ShapeVertex(position=v1),ShapeVertex(position=v2)],[]) for v1,v2 in newsegments]
    outputsegments = [segment.outputinteractive() for segment in newsegments2]
    return outputsegments
        
