# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
import numpy

class TextItem(qg.QGraphicsTextItem):
    def __init__(self,*args,**kwargs):
        super(TextItem,self).__init__(*args,**kwargs)        
        self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        font = qg.QFont('Arial', pointSize=100)
        font.setStyleStrategy(font.ForceOutline)
        self.setFont(font)
        self.scale(1,-1)
    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == qc.Qt.NoTextInteraction:
            self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        super(TextItem, self).mouseDoubleClickEvent(event)        
    def focusOutEvent(self, event):
        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
        super(TextItem, self).focusOutEvent(event)
