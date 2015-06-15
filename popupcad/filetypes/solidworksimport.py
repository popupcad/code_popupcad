# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


import numpy
from popupcad.filetypes.genericshapes import GenericPoly
from popupcad.filetypes.genericshapebase import NotSimple,ShapeInvalid,GenericShapeBase
import popupcad
import PySide.QtGui as qg
from popupcad.filetypes.popupcad_file import popupCADFile
#import shapely.geometry as sg
import popupcad.geometry.customshapely as cs

class Loop(object):
    def __init__(self,loop,geom):
        self.loop = loop
        self.geom = geom

class Face(object):
    pass

class Component(object):
    pass

class Assembly(popupCADFile):
    filetypes = {'yaml':'Yaml File'}
    defaultfiletype = 'yaml'

    @classmethod
    def lastdir(cls):
        return popupcad.lastimportdir

    @classmethod
    def setlastdir(cls,directory):
        popupcad.lastimportdir = directory

    def convert(self,parent = None,scalefactor = 1. ,area_ratio =1e-3,colinear_tol = 1e-1,bufferval = 0.,cleanup = .01):
        ok1 = True
        ok2 = True
        ok3 = True
        ok4 = True
        ok5 = True
        if scalefactor == None:
            scalefactor, ok1 = qg.QInputDialog.getDouble(parent,'Scale Factor','Scale Factor',1,0,1e10,decimals = 10)        

        if area_ratio == None:
            area_ratio, ok2 = qg.QInputDialog.getDouble(parent,'Area Ratio','Area Ratio',.001,0,1e10,decimals = 10)        

        if colinear_tol == None:
            colinear_tol, ok3 = qg.QInputDialog.getDouble(parent,'Colinear Tolerance','Colinear Tolerance',1e-8,0,1e10,decimals = 10)        

        if bufferval == None:
            bufferval, ok4 = qg.QInputDialog.getDouble(parent,'Buffer','Buffer',0,-1e10,1e10,decimals = 10)        

        if cleanup == None:
            cleanup, ok5 = qg.QInputDialog.getDouble(parent,'Simplify','Simplify',0.0,0,1e10,decimals = 10)        
    
        if ok1 and ok2 and ok3 and ok4 and ok5:
            self._convert(scalefactor,area_ratio,colinear_tol,bufferval,cleanup)
                
    def _convert(self,scalefactor,area_ratio,colinear_tol,bufferval,cleanup):
        self.geoms = []
        T1 = numpy.array(self.transform)
        R1 = T1[0:3,0:3]
        b1 = T1[0:3,3:4]
        for ii,component in enumerate(self.components):
            T2 = numpy.array(component.transform)
            R2 = T2[0:3,0:3]
            b2 = T2[0:3,3:4]            
            if component.faces!=None:
                for jj,face in enumerate(component.faces):
                    try:
                        loops = face.loops

                        ints_c = [self.transform_loop(interior,R1,b1,R2,b2,scalefactor*popupcad.internal_argument_scaling) for interior in loops]
                        
                        a = [GenericPoly.gen_from_point_lists(loop,[],test_shapely = False) for loop in ints_c]
                        b = [item.outputshapely() for item in a]
                        if cleanup>=0:
                            b = [item.simplify(cleanup*popupcad.internal_argument_scaling) for item in b]
                        c = b.pop(0)
                        for item in b:
                            c = c.symmetric_difference(item)
                        d = cs.multiinit(c)
                        e = cs.multiinit(*[item.buffer(bufferval*popupcad.internal_argument_scaling,resolution = popupcad.default_buffer_resolution) for item in d])
                        f = [GenericShapeBase.genfromshapely(item) for item in e]
                        self.geoms.extend(f)
                    except NotSimple:
                        pass
                    except ShapeInvalid:
                        pass
                    except ValueError as ex:
                        print(ex)
#                        if ex.message!='A LinearRing must have at least 3 coordinate tuples':
#                            print(ex.message)
        self.filter_small_areas(area_ratio)
            
    @staticmethod
    def transform_loop(loop,R1,b1,R2,b2,scalefactor):
        looparray = numpy.array(loop).T
        
        v2 = R1.T.dot(R2.T.dot(looparray)+b2)
        v2 = v2[0:2,:].T
        v2 = v2*scalefactor*popupcad.internal_argument_scaling
        return v2.tolist()
        
    def build_face_sketch(self):
        self.convert(scalefactor = None,bufferval = None,cleanup = None)
        sketch = popupcad.filetypes.sketch.Sketch()
        sketch.addoperationgeometries(self.geoms)
        return sketch
        
    def filter_small_areas(self,area_ratio):
        areas = []
        for geom in self.geoms:
            shape = geom.outputshapely()
            areas.append(abs(shape.area))
        goodgeoms = []
        badgeoms= []
        for geom in self.geoms:
            shape = geom.outputshapely()
            if abs(shape.area)<max(areas)*area_ratio:
                badgeoms.append(geom)
            else:
                goodgeoms.append(geom)
        self.geoms = goodgeoms
        self.badgeoms = badgeoms

    @staticmethod
    def buildloops(geoms):
        loops = []
        for geom in geoms:
            loops.append(geom.exteriorpoints())
            loops.extend(geom.interiorpoints())
        return loops
        
if __name__=='__main__':
    import sys

    app = qg.QApplication(sys.argv)
    a = Assembly.open()
    a.convert(scalefactor = 1., bufferval = None)
    sys.exit(app.exec_())
