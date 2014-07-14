# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from . import modes
from .graphicsitems import Common
#from popupcad.geometry.vertex import Vertex

class InteractiveVertex(qg.QGraphicsEllipseItem,Common):
    radius = 10
    z_below = 100
    z_above = 101
    def __init__(self,symbol,*args,**kwargs):
        try:
            temppos = kwargs.pop('pos')
        except KeyError:
            temppos = None
            
        super(InteractiveVertex,self).__init__(*args,**kwargs)
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
#        self.isInteractive=False
        self.connectedinteractive = None
        self.symbolic = symbol
        self.changed_trigger = False
        if temppos!=None:
            self.setPos(temppos)
        self.setFlag(self.ItemIsSelectable,True)

    def setconnection(self,connectedinteractive):
        self.connectedinteractive = connectedinteractive
    def setstatic(self):
        self.symbolic.setstatic(True)
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
                
    def makemoveable(self,test):
        self.setFlag(self.ItemIsMovable,test)
        self.setFlag(self.ItemSendsGeometryChanges,test)
        
    def hoverEnterEvent(self,event):
        super(InteractiveVertex,self).hoverEnterEvent(event)

        if self.connectedinteractive!=None:
            siblings = list(set(self.connectedinteractive.handles())-set([self]))
            self.setZValue(self.z_above)
            for sibling in siblings:        
                sibling.setZValue(sibling.z_below)            
        self.updatestate(self.states.state_hover)
            
    def hoverLeaveEvent(self,event):
        super(InteractiveVertex,self).hoverLeaveEvent(event)
        self.setZValue(self.z_below)
        self.updatestate(self.states.state_neutral)
        
    def itemChange(self,change,value):
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            if self.changed_trigger:
                self.changed_trigger = False
                self.scene().savesnapshot.emit()
            self.symbolic.setpos(self.pos().toTuple())
            self.connectedinteractive.updateshape()

        return super(InteractiveVertex,self).itemChange(change,value)
        
    def mousePressEvent(self,event):
        super(InteractiveVertex,self).mousePressEvent(event)
        self.changed_trigger = True        
        self.updatestate(self.states.state_pressed)

        self.scene().itemclicked.emit(self.symbolic)

        remove = (event.modifiers() & (qc.Qt.KeyboardModifierMask.ControlModifier))!=0 and (event.modifiers() & (qc.Qt.KeyboardModifierMask.ShiftModifier))
        if remove:
            if self.connectedinteractive!=None:
                self.connectedinteractive.removevertex(self)
            self.removefromscene()
            
    def mouseReleaseEvent(self,event):
        super(InteractiveVertex,self).mouseReleaseEvent(event)    
        self.updatestate(self.states.state_hover)
        self.changed_trigger = False

    def setPos(self,*args):
        super(InteractiveVertex,self).setPos(*args)
        self.updatesymbolic()        

    def updatesymbolic(self):
        self.symbolic.setpos(self.pos().toTuple())
        
    def pos(self):
        pos= super(InteractiveVertex,self).pos()
        return pos

    def updatefromsymbolic(self):
        postuple = self.symbolic.getpos()
        pos = qc.QPointF(*postuple)
        super(InteractiveVertex,self).setPos(pos)

    def setcustomscale(self,scale):
        self.setScale(scale)

    def updatescale(self):
        try:
            self.setcustomscale(1/self.scene().views()[0].zoom())
        except AttributeError:
            pass      

    def notify(self):
        self.makemoveable(False)
        if self.connectedinteractive.mode!=None:
            if self.connectedinteractive.mode==self.connectedinteractive.modes.mode_edit:
                self.makemoveable(True)
            else:
                self.removefromscene()
