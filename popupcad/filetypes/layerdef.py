# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import popupcad

class LayerDef(object):

    def __init__(self, *args):
        self.layers = list(args)
        
    def copy(self):
        layers = [layer.copy() for layer in self.layers]
        new = type(self)(*layers)
        return new

    def upgrade(self):
        layers = [layer.upgrade() for layer in self.layers]
        new = type(self)(*layers)
        return new
        
    def addlayer(self, layer):
        self.layers.append(layer)
        del self.z_values
        
    def calc_z_values(self):
        zvalue = {}
        zval = 0.
        for layer in self.layers[::1]:
            zvalue[layer] = zval
            zval += layer.thickness
        return zvalue
        
    def __repr__(self):
        string = 'Laminate'
        return string

    def getlayer(self, ref):
        dict1 = dict([(item.id, item) for item in self.layers])
        return dict1[ref]

    def getlayer_ii(self, ref):
        layer = self.getlayer(ref)
        return self.layers.index(layer)

    def neighbors(self, layer):
        '''Find the layers above and below a given layer'''
        ii = self.layers.index(layer)
        neighbors = []
        if ii > 0:
            neighbors.append(self.layers[ii - 1])
        if ii < len(self.layers) - 1:
            neighbors.append(self.layers[ii + 1])
        return neighbors

    def connected_neighbors(self, layer):
        neighbors = self.neighbors(layer)
        connected = [neighbor for neighbor in neighbors if (neighbor.is_adhesive or layer.is_adhesive)]
        return connected

    def z_values2(self):
        zvalues = {}
        z = 0.
        for layer in self.layers:
            zvalues[layer] = {'lower':z}
            zvalues[layer]['mid']=z+layer.thickness/2
            z += layer.thickness
            zvalues[layer]['upper'] = z
        return zvalues

    @property
    def z_values(self):
        try:
            return self._z_values
        except AttributeError:
            self._z_values = self.calc_z_values()
            return self._z_values

    @z_values.deleter
    def z_values(self):
        try:
            del self._z_values
        except AttributeError:
            pass
            
