# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.genericshapes import GenericShapeBase
from popupcad.filetypes.genericshapes import GenericPoly
from scipy.spatial import Delaunay

def joinedges(vertices):
    '''Create a convex polygon from given points'''
    delaunay = Delaunay(vertices)
    
    cvx = delaunay.convex_hull.copy()
    lastrow = cvx[0]        
    iis = range(len(cvx))
    for ii in iis[1:-1]:
        lastindex = lastrow[1]
        findop = (cvx[ii:]==lastindex).nonzero()
        
        jj = findop[0][0]+ii

        cvx[(ii,jj),:]=cvx[(jj,ii),:]
        if findop[1][0]==1:
            cvx[ii,(1,0)]=cvx[ii,(0,1)]
        
        lastrow = cvx[ii]

    lastindex = lastrow[1]
    findop = (cvx[-1]==lastindex).nonzero()
    if findop[0][0]==1:
        cvx[-1,(1,0)]=cvx[-1,(0,1)]
        
    polyindeces = cvx[:,0]
    polypoints=delaunay.points[polyindeces,:].tolist()
    poly = GenericPoly.gen_from_point_lists(polypoints,[])
    return poly

def autobridge(vertices):
    '''Create the triangulation of a set of points, and output the resulting triangles'''
    from scipy.spatial import Delaunay
    d = Delaunay(vertices)
    polys=d.points[d.vertices].tolist()
    genericpolys = [GenericPoly.gen_from_point_lists(poly,[]) for poly in polys]    
    return genericpolys  