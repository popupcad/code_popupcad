# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 10:11:06 2015

@author: danaukes
"""
import numpy
import scipy
import scipy.linalg

class Tetrahedron(object):
    def __init__(self,*points):
        self.points = numpy.array(points)

    def centroid(self):
        return self.points.sum(0)/len(self.points)
        
    def J(self):
        J = self.points[1:] - self.points[0]
        return J

    def volume(self):
        return scipy.linalg.det(self.J())/6

    def pointlist(self,point):
        p = numpy.c_[self.points.T,point]
        return p.flatten().tolist()

    def I_xx(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        return self.I_xx_unscaled(*pointlist)*self._J_det(*pointlist)
    def I_yy(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        return self.I_yy_unscaled(*pointlist)*self._J_det(*pointlist)
    def I_zz(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        return self.I_zz_unscaled(*pointlist)*self._J_det(*pointlist)
    def I_xy(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        return self.I_xy_unscaled(*pointlist)*self._J_det(*pointlist)
    def I_yz(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        return self.I_yz_unscaled(*pointlist)*self._J_det(*pointlist)
    def I_zx(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        return self.I_zx_unscaled(*pointlist)*self._J_det(*pointlist)
    def I(self,point = None):
        if point is None:
            point = [0,0,0]
        pointlist = self.pointlist(point)
        Ixx = self.I_xx_unscaled(*pointlist)
        Iyy = self.I_yy_unscaled(*pointlist)
        Izz = self.I_zz_unscaled(*pointlist)
        Ixy = self.I_xy_unscaled(*pointlist)
        Iyz = self.I_yz_unscaled(*pointlist)
        Izx = self.I_zx_unscaled(*pointlist)
        I = numpy.array([[Ixx,Ixy,Izx],[Ixy,Iyy,Iyz],[Izx,Iyz,Izz]])
        return I*self._J_det(*pointlist)

    #generated automatically        
    @staticmethod
    def I_xx_unscaled(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return (y_0**2 + y_0*y_1 + y_0*y_2 + y_0*y_3 - 5*y_0*yc + y_1**2 + y_1*y_2 + y_1*y_3 - 5*y_1*yc + y_2**2 + y_2*y_3 - 5*y_2*yc + y_3**2 - 5*y_3*yc + 10*yc**2 + z_0**2 + z_0*z_1 + z_0*z_2 + z_0*z_3 - 5*z_0*zc + z_1**2 + z_1*z_2 + z_1*z_3 - 5*z_1*zc + z_2**2 + z_2*z_3 - 5*z_2*zc + z_3**2 - 5*z_3*zc + 10*zc**2)/60
    @staticmethod
    def I_yy_unscaled(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return (x_0**2 + x_0*x_1 + x_0*x_2 + x_0*x_3 - 5*x_0*xc + x_1**2 + x_1*x_2 + x_1*x_3 - 5*x_1*xc + x_2**2 + x_2*x_3 - 5*x_2*xc + x_3**2 - 5*x_3*xc + 10*xc**2 + z_0**2 + z_0*z_1 + z_0*z_2 + z_0*z_3 - 5*z_0*zc + z_1**2 + z_1*z_2 + z_1*z_3 - 5*z_1*zc + z_2**2 + z_2*z_3 - 5*z_2*zc + z_3**2 - 5*z_3*zc + 10*zc**2)/60
    @staticmethod
    def I_zz_unscaled(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return (x_0**2 + x_0*x_1 + x_0*x_2 + x_0*x_3 - 5*x_0*xc + x_1**2 + x_1*x_2 + x_1*x_3 - 5*x_1*xc + x_2**2 + x_2*x_3 - 5*x_2*xc + x_3**2 - 5*x_3*xc + 10*xc**2 + y_0**2 + y_0*y_1 + y_0*y_2 + y_0*y_3 - 5*y_0*yc + y_1**2 + y_1*y_2 + y_1*y_3 - 5*y_1*yc + y_2**2 + y_2*y_3 - 5*y_2*yc + y_3**2 - 5*y_3*yc + 10*yc**2)/60
    @staticmethod
    def I_xy_unscaled(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -(2*x_0*y_0 + x_0*y_1 + x_0*y_2 + x_0*y_3 - 5*x_0*yc + x_1*y_0 + 2*x_1*y_1 + x_1*y_2 + x_1*y_3 - 5*x_1*yc + x_2*y_0 + x_2*y_1 + 2*x_2*y_2 + x_2*y_3 - 5*x_2*yc + x_3*y_0 + x_3*y_1 + x_3*y_2 + 2*x_3*y_3 - 5*x_3*yc - 5*xc*y_0 - 5*xc*y_1 - 5*xc*y_2 - 5*xc*y_3 + 20*xc*yc)/120
    @staticmethod
    def I_yz_unscaled(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -(2*y_0*z_0 + y_0*z_1 + y_0*z_2 + y_0*z_3 - 5*y_0*zc + y_1*z_0 + 2*y_1*z_1 + y_1*z_2 + y_1*z_3 - 5*y_1*zc + y_2*z_0 + y_2*z_1 + 2*y_2*z_2 + y_2*z_3 - 5*y_2*zc + y_3*z_0 + y_3*z_1 + y_3*z_2 + 2*y_3*z_3 - 5*y_3*zc - 5*yc*z_0 - 5*yc*z_1 - 5*yc*z_2 - 5*yc*z_3 + 20*yc*zc)/120
    @staticmethod
    def I_zx_unscaled(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -(2*x_0*z_0 + x_0*z_1 + x_0*z_2 + x_0*z_3 - 5*x_0*zc + x_1*z_0 + 2*x_1*z_1 + x_1*z_2 + x_1*z_3 - 5*x_1*zc + x_2*z_0 + x_2*z_1 + 2*x_2*z_2 + x_2*z_3 - 5*x_2*zc + x_3*z_0 + x_3*z_1 + x_3*z_2 + 2*x_3*z_3 - 5*x_3*zc - 5*xc*z_0 - 5*xc*z_1 - 5*xc*z_2 - 5*xc*z_3 + 20*xc*zc)/120
    @staticmethod
    def _J_det(x_0,x_1,x_2,x_3,xc,y_0,y_1,y_2,y_3,yc,z_0,z_1,z_2,z_3,zc):
        return -x_0*y_1*z_2 + x_0*y_1*z_3 + x_0*y_2*z_1 - x_0*y_2*z_3 - x_0*y_3*z_1 + x_0*y_3*z_2 + x_1*y_0*z_2 - x_1*y_0*z_3 - x_1*y_2*z_0 + x_1*y_2*z_3 + x_1*y_3*z_0 - x_1*y_3*z_2 - x_2*y_0*z_1 + x_2*y_0*z_3 + x_2*y_1*z_0 - x_2*y_1*z_3 - x_2*y_3*z_0 + x_2*y_3*z_1 + x_3*y_0*z_1 - x_3*y_0*z_2 - x_3*y_1*z_0 + x_3*y_1*z_2 + x_3*y_2*z_0 - x_3*y_2*z_1


        
if __name__=='__main__':
    p0= numpy.array([0,0,0])
    p1= numpy.array([1,0,0])
    p2= numpy.array([0,1,0])
    p3= numpy.array([0,0,1])
    t=Tetrahedron(p0,p1,p2,p3)
    c=t.centroid()    
    J = t.J()
    v = t.volume()