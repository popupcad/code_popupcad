# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:56:59 2015

@author: danb0b
"""
from popupcad.filetypes.popupcad_file import popupCADFile

class GenericLaminate(popupCADFile):
    filetypes = {'laminate':'Laminate File'}
    defaultfiletype = 'laminate'
    filters,filterstring,selectedfilter = popupCADFile.buildfilters(filetypes,defaultfiletype)

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
        
    def toLaminate(self):
        from popupcad.filetypes.laminate import Laminate
        new = Laminate(self.layerdef)
        for ii,layer in enumerate(self.layerdef.layers):
            geoms = [item.outputshapely() for item in self.geoms[layer]]
            new.replacelayergeoms(layer,geoms)
        return new
    def layers(self):
        return self.layerdef.layers
        
if __name__=='__main__':
    import PySide.QtGui as qg
    import sys
    app = qg.QApplication(sys.argv)
    

    a = GenericLaminate(1,{})
    a.copy()
    a.saveAs()
#    sys.exit(app.exec_())
