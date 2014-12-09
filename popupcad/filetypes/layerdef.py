# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad

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