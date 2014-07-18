# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


import numpy
from popupcad.geometry.genericshapebase import GenericShapeBase
from popupcad.geometry.genericshapebase import NotSimple,ShapeInvalid
import popupcad
import PySide.QtGui as qg
from popupcad.filetypes.genericfile import popupCADFile
import shapely.geometry as sg
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
    filters,filterstring,selectedfilter = popupCADFile.buildfilters(filetypes,defaultfiletype)

    @classmethod
    def lastdir(cls):
        return popupcad.lastimportdir

    @classmethod
    def setlastdir(cls,directory):
        popupcad.lastimportdir = directory

    def convert(self,parent = None,scalefactor = 1. ,area_ratio =1e-3,colinear_tol = 1e-1,bufferval = 0.):
        ok1 = True
        ok2 = True
        ok3 = True
        if scalefactor == None:
            scalefactor, ok1 = qg.QInputDialog.getDouble(parent,'Scale Factor','Scale Factor',1,0,1e10)        

        if area_ratio == None:
            area_ratio, ok2 = qg.QInputDialog.getDouble(parent,'Area Ratio','Area Ratio',.001,0,1e10,decimals = 10)        

        if colinear_tol == None:
            colinear_tol, ok3 = qg.QInputDialog.getDouble(parent,'Colinear Tolerance','Colinear Tolerance',1e-8,0,1e10,decimals = 10)        

        if bufferval == None:
            bufferval, ok3 = qg.QInputDialog.getDouble(parent,'Buffer','Buffer',0,-1e10,1e10,decimals = 10)        
    
        if ok1 and ok2:
            self._convert(scalefactor,area_ratio,colinear_tol,bufferval)
                
    def _convert(self,scalefactor,area_ratio,colinear_tol,bufferval):
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
                        
                        a = [GenericShapeBase.gengenericpoly(loop,[],test_shapely = False) for loop in ints_c]
                        b = [item.outputshapely() for item in a]
                        c = b.pop(0)
                        for item in b:
                            c = c.symmetric_difference(item)
                        d = cs.multiinit(c)
                        e = cs.multiinit(*[item.buffer(bufferval,resolution = popupcad.default_buffer_resolution) for item in d])
                        f = [GenericShapeBase.genfromshapely(item) for item in e]
                        self.geoms.extend(f)
                    except NotSimple:
                        pass
                    except ShapeInvalid:
                        pass
                    except ValueError as ex:
                        if ex.message!='A LinearRing must have at least 3 coordinate tuples':
                            print(ex.message)
        self.filter_small_areas(area_ratio)
            
    @staticmethod
    def transform_loop(loop,R1,b1,R2,b2,scalefactor):
        looparray = numpy.array(loop).T
        
        v2 = R1.T.dot(R2.T.dot(looparray)+b2)
        v2 = v2[0:2,:].T
        v2 = v2*scalefactor*popupcad.internal_argument_scaling
        return v2.tolist()
        
    def build_face_sketch(self):
        self.convert(scalefactor = None,bufferval = None)
        sketch = popupcad.filetypes.Sketch()
        sketch.addoperationgeometries(self.geoms)
        return sketch
        
    def filter_small_areas(self,area_ratio):
#        import matplotlib.pyplot as plt
#        plt.ion()
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
        
#    def plotloops(self,loops,ax=None):
#        import matplotlib.pyplot as plt
#        plt.ion()
#        
#        if ax==None:
#            f = plt.figure()
#            ax = f.add_subplot(111)
#
#        for loop in loops:
#            L = numpy.array(loop+[loop[0]])
#            ax.plot(*(L.T))
#        plt.show()                

            
if __name__=='__main__':
    import sys
#    import matplotlib.pyplot as plt
#    plt.ion()

    app = qg.QApplication(sys.argv)
    a = Assembly.open()
    a.convert(scalefactor = 1., bufferval = None)
#    if a!=None:
#        f = plt.figure()
#        ax = f.add_subplot(111)
#        A = numpy.array(a.buildloops(a.goodgeoms))
#        a.plotloops(a.buildloops(a.geoms))
#        plt.axis('equal')
#
#        A2 = numpy.array(a.buildloops(a.badgeoms))
#        a.plotloops(a.buildloops(a.badgeoms))
#        plt.axis('equal')

#    self = a
#    import matplotlib.pyplot as plt
#    plt.ion()
#    import numpy
#    areas = []
#    for geom in self.geoms:
#        shape = geom.outputshapely()
#        areas.append(shape.area)
#    areas = numpy.array(areas)
#    import scipy.stats as stats
#    
##    l = numpy.r_[min(areas):max(areas):1j*len(areas)]
#    dist = stats.binned_statistic(areas,range(len(areas)),statistic = 'count',bins = 100)
#
#    plt.hist(areas,10)
#
#    plt.hist(areas,100)
##    print dist
#
#    dist = stats.binned_statistic([1, 2, 1, 2, 4], numpy.arange(10,15), statistic='mean',bins=3)
#    print dist
#
#    numpy.histogram()    
    
#    f = plt.figure()
#    ax = f.add_subplot(111)
#    for segment in a.shared_edges:
#        s = numpy.array(segment.exteriorpoints())
#        ax.plot(*s.T)
#    ax.figure.canvas.draw()        
#                
    sys.exit(app.exec_())
