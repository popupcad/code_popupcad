# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.materials.materials import Adhesive

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
    def getlayer_ii(self,ref):
        layer = self.getlayer(ref)
        return self.layers.index(layer)
        
    def neighbors(self,layer):   
        '''Find the layers above and below a given layer'''
#        from popupcad.materials.materials import Adhesive
        ii = self.layers.index(layer)
        neighbors = []
        if ii > 0:
            neighbors.append(self.layers[ii-1])
        if ii<len(self.layers)-1:
            neighbors.append(self.layers[ii+1])
        return neighbors

    def connected_neighbors(self,layer):
        neighbors = self.neighbors(layer)
        connected = [neighbor for neighbor in neighbors if (isinstance(neighbor,Adhesive) or isinstance(layer,Adhesive))]
        return connected
        