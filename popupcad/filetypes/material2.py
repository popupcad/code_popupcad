# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

class Material2(object):
    display = ['color', 'thickness']
    editable = ['*']

    def __init__(self,name,color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive):
        self.name = name
        self.color = color
        self.thickness = thickness
        self.E1 = E1
        self.E2 = E2
        self.density = density
        self.poisson = poisson
        self.is_adhesive = is_adhesive
        self.is_rigid = is_rigid
        self.is_conductive = is_conductive
        self.id = id(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
    
    def copy(self):
        new = type(self)(self.name,self.color,self.thickness,self.E1,self.E2,self.density,self.poisson,self.is_adhesive,self.is_rigid,self.is_conductive)
        return new

    def upgrade(self):
        return self