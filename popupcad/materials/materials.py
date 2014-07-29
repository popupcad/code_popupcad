# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad

class Adhesive(object):
    pass
class Rigid(object):
    pass

class Material(object):
    display = ['color','thickness']
#    editable = ['color','thickness']
    name = 'material'
    color = (0.,0.,0.,.2)
    thickness = .025
    def __init__(self,thickness = None):
        if thickness!=None:
            self.thickness = thickness
        self.id = id(self)
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)
    
class Carbon_0_90_0(Material,Rigid):
    name = 'Carbon(0-90-0)'
    color = (1.,0.,0.,.2)

class Pyralux(Material,Adhesive):
    name = 'Pyralux'
    color = (0,1.,0.,.2)

class Kapton(Material):
    name = 'Kapton'
    color = (0.,0.,1.,.2)

class Cardboard(Material):
    name = 'Cardboard'
    color = (1.,0.,0.,.2)
        
class Silicone(Material):
    name = 'Silicone'
    color = (.75,.75,.75,.2)

class Velcro(Material):
    name = 'Velcro'
    color = (0.,.5,.5,.2)

class Dummy(Material):
    name = 'Dummy'
    color = (0.5,.5,.5,.2)

available_materials = [Carbon_0_90_0,Pyralux,Kapton,Cardboard,Silicone,Velcro,Dummy]
available_materials.sort()

class LayerDef(object):
    def __init__(self,*args):
        self.layers = list(args)
        self.refreshzvalues()
        
    def addlayer(self,layer):
        self.layers.append(layer)
        self.refreshzvalues()
        
    def refreshzvalues(self):        
        self.zvalue = {}
        zval = 0.
        for layer in self.layers[::1]:
            self.zvalue[layer]=zval
            zval +=layer.thickness*popupcad.internal_argument_scaling

    def __repr__(self):
        string = 'Laminate'
        return string
        
    def getlayer(self,ref):
        dict1 = dict([(item.id,item) for item in self.layers])
        return dict1[ref]
    
if __name__=='__main__':
    sublaminate = LayerDef(Carbon_0_90_0(),Pyralux(),Kapton(),Pyralux(),Carbon_0_90_0())