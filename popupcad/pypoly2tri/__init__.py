# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

#import cdt
from . import advancing_front
from . import shapes
from . import sweep
from . import sweep_context
from . import utils

from .shapes import Point,Triangle
from .cdt import CDT

import matplotlib.pyplot as plt
plt.ion()



if __name__=='__main__':
    import p2t
    import sys
#    sys.setrecursionlimit(8000)
#    with file('data/dude.dat','r') as f:
#    with file('data/bird.dat','r') as f:
#        data = f.readlines()
#    
#    data = [item.replace('\n','').split(' ') for item in data]
#    data = [[float(item) for item in items if item !=''] for items in data]
#    points = [Point(*coord) for coord in data]
    
    exterior = [[-1,-1],[-1,1],[1,1],[1,-1]]    
    interior= [[-.1,-.1],[-.1,.1],[.1,.1],[.1,-.1]]    
    points = [Point(*coord) for coord in exterior]
    intpoints = [Point(*coord) for coord in interior]
    cdt = CDT(points)
    cdt.AddHole(intpoints)
    cdt.Triangulate()
#    cdt = p2t.CDT(points)
#    cdt.add_hole(intpoints)
#    b = cdt.triangulate()

    fig = plt.figure()
    ax = fig.add_subplot(111)    
    import numpy
    for tri in cdt.GetTriangles():
#    for tri in b:
        points = [tri.GetPoint(ii) for ii in range(3)]
#        points = [tri.a,tri.b,tri.c]
        points = [(point.x,point.y) for point in points]
        points = numpy.array(points+points[0:1])
        
        ax.plot(*points.T)
        
