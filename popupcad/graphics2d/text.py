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

class TextParent(qg.QGraphicsPathItem,Common):
    def __init__(self,*args,**kwargs):
        super(TextParent,self).__init__(*args,**kwargs)
#        self.editmode = False
        self.editchild = TextItem(self,self)
        self.pathchild = TextPath(self)
        self.pathchild.scale(1,-1)
#        self.editchild.setParent(self)
#    def focusOutEvent(self, event):
##        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
##        super(TextItem, self).focusOutEvent(event)
##        s
#        text = self.editchild.getText()
#        self.editchild.removefromscene()
#        a = TextPath(text,self)
#    def mouseDoubleClickEvent(self, event):
#        self.editchild.setParent(self)
        
#        if self.textInteractionFlags() == qc.Qt.NoTextInteraction:
#            self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        super(TextItem, self).mouseDoubleClickEvent(event)        
#    def refresh
    def focusInEvent(self,*args,**kwargs):        
        self.editMode()
    def editmode(self):
#        if self.pathchild!=None:
#            self.pathchild.harddelete()
#            self.pathchild=None
        self.pathchild.removefromscene()
        
        self.editchild.setParentItem(self)
        self.editchild.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        self.editchild.setFocus()
    def refreshpath(self):
        text = self.editchild.toPlainText()
        self.pathchild.setText(text)
        self.pathchild.setParentItem(self)
        self.editchild.removefromscene()
        

class TextPath(qg.QGraphicsPathItem,Common):
    def __init__(self,parent,*args,**kwargs):
        super(TextPath,self).__init__(*args,**kwargs)
        self.parent = parent
#        self.setText(text)
        
    def setText(self,text):
        p = qg.QPainterPath()

        font = qg.QFont('Arial', pointSize=1000)
        p.addText(qc.QPointF(0,0),font,text)

        p2 = qg.QPainterPath()
        for ii in range(p.elementCount()):
            element = p.elementAt(ii)
            if element.isMoveTo():
                p2.moveTo(element.x,element.y)
            elif element.isLineTo():
                p2.lineTo(element.x,element.y)
            elif element.isCurveTo():
                p2.lineTo(element.x,element.y)

        self.setPath(p2)
    def mouseDoubleClickEvent(self, event):
        self.parent.editmode()
        

class TextItem(qg.QGraphicsTextItem,Common):
    def __init__(self,parent,*args,**kwargs):
        super(TextItem,self).__init__(*args,**kwargs)        
        self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        font = qg.QFont('Arial', pointSize=1000)
        font.setStyleStrategy(font.ForceOutline)
        self.setFont(font)
        self.scale(1,-1)
        self.parent = parent
#    def mouseDoubleClickEvent(self, event):
#        if self.textInteractionFlags() == qc.Qt.NoTextInteraction:
#            self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        super(TextItem, self).mouseDoubleClickEvent(event)        
    def focusOutEvent(self, event):
        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
        self.parent.refreshpath()
#        super(TextItem, self).focusOutEvent(event)


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
