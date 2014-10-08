# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from .graphicsitems import Common
from .graphicsitems import CommonShape
from .modes import Modes

class StaticModes(Modes):
    modelist = []
    modelist.append('mode_default')
    modelist.append('mode_render')

class Static(Common):
    modes = StaticModes()
    pencolor = qg.QColor.fromRgbF(.2,.2,.2, 1)
    linewidth = 1.0
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    
    brushcolor = qg.QColor.fromRgbF(.5,.5,.5,.25)
    brushpattern =  qc.Qt.SolidPattern

    basicpen = qg.QPen(pencolor,linewidth,style,capstyle,joinstyle) 
    basicbrush = qg.QBrush(brushcolor,brushpattern)    
    nobrush = qc.Qt.NoBrush
    
    pens = {}
    pens[modes.mode_default] = basicpen      
    pens[modes.mode_render] =  basicpen

    brushes = {}
    brushes[modes.mode_default] = basicbrush
    brushes[modes.mode_render] = basicbrush

    nobrushes = {}
    nobrushes[modes.mode_default] = nobrush
    nobrushes[modes.mode_render] = nobrush

    z_value = 10
    isDeletable = False
    def __init__(self,generic,*args,**kwargs):
        self.generic = generic
        
        try:
            self.color = kwargs.pop('color')
        except KeyError:
            pass

        super(Static,self).__init__(*args,**kwargs)

        self.setZValue(self.z_value)
        self.setAcceptHoverEvents(True)

        self.setselectable(False)
        self.updatemode(self.modes.mode_default)
        self.updateshape()
        self.setselectable(False)
    def painterpath(self):
        return self.generic.painterpath()
    def exteriorpoints(self):
        return self.generic.exteriorpoints()
        
    def updatemode(self,mode):
        self.mode = getattr(self.modes,mode)
        pen = self.pens[self.mode]
        pen.setCosmetic(True)
        self.setPen(pen)
        brush = qg.QBrush(self.brushes[self.mode])
        try:
            brush.setColor(qg.QColor.fromRgbF(*self.color))
        except AttributeError:
            pass
        
        self.setBrush(brush)
        self.update()
        self.refreshview()

    def setselectable(self,test):
        self.selectable = test

    def updateshape(self):
        super(Static,self).updateshape()

    def refreshview(self):
        self.setEnabled(True)
        self.setZValue(self.z_value)        

        self.setFlag(self.ItemIsMovable,False)
        self.setFlag(self.ItemIsSelectable,False)
        self.setFlag(self.ItemIsFocusable,False)

        if self.selectable:
            self.setFlag(self.ItemIsSelectable,True)

    def mouseDoubleClickEvent(self,event):
        if self.selectable:
            try:
                self.scene().highlightbody.emit(self.generic.id)
            except:
                pass
        else:
            super(Static,self).mouseDoubleClickEvent(event)
            
class StaticPoly(Static,CommonShape,qg.QGraphicsPathItem):
    pass
class StaticCircle(Static,CommonShape,qg.QGraphicsPathItem):
    pass
class StaticRect2Point(Static,CommonShape,qg.QGraphicsPathItem):
    pass
class StaticPath(Static,CommonShape,qg.QGraphicsPathItem):
    brushes = Static.nobrushes.copy()
class StaticLine(Static,CommonShape,qg.QGraphicsPathItem):
    brushes = Static.nobrushes.copy()
