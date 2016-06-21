# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt

if qt.loaded == 'PyQt4':
    from PyQt4.QtGui import *

#    Code no longer needs this monkeypatching

#    QGraphicsView.DragMode.NoDrag = QGraphicsView.NoDrag 
#    QGraphicsView.DragMode.ScrollHandDrag = QGraphicsView.ScrollHandDrag
#    QGraphicsView.DragMode.RubberBandDrag = QGraphicsView.RubberBandDrag
#    
#    QSizePolicy.Policy.Expanding = QSizePolicy.Expanding 
#    QSizePolicy.Policy.Fixed = QSizePolicy.Fixed 
#    QSizePolicy.Policy.Ignored = QSizePolicy.Ignored 
#    QSizePolicy.Policy.Maximum = QSizePolicy.Maximum 
#    QSizePolicy.Policy.Minimum = QSizePolicy.Minimum 
#    QSizePolicy.Policy.MinimumExpanding = QSizePolicy.MinimumExpanding
#    QSizePolicy.Policy.Preferred = QSizePolicy.Preferred 
#    
#    QTreeWidget.DragDropMode.DragDrop = QTreeWidget.DragDrop 
#    QTreeWidget.DragDropMode.DragOnly = QTreeWidget.DragOnly 
#    QTreeWidget.DragDropMode.DropOnly = QTreeWidget.DropOnly 
#    QTreeWidget.DragDropMode.InternalMove = QTreeWidget.InternalMove 
#    QTreeWidget.DragDropMode.NoDragDrop = QTreeWidget.NoDragDrop 
#
#    QTreeWidget.EditTrigger.NoEditTriggers = QTreeWidget.NoEditTriggers
#    QTreeWidget.EditTrigger.EditKeyPressed = QTreeWidget.EditKeyPressed
#    
#    QListWidget.SelectionBehavior.SelectRows = QListWidget.SelectRows 
#    QListWidget.SelectionMode.SingleSelection = QListWidget.SingleSelection
#    QListWidget.SelectionMode.MultiSelection = QListWidget.MultiSelection    
#    QListWidget.SelectionMode.ExtendedSelection = QListWidget.ExtendedSelection    
#
#    QToolButton.ToolButtonPopupMode.InstantPopup = QToolButton.InstantPopup
#
#    QGraphicsPathItem.GraphicsItemChange.ItemPositionHasChanged = QGraphicsPathItem.ItemPositionHasChanged
#    QPainterPath.ElementType.MoveToElement = QPainterPath.MoveToElement
#    QPainterPath.ElementType.LineToElement = QPainterPath.LineToElement
#    QPainterPath.ElementType.CurveToElement = QPainterPath.CurveToElement
#    QPainterPath.ElementType.CurveToDataElement = QPainterPath.CurveToDataElement
#    
#    QPainter.RenderHint.Antialiasing = QPainter.Antialiasing
#
#    QImage.Format.Format_ARGB32 = QImage.Format_ARGB32
