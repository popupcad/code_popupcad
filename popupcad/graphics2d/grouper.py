# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
import math
import numpy

from .graphicsitems import Common

def calctransform(x1,x2,q1,q2,scale_x,scale_y):
    
    T0 = numpy.eye(3)
    T0[0:2,2] = -x1

    T1 = numpy.eye(3)
    T1[0,0] = math.cos(-q1)
    T1[0,1] = -math.sin(-q1)
    T1[1,1] = math.cos(-q1)
    T1[1,0] = math.sin(-q1)

    T2 = numpy.eye(3)
    T2[0,0] = scale_x
    T2[1,1] = scale_y
    
    T3 = numpy.eye(3)
    T3[0,0] = math.cos(q2)
    T3[0,1] = -math.sin(q2)
    T3[1,1] = math.cos(q2)
    T3[1,0] = math.sin(q2)
    T3[0:2,2] = x2
    
    T = T3.dot(T2.dot(T1.dot(T0)))
    return T

def array2transform(T):
    array = T[0,0],T[0,1],T[1,0],T[1,1],T[0,2],T[1,2]
    t = qg.QTransform(*array)
    return t
    

class Grouper(qg.QGraphicsRectItem,Common):
    isDeletable = True
    def __init__(self,*args):
        super(Grouper,self).__init__(*args)
        p1 = qc.QPointF(-10,-10)
        p2 = qc.QPointF(10,10)
        rect = qc.QRectF(p1, p2)
        self.setRect(rect)
        
        self.groupeditems = []
        
        self.c1 = ScaleHandle(self)
        self.c2 = ScaleHandle(self)
        self.c3 = ScaleHandle(self)
        self.c4 = ScaleHandle(self)
        
        self.rotatehandle = RotateHandle(self)
        
        self.updatecontrolvertices()
        self.rotatehandle.setPos(0,10)
        self.dq = 0
        self.scale_x= 1.
        self.scale_y= 1.
        self.controlvertices = [self.c1,self.c2,self.c3,self.c4,self.rotatehandle]

        self.setFlag(self.ItemIsSelectable,True)
        self.setFlag(self.ItemIsFocusable,True)

    def addchildren(self,items):
        for item in items:
            item.setParentItem(self)
            self.groupeditems.append(item)
        self.rebound()
        
    def removegroupeditems(self):
        while not not self.groupeditems:
            item = self.groupeditems.pop()
            item.setParentItem(None)
            
    def updatecontrolvertices(self):
        rect = self.rect()
        
        self.c1.setPos(rect.bottomLeft())
        self.c2.setPos(rect.topLeft())
        self.c3.setPos(rect.topRight())
        self.c4.setPos(rect.bottomRight())

        self.rotatehandle.setPos((rect.bottomLeft()+rect.bottomRight())/2)
            
    def rebound(self):
        allpoints = []
        for child in self.allchildren():
            if child not in self.controlvertices:
                rect = child.boundingRect()
                p1 = rect.bottomLeft()
                p2 = rect.topLeft()
                p3 = rect.topRight()
                p4 = rect.bottomRight()
                points = [p1,p2,p3,p4]
                points = [child.mapToItem(self,p) for p in points]
                points = [[p.x(),p.y()] for p in points]
                allpoints.extend(points)
        allpoints = numpy.array(allpoints)

        p1 = qc.QPointF(*(allpoints.min(0)))
        p2 = qc.QPointF(*(allpoints.max(0)))
        
        rect = qc.QRectF(p1, p2)
        self.setRect(rect)
        self.updatecontrolvertices()
        self.recenter()
        self.setRect(qc.QRectF(self.c1.pos(),self.c3.pos()))

    def allchildren(self):
        return self.childItems() 

    def recenter(self):
        bl = numpy.array([self.c1.pos().x(),self.c1.pos().y()])
        tr = numpy.array([self.c3.pos().x(),self.c3.pos().y()])
        shiftval = (tr+bl)/2
        self.moveBy(*shiftval)
        for child in self.allchildren():
            child.moveBy(*(-shiftval))
        
    def cornerscale(self,startpos,currentpos,handle,proportional = True):
        center = (self.c1.scenePos()+self.c3.scenePos())/2
        center = numpy.array([center.x(),center.y()])
        v1 = startpos -center
        v2 = currentpos -center
        q1 = math.atan2(v1[1],v1[0])
        q2 = math.atan2(v2[1],v2[0])
        dq = q2 - q1
        zed = numpy.array([0,0])
        t = calctransform(zed, zed,0,dq,1,1)
        t = t[0:2,0:2]
        v11 = t.dot(v1)
        v22 = t.dot(v2)
        scale = (v2.dot(v2)**.5) / v1.dot(v1)**.5
        
        if isinstance(handle, ScaleHandle):
            if proportional:
                self.scale_x = scale*self.scalex
                self.scale_y = scale*self.scalex
            else:                
                if not any(v11==0):
                    scale_x = v22[0] / v11[0]
                    scale_y = v22[1] / v11[1]
                    self.scale_x = scale_x*self.scalex
                    self.scale_y = scale_y*self.scaley
        elif isinstance(handle, RotateHandle):
            self.dq = dq+self.originalrotation 
        else:
            raise(Exception('Enum Problem'))

        self.scaleme()
        self.recenter()

    def scaleme(self):
        zed = numpy.array([0,0])
        t = calctransform(zed,zed,0,self.dq,self.scale_x,self.scale_y)
        self.setTransform(array2transform(t).transposed())
        

    def savetinfo(self):
        t = self.transform()
        t.rotate(-self.rotation())
        a = numpy.array([t.m11(),t.m12(),t.m13()])
        b = numpy.array([t.m21(),t.m22(),t.m23()])
        self.scalex = a.dot(a)**.5
        self.scaley = b.dot(b)**.5
        x = a[0]/self.scalex
        y = a[1]/self.scalex
        self.originalrotation = math.atan2(y,x)

class StretchBox(qg.QGraphicsPathItem,Common):
    def __init__(self,*args):
        super(StretchBox,self).__init__(*args)
        p1 = qc.QPointF(-10,-10)
        p2 = qc.QPointF(10,10)
        rect = qc.QRectF(p1, p2)
        painterpath = qg.QPainterPath()
        painterpath.addRect(rect)
        self.setPath(painterpath)
    

class Handle(qg.QGraphicsEllipseItem,Common):
    def __init__(self,*args):
        super(Handle,self).__init__(*args)

        p1 = qc.QPointF(-5,-5)
        p2 = qc.QPointF(5,5)
        rect = qc.QRectF(p1,p2)
        
        self.setRect(rect)
        self.setFlag(self.ItemIsFocusable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIgnoresTransformations)
    def dragMoveEvent(self,*args):
        super(Handle,self).dragMoveEvent(*args)
    def mouseMoveEvent(self,event):
        proportional = not not (event.modifiers() & qc.Qt.KeyboardModifierMask.ControlModifier)
        c = numpy.array([event.scenePos().x(),event.scenePos().y()])
        self.parentItem().cornerscale(self.mousePressPos, c,self,proportional)
    def mousePressEvent(self,event):
        self.mousePressPos = numpy.array([event.scenePos().x(),event.scenePos().y()])
        self.parentItem().savetinfo()
class ScaleHandle(Handle):
    pass
class RotateHandle(Handle):
    pass

        
if __name__ == "__main__":
    import sys
    from popupcad.widgets.simplescene import SimpleSceneDialog
    from popupcad.filetypes.solidworksimport import Assembly
    
    app = qg.QApplication(sys.argv)
    grouper = Grouper()
    grouper.setFlag(grouper.ItemIsMovable,True)
    grouper.setFlag(grouper.ItemIsSelectable,True)
    grouper.setPos(500,500)

    mw = SimpleSceneDialog(None,[grouper])
    dummy = Assembly.open()
    sketch = dummy.buildsketch()
    parts = sketch.operationgeometry
    realparts = [item.outputstatic() for item in parts]
    grouper.addchildren(realparts)
    
    mw.show()
