# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:06:44 2015

@author: danaukes
"""
import sys
if '--PyQt4' in sys.argv:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    import PyQt4.QtSvg as QtSvg

    QtCore.Signal = QtCore.SIGNAL
    
    QtCore.Qt.ItemSelectionMode.ContainsItemShape = 0
    QtCore.Qt.ItemSelectionMode.IntersectsItemShape = 1
    QtCore.Qt.ItemSelectionMode.ContainsItemBoundingRect = 2
    QtCore.Qt.ItemSelectionMode.IntersectsItemBoundingRect = 3

    QtGui.QGraphicsView.DragMode.NoDrag = 0
    QtGui.QGraphicsView.DragMode.ScrollHandDrag = 1
    QtGui.QGraphicsView.DragMode.RubberBandDrag = 2
    
    loaded = 'PyQt4'
else:
    import PySide.QtGui as QtGui
    import PySide.QtCore as QtCore
    import PySide.QtSvg as QtSvg
    loaded = 'PySide'
