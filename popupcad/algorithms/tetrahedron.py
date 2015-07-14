# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 10:11:06 2015

@author: danaukes
"""
import numpy
import scipy
import scipy.linalg

class Tetrahedron(object):
    def __init__(self,density,*points):
        self.points = numpy.array(points)
        self.density = density
        
    def centroid(self):
        return self.points.sum(0)/len(self.points)
        
    def J(self):
        J = self.points[1:] - self.points[0]
        return J

    def volume(self):
        return abs(scipy.linalg.det(self.J())/6)

    def mass(self):
        return self.volume()*self.density

    def variable_list(self,point):
        density = self.density
        volume = self.volume()
        points = numpy.c_[self.points.T,point]
        points = points.flatten().tolist()
        return [density,volume]+points

    def I_xx(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        return self.I_xx_unscaled(*variable_list)*self._J_det(*variable_list)
    def I_yy(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        return self.I_yy_unscaled(*variable_list)*self._J_det(*variable_list)
    def I_zz(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        return self.I_zz_unscaled(*variable_list)*self._J_det(*variable_list)
    def I_xy(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        return self.I_xy_unscaled(*variable_list)*self._J_det(*variable_list)
    def I_yz(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        return self.I_yz_unscaled(*variable_list)*self._J_det(*variable_list)
    def I_zx(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        return self.I_zx_unscaled(*variable_list)*self._J_det(*variable_list)
    def I(self,point = None):
        if point is None:
            point = [0,0,0]
        variable_list = self.variable_list(point)
        Ixx = self.I_xx_unscaled(*variable_list)
        Iyy = self.I_yy_unscaled(*variable_list)
        Izz = self.I_zz_unscaled(*variable_list)
        Ixy = self.I_xy_unscaled(*variable_list)
        Iyz = self.I_yz_unscaled(*variable_list)
        Izx = self.I_zx_unscaled(*variable_list)
        I = numpy.array([[Ixx,Ixy,Izx],[Ixy,Iyy,Iyz],[Izx,Iyz,Izz]])
        return I*self._J_det(*variable_list)

    #generated automatically        
    @staticmethod
    def I_xx_unscaled(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return (density*volume*x_0**2 + density*volume*x_0*x_1 + density*volume*x_0*x_2 + density*volume*x_0*x_3 - 5*density*volume*x_0*xc + density*volume*x_1**2 + density*volume*x_1*x_2 + density*volume*x_1*x_3 - 5*density*volume*x_1*xc + density*volume*x_2**2 + density*volume*x_2*x_3 - 5*density*volume*x_2*xc + density*volume*x_3**2 - 5*density*volume*x_3*xc + 10*density*volume*xc**2 + density*volume*y_0**2 + density*volume*y_0*y_1 + density*volume*y_0*y_2 + density*volume*y_0*y_3 - 5*density*volume*y_0*yc + density*volume*y_1**2 + density*volume*y_1*y_2 + density*volume*y_1*y_3 - 5*density*volume*y_1*yc + density*volume*y_2**2 + density*volume*y_2*y_3 - 5*density*volume*y_2*yc + density*volume*y_3**2 - 5*density*volume*y_3*yc + 10*density*volume*yc**2 + density*volume*z_0**2 + density*volume*z_0*z_1 + density*volume*z_0*z_2 + density*volume*z_0*z_3 - 5*density*volume*z_0*zc + density*volume*z_1**2 + density*volume*z_1*z_2 + density*volume*z_1*z_3 - 5*density*volume*z_1*zc + density*volume*z_2**2 + density*volume*z_2*z_3 - 5*density*volume*z_2*zc + density*volume*z_3**2 - 5*density*volume*z_3*zc + 10*density*volume*zc**2 - x_0**2 - x_0*x_1 - x_0*x_2 - x_0*x_3 + 5*x_0*xc - x_1**2 - x_1*x_2 - x_1*x_3 + 5*x_1*xc - x_2**2 - x_2*x_3 + 5*x_2*xc - x_3**2 + 5*x_3*xc - 10*xc**2)/60
    @staticmethod
    def I_yy_unscaled(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return (density*volume*x_0**2 + density*volume*x_0*x_1 + density*volume*x_0*x_2 + density*volume*x_0*x_3 - 5*density*volume*x_0*xc + density*volume*x_1**2 + density*volume*x_1*x_2 + density*volume*x_1*x_3 - 5*density*volume*x_1*xc + density*volume*x_2**2 + density*volume*x_2*x_3 - 5*density*volume*x_2*xc + density*volume*x_3**2 - 5*density*volume*x_3*xc + 10*density*volume*xc**2 + density*volume*y_0**2 + density*volume*y_0*y_1 + density*volume*y_0*y_2 + density*volume*y_0*y_3 - 5*density*volume*y_0*yc + density*volume*y_1**2 + density*volume*y_1*y_2 + density*volume*y_1*y_3 - 5*density*volume*y_1*yc + density*volume*y_2**2 + density*volume*y_2*y_3 - 5*density*volume*y_2*yc + density*volume*y_3**2 - 5*density*volume*y_3*yc + 10*density*volume*yc**2 + density*volume*z_0**2 + density*volume*z_0*z_1 + density*volume*z_0*z_2 + density*volume*z_0*z_3 - 5*density*volume*z_0*zc + density*volume*z_1**2 + density*volume*z_1*z_2 + density*volume*z_1*z_3 - 5*density*volume*z_1*zc + density*volume*z_2**2 + density*volume*z_2*z_3 - 5*density*volume*z_2*zc + density*volume*z_3**2 - 5*density*volume*z_3*zc + 10*density*volume*zc**2 - y_0**2 - y_0*y_1 - y_0*y_2 - y_0*y_3 + 5*y_0*yc - y_1**2 - y_1*y_2 - y_1*y_3 + 5*y_1*yc - y_2**2 - y_2*y_3 + 5*y_2*yc - y_3**2 + 5*y_3*yc - 10*yc**2)/60
    @staticmethod
    def I_zz_unscaled(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return (density*volume*x_0**2 + density*volume*x_0*x_1 + density*volume*x_0*x_2 + density*volume*x_0*x_3 - 5*density*volume*x_0*xc + density*volume*x_1**2 + density*volume*x_1*x_2 + density*volume*x_1*x_3 - 5*density*volume*x_1*xc + density*volume*x_2**2 + density*volume*x_2*x_3 - 5*density*volume*x_2*xc + density*volume*x_3**2 - 5*density*volume*x_3*xc + 10*density*volume*xc**2 + density*volume*y_0**2 + density*volume*y_0*y_1 + density*volume*y_0*y_2 + density*volume*y_0*y_3 - 5*density*volume*y_0*yc + density*volume*y_1**2 + density*volume*y_1*y_2 + density*volume*y_1*y_3 - 5*density*volume*y_1*yc + density*volume*y_2**2 + density*volume*y_2*y_3 - 5*density*volume*y_2*yc + density*volume*y_3**2 - 5*density*volume*y_3*yc + 10*density*volume*yc**2 + density*volume*z_0**2 + density*volume*z_0*z_1 + density*volume*z_0*z_2 + density*volume*z_0*z_3 - 5*density*volume*z_0*zc + density*volume*z_1**2 + density*volume*z_1*z_2 + density*volume*z_1*z_3 - 5*density*volume*z_1*zc + density*volume*z_2**2 + density*volume*z_2*z_3 - 5*density*volume*z_2*zc + density*volume*z_3**2 - 5*density*volume*z_3*zc + 10*density*volume*zc**2 - z_0**2 - z_0*z_1 - z_0*z_2 - z_0*z_3 + 5*z_0*zc - z_1**2 - z_1*z_2 - z_1*z_3 + 5*z_1*zc - z_2**2 - z_2*z_3 + 5*z_2*zc - z_3**2 + 5*z_3*zc - 10*zc**2)/60
    @staticmethod
    def I_xy_unscaled(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -(2*x_0*y_0 + x_0*y_1 + x_0*y_2 + x_0*y_3 - 5*x_0*yc + x_1*y_0 + 2*x_1*y_1 + x_1*y_2 + x_1*y_3 - 5*x_1*yc + x_2*y_0 + x_2*y_1 + 2*x_2*y_2 + x_2*y_3 - 5*x_2*yc + x_3*y_0 + x_3*y_1 + x_3*y_2 + 2*x_3*y_3 - 5*x_3*yc - 5*xc*y_0 - 5*xc*y_1 - 5*xc*y_2 - 5*xc*y_3 + 20*xc*yc)/120
    @staticmethod
    def I_yz_unscaled(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -(2*y_0*z_0 + y_0*z_1 + y_0*z_2 + y_0*z_3 - 5*y_0*zc + y_1*z_0 + 2*y_1*z_1 + y_1*z_2 + y_1*z_3 - 5*y_1*zc + y_2*z_0 + y_2*z_1 + 2*y_2*z_2 + y_2*z_3 - 5*y_2*zc + y_3*z_0 + y_3*z_1 + y_3*z_2 + 2*y_3*z_3 - 5*y_3*zc - 5*yc*z_0 - 5*yc*z_1 - 5*yc*z_2 - 5*yc*z_3 + 20*yc*zc)/120
    @staticmethod
    def I_zx_unscaled(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -(2*x_0*z_0 + x_0*z_1 + x_0*z_2 + x_0*z_3 - 5*x_0*zc + x_1*z_0 + 2*x_1*z_1 + x_1*z_2 + x_1*z_3 - 5*x_1*zc + x_2*z_0 + x_2*z_1 + 2*x_2*z_2 + x_2*z_3 - 5*x_2*zc + x_3*z_0 + x_3*z_1 + x_3*z_2 + 2*x_3*z_3 - 5*x_3*zc - 5*xc*z_0 - 5*xc*z_1 - 5*xc*z_2 - 5*xc*z_3 + 20*xc*zc)/120
    @staticmethod
    def _J_det(density,volume,x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -x_0*y_1*z_2 + x_0*y_1*z_3 + x_0*y_2*z_1 - x_0*y_2*z_3 - x_0*y_3*z_1 + x_0*y_3*z_2 + x_1*y_0*z_2 - x_1*y_0*z_3 - x_1*y_2*z_0 + x_1*y_2*z_3 + x_1*y_3*z_0 - x_1*y_3*z_2 - x_2*y_0*z_1 + x_2*y_0*z_3 + x_2*y_1*z_0 - x_2*y_1*z_3 - x_2*y_3*z_0 + x_2*y_3*z_1 + x_3*y_0*z_1 - x_3*y_0*z_2 - x_3*y_1*z_0 + x_3*y_1*z_2 + x_3*y_2*z_0 - x_3*y_2*z_1


        
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