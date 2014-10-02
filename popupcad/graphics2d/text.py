# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
import numpy
from popupcad.graphics2d.graphicsitems import Common

class TextParent(qg.QGraphicsItem,Common):
    def __init__(self,*args,**kwargs):
        super(TextParent,self).__init__(*args,**kwargs)
        self.editmode = False
        self.editchild = TextItem(self)
#        self.editchild.setParent(self)
    def focusOutEvent(self, event):
#        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
#        super(TextItem, self).focusOutEvent(event)
#        s
        text = self.editchild.getText()
        self.editchild.removefromscene()
        a = TextPath(text,self)
    def mouseDoubleClickEvent(self, event):
        self.editchild.setParent(self)
        
#        if self.textInteractionFlags() == qc.Qt.NoTextInteraction:
#            self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        super(TextItem, self).mouseDoubleClickEvent(event)        
        

class TextPath(qg.QGraphicsPathItem):
    def __init__(self,text,*args,**kwargs):
        super(TextPath,self).__init__(*args,**kwargs)
        p = qg.QPainterPath()
        p.addText(qc.QPointF(0,0),qg.QFont(),text)

        p2 = qg.QPainterPath()
        for ii in range(p.elementCount()):
            element = p.elementAt(ii)
            if element.isMoveTo():
                p2.moveTo(element.x,element.y)
            if element.isLineTo():
                p2.lineTo(element.x,element.y)
            if element.isCurveTo():
                p2.lineTo(element.x,element.y)

        self.setPath(p2)

class TextItem(qg.QGraphicsTextItem):
    def __init__(self,*args,**kwargs):
        super(TextItem,self).__init__(*args,**kwargs)        
        self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        font = qg.QFont('Arial', pointSize=1000)
        font.setStyleStrategy(font.ForceOutline)
        self.setFont(font)
        self.scale(1,-1)
        
#    def mouseDoubleClickEvent(self, event):
#        if self.textInteractionFlags() == qc.Qt.NoTextInteraction:
#            self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        super(TextItem, self).mouseDoubleClickEvent(event)        
    def focusOutEvent(self, event):
        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
        super(TextItem, self).focusOutEvent(event)


#class GraphicalElement(qg.QGraphicsTextItem):
#    def __init__(self,*args,**kwargs):
#        super(TextItem,self).__init__(*args,**kwargs)        
#        self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        font = qg.QFont('Arial', pointSize=100)
#        font.setStyleStrategy(font.ForceOutline)
#        self.setFont(font)
#        self.scale(1,-1)
#    def mouseDoubleClickEvent(self, event):
#        if self.textInteractionFlags() == qc.Qt.NoTextInteraction:
#            self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        super(TextItem, self).mouseDoubleClickEvent(event)        
#    def focusOutEvent(self, event):
#        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
#        super(TextItem, self).focusOutEvent(event)
