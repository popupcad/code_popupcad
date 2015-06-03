# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:56:59 2015

@author: danb0b
"""
from popupcad.filetypes.popupcad_file import popupCADFile

class GenericLaminate(popupCADFile):
    filetypes = {'laminate':'Laminate File'}
    defaultfiletype = 'laminate'

    def __init__(self,layerdef,geoms):
        super(GenericLaminate,self).__init__()
        self.layerdef = layerdef
        self.geoms = geoms
        
    def copy(self,identical = True):
        geoms = {}
        for key,value in self.geoms.items():
            geoms[key] = [item.copy(identical) for item in value]
        new = type(self)(self.layerdef,geoms)
        if identical:
            new.id = self.id
        return new
        
    def to_csg(self):
        from popupcad.filetypes.laminate import Laminate
        new = Laminate(self.layerdef)
        for ii,layer in enumerate(self.layerdef.layers):
            geoms = [item.outputshapely() for item in self.geoms[layer]]
            new.replacelayergeoms(layer,geoms)
        return new

    def to_static(self):
        display_geometry_2d = {}
        for layer,geometry in self.geoms.items():
            displaygeometry = [geom.outputstatic(brush_color = layer.color) for geom in geometry]
            display_geometry_2d[layer] = displaygeometry
        return display_geometry_2d

    def to_triangles(self):
        alltriangles = {}
        for layer,geoms in self.geoms.items():
            triangles = []
            for geom in geoms:
                try:
                    triangles.extend(geom.triangles3())
                except AttributeError:
                    pass
            alltriangles[layer] = triangles
        return alltriangles
        

    def layers(self):
        return self.layerdef.layers

    def to_static_sorted(self):
        items = []
        display_geometry = self.to_static() 
        layers = self.layerdef.layers
        for layer in layers:
            items.extend(display_geometry[layer])
        return items        
        
if __name__=='__main__':
    import PySide.QtGui as qg
    import sys
    app = qg.QApplication(sys.argv)
    

    a = GenericLaminate(1,{})
    a.copy()
    a.saveAs()
#    sys.exit(app.exec_())
