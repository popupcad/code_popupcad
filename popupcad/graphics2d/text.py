# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
#import matplotlib.pyplot as plt
#plt.ion()
import numpy

class TextItem(qg.QGraphicsTextItem):
    def __init__(self,*args,**kwargs):
        super(TextItem,self).__init__(*args,**kwargs)        
#        self.setTextInteractionFlags(qc.Qt.NoTextInteraction)
        self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
#        self.setPlainText('asdfasdf')
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
#        self.lostFocus.emit(self)
        super(TextItem, self).focusOutEvent(event)
#    def genpointlists(self):
#        a = self.shape()
#        b = numpy.r_[0:1:100j]
#        c = [a.pointAtPercent(ii) for ii in b]
#        d = [(point.x(),point.y()) for point in c]
#        e = numpy.array(d)
#        plt.plot(*(e.T))
##        b = a.toFillPolygons()
##        c = [poly.toList() for poly in b]
##        d = [[(point.x(),point.y()) for point in poly] for poly in c]
##        return d
#        