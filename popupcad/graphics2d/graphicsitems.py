# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg
import numpy
import popupcad.geometry

class Common(object):
    z_value = 0
    isDeletable = False
    def allchildren(self):
        return self.childItems()
    def softdelete(self):
        if self.isDeletable:
            self.harddelete()
    def harddelete(self):
        for child in self.allchildren():
            child.setParentItem(None)
            child.harddelete()
            del child
        self.setParentItem(None)
        self.removefromscene()
        del self

    def removefromscene(self):
        try:
            self.scene().removeItem(self)
        except AttributeError:
            pass

    def fullremove(self):
        for child in self.allchildren():
            child.setParentItem(None)
            child.fullremove()
            del child
        self.setParentItem(None)
        self.removefromscene()

class BasicLine(qg.QGraphicsPathItem,Common):
    pass

class SuperLine(qg.QGraphicsPathItem,Common):
    isDeletable = False
    neutral_buffer = 20
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    basicpen = qg.QPen(qg.QColor.fromRgbF(0,0,0,0), neutral_buffer, style, capstyle, joinstyle)             
    def __init__(self,*args,**kwargs):
        super(SuperLine,self).__init__(*args,**kwargs)
        self.line= BasicLine()
        self.line.setParentItem(self)
        self.setMyPen(self.basicpen)
        self.setBoundingRegionGranularity(.5)
    def setPos(self,*args,**kwargs):
        super(SuperLine,self).setPos(*args,**kwargs)
    def setPath(self,*args,**kwargs):
        super(SuperLine,self).setPath(*args,**kwargs)
        self.line.setPath(*args,**kwargs)
    def setPen(self,pen):
        self.line.setPen(pen)
    def setMyPen(self,pen):
        super(SuperLine,self).setPen(pen)

class CommonShape(object):
    def create_selectable_edge_loop(self):
        from .interactiveedge import InteractiveEdge
        self.selectableedges = []
        exterior = self.exterior()
        segments = zip(exterior,exterior[1:]+exterior[0:1])
        for handle1,handle2 in segments:
            item = InteractiveEdge(handle1,handle2)
            self.selectableedges.append(item)  
    def create_selectable_edge_path(self):
        from interactiveedge import InteractiveEdge
        self.selectableedges = []
        exterior = self.exterior()
        segments = zip(exterior[:-1],exterior[1:])
        for handle1,handle2 in segments:
            item = InteractiveEdge(handle1,handle2)
            self.selectableedges.append(item)  

    def create_selectable_edges(self):
        self.create_selectable_edge_loop()
        
    def updateshape(self):
        path = self.painterpath()
        self.setPath(path)
        self.update()

#class Rect2Point(CommonShape):
#    def create_selectable_edges(self):
#        self.create_selectable_edge_path()
#            

