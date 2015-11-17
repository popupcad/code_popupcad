# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:47:02 2015

@author: danaukes
"""

import qt

if qt.pyqt_loaded:
    from PyQt4.QtGui import *

    QGraphicsView.DragMode.NoDrag = 0
    QGraphicsView.DragMode.ScrollHandDrag = 1
    QGraphicsView.DragMode.RubberBandDrag = 2
    
    QSizePolicy.Policy.Expanding = 7
    QSizePolicy.Policy.Fixed = 0
    QSizePolicy.Policy.Ignored = 13
    QSizePolicy.Policy.Maximum = 4
    QSizePolicy.Policy.Minimum = 1
    QSizePolicy.Policy.MinimumExpanding = 3
    QSizePolicy.Policy.Preferred = 5
    
    QTreeWidget.DragDropMode.DragDrop = 3
    QTreeWidget.DragDropMode.DragOnly = 3
    QTreeWidget.DragDropMode.DropOnly = 2
    QTreeWidget.DragDropMode.InternalMove = 4
    QTreeWidget.DragDropMode.NoDragDrop = 0

    QTreeWidget.EditTrigger.NoEditTriggers = QTreeWidget.NoEditTriggers
    QTreeWidget.EditTrigger.EditKeyPressed = QTreeWidget.EditKeyPressed
    
    QListWidget.SelectionBehavior.SelectRows = QListWidget.SelectRows 
    QListWidget.SelectionMode.SingleSelection = QListWidget.SingleSelection
    QListWidget.SelectionMode.MultiSelection = QListWidget.MultiSelection    
    QListWidget.SelectionMode.ExtendedSelection = QListWidget.ExtendedSelection    

    QToolButton.ToolButtonPopupMode.InstantPopup = QToolButton.InstantPopup

    QGraphicsPathItem.GraphicsItemChange.ItemPositionHasChanged = QGraphicsPathItem.ItemPositionHasChanged
    QPainterPath.ElementType.MoveToElement = QPainterPath.MoveToElement
    QPainterPath.ElementType.LineToElement = QPainterPath.LineToElement
    QPainterPath.ElementType.CurveToElement = QPainterPath.CurveToElement
    QPainterPath.ElementType.CurveToDataElement = QPainterPath.CurveToDataElement
    
    QPainter.RenderHint.Antialiasing = QPainter.Antialiasing

    QImage.Format.Format_ARGB32 = QImage.Format_ARGB32

else:
    from PySide.QtGui import *
