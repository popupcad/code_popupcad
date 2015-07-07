# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:57:48 2015

@author: danaukes
"""
import numpy
import scipy
import scipy.linalg

class Triangle(object):
    def __init__(self,p0,p1,p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
    def centroid(self):
        return (self.p0+self.p1+self.p2) / 3
    def J(self):
        import numpy
        J = numpy.array([self.p1-self.p0,self.p2-self.p0])
        return J
    def area(self):
        return scipy.linalg.det(J)/2

if __name__=='__main__':
    p0= numpy.array([0,0])
    p1= numpy.array([1,1])
    p2= numpy.array([1,1])
    t=Triangle(p0,p1,p2)
    c=t.centroid()    
    J = t.J()
    Jdet = scipy.linalg.det(J)