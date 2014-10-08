# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.geometry.line import Line
from . import modes
from .graphicsitems import Common

class EdgeBase(Common):
    def __init__(self):
        self.states = modes.EdgeVertexStates()
        self.modes = modes.EdgeVertexModes()
        self.defaultpen = qg.QPen(qg.QColor.fromRgbF(0,0,0,0), 0.0, qc.Qt.PenStyle.NoPen) 
    def updatemode(self,mode):
        self.mode = mode
        self.setPen(self.querypen())
        self.update()
    def updatestate(self,state):
        self.state = state
        self.setPen(self.querypen())
        self.update()     

class HighlightedEdge(qg.QGraphicsLineItem,EdgeBase):
    isDeletable = False
    z_below = 52
    linewidth = 2
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    def __init__(self,*args,**kwargs):
        super(HighlightedEdge,self).__init__(*args,**kwargs)
        EdgeBase.__init__(self)

        self.state = self.states.state_neutral
        self.updatemode(self.modes.mode_normal)
        self.updatestate(self.states.state_neutral)
        self.setAcceptHoverEvents(False)
        self.setZValue(self.z_below)

    def querypen(self):
        if self.mode == self.modes.mode_render:
            pen =  qg.QPen(qg.QColor.fromRgbF(0,0,0,1),0,qc.Qt.PenStyle.NoPen)
        else:
            if self.state == self.states.state_hover:
                pen =  qg.QPen(qg.QColor.fromRgbF(1,.5,0, 1), self.linewidth, self.style,self.capstyle,self.joinstyle)  
            if self.state == self.states.state_pressed:
                pen =  qg.QPen(qg.QColor.fromRgbF(1,0,0, 1), self.linewidth, self.style,self.capstyle,self.joinstyle)      
            if self.state == self.states.state_neutral:
                pen =  qg.QPen(qg.QColor.fromRgbF(0,0,0, 1), self.linewidth, self.style,self.capstyle,self.joinstyle)  
        pen.setCosmetic(True)
        return pen


class InteractiveEdge(qg.QGraphicsLineItem,EdgeBase):
    isDeletable = False
    neutral_buffer = 20
    hover_buffer = 30
    z_below = 50
    z_above = 51
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    defaultcolor = qg.QColor.fromRgbF(0,0,0,0)
    nopen = qc.Qt.NoPen
    boundingrectbuffer = 2
    
    def __init__(self,generic,*args,**kwargs):
        qg.QGraphicsLineItem.__init__(self,*args,**kwargs)
        EdgeBase.__init__(self)

        self.generic = generic

        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsFocusable,True)
        self.setFlag(self.ItemIsSelectable,True)
        self.highlightededge= HighlightedEdge()
        self.highlightededge.setParentItem(self)

        self.scale = 1
        self.state = self.states.state_neutral
        self.updatemode(self.modes.mode_normal)
        self.updatestate(self.states.state_neutral)
        self.setZValue(self.z_below)

        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsFocusable,True)
        self.connectedinteractive = None
        
        self.setFlag(self.ItemIsSelectable,True)
        self.setFlag(self.ItemIsMovable,False)

    def querypen(self):
        if self.mode == self.modes.mode_render:
            return self.nopen
        else:
            hoverpen =  qg.QPen(self.defaultcolor, self.hover_buffer*self.scale, self.style,self.capstyle,self.joinstyle)  
            neutralpen =  qg.QPen(self.defaultcolor, self.neutral_buffer*self.scale, self.style,self.capstyle,self.joinstyle)         

            if self.state == self.states.state_hover:
                return hoverpen
            elif self.state == self.states.state_pressed:
                return hoverpen
            elif self.state == self.states.state_neutral:
                return neutralpen

        return neutralpen

    def setcustomscale(self,scale):
        self.scale = scale
        self.setPen(self.querypen())

    def boundingRect(self):
        rect = super(InteractiveEdge,self).boundingRect()
        a = self.boundingrectbuffer * self.scale
        rect.adjust(-a,-a,a,a)
        return rect

    def updatescale(self):
        try:
            self.setcustomscale(1/self.scene().views()[0].zoom())
        except AttributeError:
            pass            
        
    def get_generic(self):
        return self.generic        
        
    def setconnection(self,connectedinteractive):
        self.connectedinteractive = connectedinteractive

    def makeselectable(self,test):
        self.setFlag(self.ItemIsSelectable,test)

    def updatemode(self,mode):
        super(InteractiveEdge,self).updatemode(mode)
        self.highlightededge.updatemode(mode)
    def updatestate(self,state):
        super(InteractiveEdge,self).updatestate(state)
        self.highlightededge.updatestate(state)
    def setPos(self,*args,**kwargs):
        super(InteractiveEdge,self).setPos(*args,**kwargs)
    def setLine(self,*args,**kwargs):
        super(InteractiveEdge,self).setLine(*args,**kwargs)
        self.highlightededge.setLine(*args,**kwargs)

    def handleupdate(self):
        point1 = self.generic.vertex1.getpos()
        point2 = self.generic.vertex2.getpos()
        self.setLine(point1[0],point1[1],point2[0],point2[1])

    def hoverEnterEvent(self,event):
        super(InteractiveEdge,self).hoverEnterEvent(event)
        if self.connectedinteractive!=None:
            siblings = list(set(self.connectedinteractive.selectableedges)-set([self]))
            self.setZValue(self.z_above)
            for sibling in siblings:        
                sibling.setZValue(sibling.z_below)            
        self.updatestate(self.states.state_hover)
    def hoverLeaveEvent(self,event):
        super(InteractiveEdge,self).hoverLeaveEvent(event)
        self.updatestate(self.states.state_neutral)
        self.setZValue(self.z_below)
    def mousePressEvent(self,event):
        self.updatestate(self.states.state_pressed)
        if self.ItemIsSelectable==(self.ItemIsSelectable & self.flags()):
            super(InteractiveEdge,self).mousePressEvent(event)
    def mouseReleaseEvent(self,event):
        self.updatestate(self.states.state_hover)
        if self.ItemIsSelectable==(self.ItemIsSelectable & self.flags()):
            super(InteractiveEdge,self).mouseReleaseEvent(event)
    def notify(self):
        pass

class ReferenceInteractiveEdge(InteractiveEdge):
    pass