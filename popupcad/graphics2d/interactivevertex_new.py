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
    def __init__(self,*args,**kwargs):
        super(InteractiveVertex,self).__init__(*args,**kwargs)
        self.connectedinteractive = None

    def setconnection(self,connectedinteractive):
        self.connectedinteractive = connectedinteractive

    def hoverEnterEvent(self,event):
        super(InteractiveVertex,self).hoverEnterEvent(event)

        if self.connectedinteractive!=None:
            siblings = list(set(self.connectedinteractive.handles())-set([self]))
            self.setZValue(self.z_above)
            for sibling in siblings:        
                sibling.setZValue(sibling.z_below)            
            
    def itemChange(self,change,value):
        result = super(InteractiveVertex,self).itemChange(change,value)
        self.connectedinteractive.updateshape()
        return result

        
    def mousePressEvent(self,event):
        super(InteractiveVertex,self).mousePressEvent(event)

        remove = (event.modifiers() & (qc.Qt.KeyboardModifierMask.ControlModifier))!=0 and (event.modifiers() & (qc.Qt.KeyboardModifierMask.ShiftModifier))
        if remove:
            if self.connectedinteractive!=None:
                self.connectedinteractive.removevertex(self)
            self.removefromscene()
            
    def notify(self):
        self.makemoveable(False)
        if self.connectedinteractive.mode!=None:
            if self.connectedinteractive.mode==self.connectedinteractive.modes.mode_edit:
                self.makemoveable(True)
            else:
                self.removefromscene()

class ReferenceInteractiveVertex(InteractiveVertex):
    pass    