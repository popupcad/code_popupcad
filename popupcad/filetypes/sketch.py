# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import os
from popupcad.constraints import ConstraintSystem
import popupcad
#import PySide.QtGui as qg
from .genericfile import popupCADFile

class Sketch(popupCADFile):
    filetypes = {'sketch':'Sketch File'}
    defaultfiletype = 'sketch'
    filters,filterstring,selectedfilter = popupCADFile.buildfilters(filetypes,defaultfiletype)
    @classmethod
    def lastdir(cls):
        return popupcad.lastsketchdir

    @classmethod
    def setlastdir(cls,directory):
        popupcad.lastsketchdir = directory

    def __init__(self):
        super(Sketch,self).__init__()
        self.operationgeometry = []
        self.constraintsystem = ConstraintSystem()
        self.id = id(self)
        self._basename = self.genbasename()

    def copy(self,identical = True):
        new = Sketch()
        new.operationgeometry = [geom.copy(identical=True) for geom in self.operationgeometry if geom.isValid()]
        new.constraintsystem = self.constraintsystem.copy()
        if identical:
            new.id = self.id

        self.copy_file_params(new,identical)

        return new

    def addoperationgeometries(self,polygons):
        self.operationgeometry.extend(polygons)

    def cleargeometries(self):
        self.operationgeometry = []

    def edit(self,parent,design = None,**kwargs):
        from popupcad.guis.sketcher import Sketcher
        sketcher = Sketcher(parent,self,design,accept_method = self.edit_result,**kwargs)
        sketcher.show()
        sketcher.graphicsview.zoomToFit()

    def edit_result(self,sketch):
        self.operationgeometry = sketch.operationgeometry
        self.constraintsystem = sketch.constraintsystem
        
    def output_csg(self):
        import popupcad.geometry.customshapely
        shapelygeoms = []
        for item in self.operationgeometry:
            try:
                if not item.is_construction():
                    shapelyitem = item.outputshapely()
                    shapelygeoms.append(shapelyitem)
            except ValueError as ex:
                print(ex)
            except AttributeError as ex:
                shapelyitem = item.outputshapely()
                shapelygeoms.append(shapelyitem)
        shapelygeoms = popupcad.geometry.customshapely.unary_union_safe(shapelygeoms)   
        shapelygeoms = popupcad.geometry.customshapely.multiinit(shapelygeoms)
        return shapelygeoms