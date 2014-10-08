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
from .interactivevertexbase import InteractiveVertexBase

class InteractiveVertex(InteractiveVertexBase):
    radius = 10
    z_below = 100
    z_above = 105
    def __init__(self,*args,**kwargs):
        super(InteractiveVertex,self).__init__(*args,**kwargs)
        self.connectedinteractive = None

    def setconnection(self,connectedinteractive):
        self.connectedinteractive = connectedinteractive
    def hoverEnterEvent(self,event):
        qg.QGraphicsEllipseItem.hoverEnterEvent(self,event)

        if self.connectedinteractive!=None:
            siblings = list(set(self.connectedinteractive.handles())-set([self]))
            self.setZValue(self.z_above)
            for sibling in siblings:        
                sibling.setZValue(sibling.z_below)            
        self.updatestate(self.states.state_hover)
            
    def hoverLeaveEvent(self,event):
        qg.QGraphicsEllipseItem.hoverLeaveEvent(self,event)
        self.setZValue(self.z_below)
        self.updatestate(self.states.state_neutral)
        
    def itemChange(self,change,value):
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            if self.changed_trigger:
                self.changed_trigger = False
                self.scene().savesnapshot.emit()
            self.get_generic().setpos(self.pos().toTuple())
            try:
                self.connectedinteractive.updateshape()
            except AttributeError:
                pass                
            

        return qg.QGraphicsEllipseItem.itemChange(self,change,value)

    def mouseMoveEvent(self,event):
        if self.connectedinteractive.mode!=None:
            if self.connectedinteractive.mode==self.connectedinteractive.modes.mode_edit:
                super(InteractiveVertex,self).mouseMoveEvent(event)
        
    def mousePressEvent(self,event):
        qg.QGraphicsEllipseItem.mousePressEvent(self,event)
        self.changed_trigger = True        
        self.updatestate(self.states.state_pressed)

        self.scene().itemclicked.emit(self.get_generic())

        remove = (event.modifiers() & (qc.Qt.KeyboardModifierMask.ControlModifier))!=0 and (event.modifiers() & (qc.Qt.KeyboardModifierMask.ShiftModifier))
        if remove:
            if self.connectedinteractive!=None:
                self.connectedinteractive.removevertex(self)
            self.removefromscene()
            
#    def notify(self):
#        self.moveable = False
#        if self.connectedinteractive.mode!=None:
#            if self.connectedinteractive.mode==self.connectedinteractive.modes.mode_edit:
#                self.moveable = True
#            else:
#                self.removefromscene()

class InteractiveShapeVertex(InteractiveVertex):
    radius = 10
    z_below = 100
    z_above = 105


class ReferenceInteractiveVertex(InteractiveVertex):
    radius = 10
    z_below = 100
    z_above = 105

