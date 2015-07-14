# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 10:11:06 2015

@author: danaukes
"""
import numpy
import scipy
import scipy.linalg

def I_xx_unscaled(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return density*(y_0**2 + y_0*y_1 + y_0*y_2 + y_0*y_3 - 5*y_0*yc + y_1**2 + y_1*y_2 + y_1*y_3 - 5*y_1*yc + y_2**2 + y_2*y_3 - 5*y_2*yc + y_3**2 - 5*y_3*yc + 10*yc**2 + z_0**2 + z_0*z_1 + z_0*z_2 + z_0*z_3 - 5*z_0*zc + z_1**2 + z_1*z_2 + z_1*z_3 - 5*z_1*zc + z_2**2 + z_2*z_3 - 5*z_2*zc + z_3**2 - 5*z_3*zc + 10*zc**2)/60
def I_yy_unscaled(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return density*(x_0**2 + x_0*x_1 + x_0*x_2 + x_0*x_3 - 5*x_0*xc + x_1**2 + x_1*x_2 + x_1*x_3 - 5*x_1*xc + x_2**2 + x_2*x_3 - 5*x_2*xc + x_3**2 - 5*x_3*xc + 10*xc**2 + z_0**2 + z_0*z_1 + z_0*z_2 + z_0*z_3 - 5*z_0*zc + z_1**2 + z_1*z_2 + z_1*z_3 - 5*z_1*zc + z_2**2 + z_2*z_3 - 5*z_2*zc + z_3**2 - 5*z_3*zc + 10*zc**2)/60
def I_zz_unscaled(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return density*(x_0**2 + x_0*x_1 + x_0*x_2 + x_0*x_3 - 5*x_0*xc + x_1**2 + x_1*x_2 + x_1*x_3 - 5*x_1*xc + x_2**2 + x_2*x_3 - 5*x_2*xc + x_3**2 - 5*x_3*xc + 10*xc**2 + y_0**2 + y_0*y_1 + y_0*y_2 + y_0*y_3 - 5*y_0*yc + y_1**2 + y_1*y_2 + y_1*y_3 - 5*y_1*yc + y_2**2 + y_2*y_3 - 5*y_2*yc + y_3**2 - 5*y_3*yc + 10*yc**2)/60
def I_xy_unscaled(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return -density*(2*x_0*y_0 + x_0*y_1 + x_0*y_2 + x_0*y_3 - 5*x_0*yc + x_1*y_0 + 2*x_1*y_1 + x_1*y_2 + x_1*y_3 - 5*x_1*yc + x_2*y_0 + x_2*y_1 + 2*x_2*y_2 + x_2*y_3 - 5*x_2*yc + x_3*y_0 + x_3*y_1 + x_3*y_2 + 2*x_3*y_3 - 5*x_3*yc - 5*xc*y_0 - 5*xc*y_1 - 5*xc*y_2 - 5*xc*y_3 + 20*xc*yc)/120
def I_yz_unscaled(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return -density*(2*y_0*z_0 + y_0*z_1 + y_0*z_2 + y_0*z_3 - 5*y_0*zc + y_1*z_0 + 2*y_1*z_1 + y_1*z_2 + y_1*z_3 - 5*y_1*zc + y_2*z_0 + y_2*z_1 + 2*y_2*z_2 + y_2*z_3 - 5*y_2*zc + y_3*z_0 + y_3*z_1 + y_3*z_2 + 2*y_3*z_3 - 5*y_3*zc - 5*yc*z_0 - 5*yc*z_1 - 5*yc*z_2 - 5*yc*z_3 + 20*yc*zc)/120
def I_zx_unscaled(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return -density*(2*x_0*z_0 + x_0*z_1 + x_0*z_2 + x_0*z_3 - 5*x_0*zc + x_1*z_0 + 2*x_1*z_1 + x_1*z_2 + x_1*z_3 - 5*x_1*zc + x_2*z_0 + x_2*z_1 + 2*x_2*z_2 + x_2*z_3 - 5*x_2*zc + x_3*z_0 + x_3*z_1 + x_3*z_2 + 2*x_3*z_3 - 5*x_3*zc - 5*xc*z_0 - 5*xc*z_1 - 5*xc*z_2 - 5*xc*z_3 + 20*xc*zc)/120
def _J_det(density,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
    return -x_0*y_1*z_2 + x_0*y_1*z_3 + x_0*y_2*z_1 - x_0*y_2*z_3 - x_0*y_3*z_1 + x_0*y_3*z_2 + x_1*y_0*z_2 - x_1*y_0*z_3 - x_1*y_2*z_0 + x_1*y_2*z_3 + x_1*y_3*z_0 - x_1*y_3*z_2 - x_2*y_0*z_1 + x_2*y_0*z_3 + x_2*y_1*z_0 - x_2*y_1*z_3 - x_2*y_3*z_0 + x_2*y_3*z_1 + x_3*y_0*z_1 - x_3*y_0*z_2 - x_3*y_1*z_0 + x_3*y_1*z_2 + x_3*y_2*z_0 - x_3*y_2*z_1


class Tetrahedron(object):
    def __init__(self,*points):
        self.points = numpy.array(points)
        
    def centroid(self):
        return self.points.sum(0)/len(self.points)
        
    def J(self):
        J = self.points[1:] - self.points[0]
        return J

    def volume(self):
        return abs(scipy.linalg.det(self.J())/6)

    def mass(self):
        return self.volume()*self.density

    def variable_list(self,density,point):
        points = numpy.c_[self.points.T,point]
        points = points.flatten().tolist()
        return [density]+points

    def I_xx(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        return I_xx_unscaled(*variable_list)*abs(self._J_det(*variable_list))
#        return I_xx_unscaled(*variable_list)
    def I_yy(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        return I_yy_unscaled(*variable_list)*abs(self._J_det(*variable_list))
#        return I_yy_unscaled(*variable_list)
    def I_zz(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        return I_zz_unscaled(*variable_list)*abs(self._J_det(*variable_list))
#        return I_zz_unscaled(*variable_list)
    def I_xy(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        return I_xy_unscaled(*variable_list)*abs(self._J_det(*variable_list))
#        return I_xy_unscaled(*variable_list)
    def I_yz(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        return I_yz_unscaled(*variable_list)*abs(self._J_det(*variable_list))
#        return I_yz_unscaled(*variable_list)
    def I_zx(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        return I_zx_unscaled(*variable_list)*abs(self._J_det(*variable_list))
#        return I_zx_unscaled(*variable_list)
    def I(self,density,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(density,point)
        Ixx = I_xx_unscaled(*variable_list)
        Iyy = I_yy_unscaled(*variable_list)
        Izz = I_zz_unscaled(*variable_list)
        Ixy = I_xy_unscaled(*variable_list)
        Iyz = I_yz_unscaled(*variable_list)
        Izx = I_zx_unscaled(*variable_list)
        I = numpy.array([[Ixx,Ixy,Izx],[Ixy,Iyy,Iyz],[Izx,Iyz,Izz]])
        return I*abs(_J_det(*variable_list))
#        return I




        
if __name__=='__main__':
    p0= numpy.array([0,0,0])
    p1= numpy.array([1,0,0])
    p2= numpy.array([0,1,0])
    p3= numpy.array([0,0,1])
    density = 1000
    t=Tetrahedron(density,p0,p1,p2,p3)
    c=t.centroid()    
    J = t.J()
    v = t.volume()