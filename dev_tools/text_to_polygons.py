# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 20:58:26 2016

@author: danb0b
"""
import numpy 

def quadratic(t,p0,p1,p2):
    b = p0*(1-t)**2 + 2*p1*t*(1-t) + p2*t**2
    return b
    
def cubic(t,p0,p1,p2,p3):
    b = p0*(1-t)**3+3*p1*t*(1-t)**2+3*p2*t**2*(1-t)+p3*t**3
    return b

def interp_2d(function,points,SUBDIVISION):
    points = numpy.array(points)
    t = numpy.r_[1/SUBDIVISION:1:SUBDIVISION*1j]
    interp = [function(t_i,*points) for t_i in t]
    return interp
    
def text_to_polygons(text,prop,subdivision = None):
    from matplotlib.textpath import TextPath
#    from matplotlib.font_manager import FontProperties
#    prop = FontProperties(family='Times New Roman',size=10)
    text_path = TextPath([0,0],text,prop=prop)

    subdivision = subdivision or 10
    
    codes = text_path.codes
    vertices = text_path.vertices

    polygons = []
    polygon = []
    ii=0
    done = False
    while not done:
        print(ii)
        
        if codes[ii] == text_path.MOVETO:
            if len(polygon)>0:
                polygons.append(polygon)
            polygon = [tuple(vertices[ii])]
            ii+=1
                
        elif codes[ii] == text_path.LINETO:
            polygon.append(tuple(vertices[ii]))
            ii+=1
        elif codes[ii] == text_path.CURVE3:
            curve_points = vertices[(ii-1,ii,ii+1),:]
            polygon.extend(interp_2d(quadratic,curve_points,subdivision))
            ii+=2
        elif  codes[ii] == text_path.CURVE4:
            curve_points = vertices[(ii-1,ii,ii+1,ii+2),:]
            polygon.extend(interp_2d(cubic,curve_points,subdivision))
            ii+=3
        elif  codes[ii] == text_path.CLOSEPOLY:
            polygons.append(polygon)
            polygon = []
            ii+=1
        else:
            raise(Exception('unknown'))
        done = ii>=len(codes)

    if len(polygon)>0:
        polygons.append(polygon)
    return polygons


if __name__=='__main__':
    import matplotlib.pyplot as plt
    plt.ion()
    g = text_to_polygons('Hello',None)
    for poly in g:
        poly = poly[:]+poly[0:1]
        poly = numpy.array(poly)
        plt.plot(poly[:,0],poly[:,1])
    plt.axis('equal')
    plt.show()
