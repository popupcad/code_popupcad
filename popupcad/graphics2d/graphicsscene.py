# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg

import popupcad
import popupcad.constraints as constraints
from .static import Static
from .svg_support import SVGOutputSupport
from .modes import Modes
from popupcad.graphics2d.interactivevertex import InteractiveVertex
from popupcad.graphics2d.interactiveedge import InteractiveEdge
from .text import TextItem
import time

import numpy

class GraphicsScene(qg.QGraphicsScene,SVGOutputSupport):
    highlightbody=qc.Signal(int)
    mode_select,mode_pan,mode_newgeometry = range(3)
    newpolygon = qc.Signal()
    itemclicked = qc.Signal(object)
    enteringeditmode = qc.Signal()
    leavingeditmode = qc.Signal()
    savesnapshot = qc.Signal()

    def __init__(self):
        super(GraphicsScene,self).__init__()
        self.setSceneRect(qc.QRectF(0, 0, 1000,1000))
        self.setBackgroundBrush(qg.QBrush(qg.QPixmap(popupcad.backgroundpath)))
        self.snaptogrid= False
        self.gridsize = 20
        self.temp = None
        self.update()
        self.setItemIndexMethod(self.NoIndex)
#        self.constraintsystem = constraints.ConstraintSystem()
        self.constraints_on= False
        self.controlpoints = []
        self.controllines = []
        self.nextgeometry = None
    def addItem(self,item):
        super(GraphicsScene,self).addItem(item)
        try:
            item.updatescale()
        except AttributeError:
            pass
        
    def setIsEnabled(self,test):
        for item in self.items():
            if not isinstance(item,Static):
                item.setEnabled(test)
#    def updatescenerect(self):
#        bufferval = .2
#        items = self.items()
#        if len(items)>0:
#            parents = [item for item in items if hasattr(item,'handles') ]
#            nonparents = [item for item in items if not hasattr(item,'handles') ]
#            handles = [handle for item in parents for handle in item.handles]
#            positions=[geom.pos() for geom in nonparents+handles]
#            positions = [[pos.x(),pos.y()] for pos in positions]
#            positions = numpy.array(positions)
#            mins = positions.min(0)
#            maxs = positions.max(0)
#            rect = maxs-mins
#            bufferedrect = rect*(1.+2.*bufferval)
#            llbuffer = mins - rect*bufferval
#            self.setSceneRect(*(llbuffer.tolist()+bufferedrect.tolist()))

#    def wheelEvent(self,event):
#        scenepos =event.scenePos()
#        viewpos = self.views()[0].mapFromScene(event.scenePos())
#        viewpos = qc.QPointF(viewpos)
#        
#        scalefactor = 1.2
#        recenter = True
#        if event.delta()<0:
#            scalefactor = 1./scalefactor
#            recenter = False
#        self.views()[0].updatescale(scalefactor,viewpos,scenepos,recenter)
        
    def deleteall(self):
        for item in self.items():
            item.harddelete()
        self.update()

    def removeItem(self,item):
        self.saferemoveitem(item)
        
    def saferemoveitem(self,item):
        if item in self.items():
            super(GraphicsScene,self).removeItem(item)
                    
    def addpolygon(self,polygonclass):
        self.nextgeometry = polygonclass
        
    def returnpoint(self,point):
        if self.snaptogrid:
            gridsize = 1.*self.gridsize
            gridvalue = ((numpy.array(point.toTuple(),dtype=float)/gridsize).round()*gridsize)
            return qc.QPointF(*gridvalue)
        else:
            return point

#    def updatemouse(self):
#        mousemode = {}
#        mousemode[self.mode_select]=qg.QGraphicsView.DragMode.RubberBandDrag
#        mousemode[self.mode_pan]=qg.QGraphicsView.DragMode.ScrollHandDrag
#        mousemode[self.mode_newgeometry]=qg.QGraphicsView.DragMode.NoDrag
#        [view.setDragMode(mousemode[self.mode]) for view in self.views()]
            
    def screenShot(self):
        import os
        import popupcad
        
        from popupcad.graphics2d.svg_support import OutputSelection

        win = OutputSelection()
        accepted = win.exec_()
        if accepted:
            scaling = win.acceptdata()
        else:
            return
            
        time = popupcad.basic_functions.return_formatted_time()
        filename = os.path.normpath(os.path.join(popupcad.exportdir,'2D_screenshot_'+time+'.svg'))
        self.renderprocess(filename,scaling)

    def keyPressEvent(self,event):
        super(GraphicsScene,self).keyPressEvent(event)
        if event.key() == qc.Qt.Key_Delete:
            self.delete_selected_items()
            
    def cut_to_clipboard(self):
        self.copy_to_clipboard()
        self.delete_selected_items()

    def copy_to_clipboard(self):
        self.clipboard = [item for item in self.selectedItems() if hasattr(item,'copy')]

    def delete_selected_items(self):
        [item.softdelete() for item in self.selectedItems()]

    def paste_from_clipboard(self):
        [self.addItem(item.copy()) for item in self.clipboard]

    def deselectall(self):                
        [item.setSelected(False) for item in self.selectedItems()]
            
    def mousePressEvent(self, event):
        pos = self.returnpoint(event.scenePos())

        if self.temp!=None:
            if event.button() == qc.Qt.LeftButton:
                self.temp.mousepress(pos)            

        elif self.nextgeometry!=None:
            if event.button() == qc.Qt.LeftButton:
                if self.temp==None:
                    if self.nextgeometry==TextItem:
                        temp = self.nextgeometry()
                        self.addItem(temp)
                        self.setFocusItem(temp)
                        temp.setPos(pos)
                        self.nextgeometry = None
                    else:
                        self.temp = self.nextgeometry()
                        self.addItem(self.temp)
                        self.setFocusItem(self.temp)
                        self.temp.mousepress(pos)
                        self.nextgeometry = None
        else:
            super(GraphicsScene,self).mousePressEvent(event)
#            if self.selectedItems()==[]:
#                for item in self.items():
#                    try:
#                        if not self.constraints_on:
#                            item.reset()
#                    except AttributeError:
#                        pass
#                self.leavingeditmode.emit()
#                self.update()
            self.leavingeditmode.emit()

    def mouseMoveEvent(self, event):
        pos = self.returnpoint(event.scenePos())
        if not self.temp==None:
            self.temp.mousemove(pos)
        else:
            super(GraphicsScene,self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = self.returnpoint(event.scenePos())
        if not self.temp==None:
            self.temp.mouserelease(pos)
        else:
            super(GraphicsScene,self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self,event):
        pos = self.returnpoint(event.pos())
        if self.temp!=None:
            self.temp.mousedoubleclick(pos)
        else:
            super(GraphicsScene,self).mouseDoubleClickEvent(event)

    def childfinished(self):
        self.newpolygon.emit()
        self.temp=None

    def cancelcreate(self):
        self.nextgeometry = None
        try:
            self.temp.harddelete()
        except AttributeError:
            pass
        self.temp = None
        
    def showvertices(self):
        if self.constraints_on:        
            self.constraints_on = False
        else:
            self.constraints_on = True

        if self.constraints_on:            
            for item in self.items():
                try:
                    for child in item.children():
                        if not child in self.items():
                            self.addItem(child)
                except AttributeError:
                    pass
            for item in self.controlpoints+self.controllines:
                if not item in self.items():
                    self.addItem(item)
        else:
            for item in self.items():
                try:
                    for child in item.children():
                        child.removefromscene()
                except AttributeError:
                    pass
            for item in self.controlpoints+self.controllines:
                item.removefromscene()
                    
        
        self.views()[0].updatescaleables()

    def removerefgeoms(self):
        for item in self.items():
            if isinstance(item,Static):
                self.removeItem(item)
            if isinstance(item,InteractiveVertex):
                self.removeItem(item)
            if isinstance(item,InteractiveEdge):
                self.removeItem(item)
            