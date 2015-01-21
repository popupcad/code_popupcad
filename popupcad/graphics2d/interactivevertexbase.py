# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from . import modes
from popupcad.graphics2d.graphicsitems import Common

class InteractiveVertexBase(qg.QGraphicsEllipseItem,Common):
    radius = 10
    z_below = 100
    z_above = 105
    def __init__(self,symbol,*args,**kwargs):
        try:
            temppos = kwargs.pop('pos')
        except KeyError:
            temppos = None
            
        super(InteractiveVertexBase,self).__init__(*args,**kwargs)
        self.states = modes.EdgeVertexStates()
        self.modes = modes.EdgeVertexModes()
        self.defaultpen = qg.QPen(qg.QColor.fromRgbF(0,0,0,0), 0.0, qc.Qt.PenStyle.NoPen) 
        
        self.setAcceptHoverEvents(True)
        self.setRect(-1.*self.radius/2,-1.*self.radius/2,self.radius,self.radius)
        self.setZValue(self.z_below)

        self.state = self.states.state_neutral
        self.updatemode(self.modes.mode_normal)
        self.updatestate(self.states.state_neutral)
        self.setFlag(self.ItemIsFocusable,True)
        self.changed_trigger = False
        if temppos!=None:
            self.setPos(temppos)
        self.setselectable(True)
        self.generic = symbol
        self.setFlag(self.ItemIsMovable,True)
#        self.setFlag(self.ItemSendsGeometryChanges,True)

    def updatemode(self,mode):
        self.mode = getattr(self.modes,mode)
        self.setPen(self.querypen())
        self.setBrush(self.querybrush())
        self.update()

    def updatestate(self,state):
        self.state = getattr(self.states,state)
        self.setPen(self.querypen())
        self.setBrush(self.querybrush())
        self.update()
        
    def querypen(self):
        if self.mode == self.modes.mode_render:
            pen =  self.defaultpen
        else:
            if self.state == self.states.state_hover:
                pen =  qg.QPen(qg.QColor.fromRgbF(0,0,0,1), 1.0, qc.Qt.SolidLine,qc.Qt.RoundCap, qc.Qt.RoundJoin)  
            if self.state == self.states.state_pressed:
                pen =  qg.QPen(qg.QColor.fromRgbF(0,0,0,1), 1.0, qc.Qt.SolidLine,qc.Qt.RoundCap, qc.Qt.RoundJoin)
            if self.state == self.states.state_neutral:
                pen =  qg.QPen(qg.QColor.fromRgbF(0,0,0,1), 1.0, qc.Qt.SolidLine,qc.Qt.RoundCap, qc.Qt.RoundJoin)  
        pen.setCosmetic(True)
        return pen

    def querybrush(self):
        if self.mode == self.modes.mode_render:
            brush =  qg.QBrush(qg.QColor.fromRgbF(0,0,0, 0), qc.Qt.NoBrush)
        else:
            if self.state == self.states.state_hover:
                brush =  qg.QBrush(qg.QColor.fromRgbF(1,.5,0, 1), qc.Qt.SolidPattern) 
            if self.state == self.states.state_pressed:
                brush =  qg.QBrush(qg.QColor.fromRgbF(1,0,0, 1), qc.Qt.SolidPattern)
            if self.state == self.states.state_neutral:
                brush =  qg.QBrush(qg.QColor.fromRgbF(0,0,0, 1), qc.Qt.SolidPattern) 
        return brush
                
    def setselectable(self,test):
        self.setFlag(self.ItemIsSelectable,test)
        
    def hoverEnterEvent(self,event):
        super(InteractiveVertexBase,self).hoverEnterEvent(event)

        self.updatestate(self.states.state_hover)
            
    def hoverLeaveEvent(self,event):
        super(InteractiveVertexBase,self).hoverLeaveEvent(event)
        self.setZValue(self.z_below)
        self.updatestate(self.states.state_neutral)
        
#    def itemChange(self,change,value):
#        if change == self.GraphicsItemChange.ItemPositionHasChanged:
#            if self.changed_trigger:
#                self.changed_trigger = False
#                self.scene().savesnapshot.emit()
#            self.get_generic().setpos(self.pos().toTuple())
#
#        return super(InteractiveVertexBase,self).itemChange(change,value)
        
    def mousePressEvent(self,event):
        if self.generic.is_moveable():
            self.changed_trigger = True
        self.updatestate(self.states.state_pressed)
        self.scene().itemclicked.emit(self.get_generic())
        super(InteractiveVertexBase,self).mousePressEvent(event)


    def mouseMoveEvent(self,event):
        if self.generic.is_moveable():
            if self.changed_trigger:
                self.changed_trigger = False
                self.scene().savesnapshot.emit()
            dp = event.scenePos() - event.lastScenePos()
            self.generic.constrained_shift(dp.toTuple(),self.constraintsystem())
            self.updateshape()

#        if self.generic.is_moveable():
#            super(InteractiveVertexBase,self).mouseMoveEvent(event)
            
    def mouseReleaseEvent(self,event):
        super(InteractiveVertexBase,self).mouseReleaseEvent(event)    
        self.updatestate(self.states.state_hover)
        self.changed_trigger = False
        self.scene().refresh_request.emit()
        

    def setPos(self,pos):
        self.generic.setpos(pos.toTuple())
        self.updateshape()

    def get_generic(self):
        try:
            return self.generic
        except AttributeError:
            self.generic = self.symbolic
            del self.symbolic
            return self.generic

    
#    def pos(self):
#        pos= super(InteractiveVertexBase,self).pos()
#        return pos

    def updateshape(self):
        postuple = self.get_generic().getpos()
        pos = qc.QPointF(*postuple)
        super(InteractiveVertexBase,self).setPos(pos)

    def setcustomscale(self,scale):
        self.setScale(scale)

    def updatescale(self):
        try:
            self.setcustomscale(1/self.scene().views()[0].zoom())
        except AttributeError:
            pass      


