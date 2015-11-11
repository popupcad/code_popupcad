# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt
import qt.QtCore as qc
import qt.QtGui as qg
#import popupcad.graphics2d.modes as modes
#from popupcad.graphics2d.graphicsitems import Common
from popupcad.graphics2d.interactivevertexbase import InteractiveVertexBase


class InteractiveVertex(InteractiveVertexBase):
    radius = 10
    z_below = 100
    z_above = 105

    def __init__(self, *args, **kwargs):
        super(InteractiveVertex, self).__init__(*args, **kwargs)
        self.connectedinteractive = None

    def setconnection(self, connectedinteractive):
        self.connectedinteractive = connectedinteractive

    def hoverEnterEvent(self, event):
        qg.QGraphicsEllipseItem.hoverEnterEvent(self, event)
        if self.connectedinteractive is not None:
            self.setZValue(self.z_above)
        self.updatestate(self.states.state_hover)

    def hoverLeaveEvent(self, event):
        qg.QGraphicsEllipseItem.hoverLeaveEvent(self, event)
        self.setZValue(self.z_below)
        self.updatestate(self.states.state_neutral)

    def mouseMoveEvent(self, event):
        if self.connectedinteractive.mode is not None:
            if self.connectedinteractive.mode == self.connectedinteractive.modes.mode_edit:
                super(InteractiveVertex, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        remove = (
            event.modifiers() & (
                qc.Qt.KeyboardModifierMask.ControlModifier)) != 0 and (
            event.modifiers() & (
                qc.Qt.KeyboardModifierMask.ShiftModifier))
        if remove:
            if self.connectedinteractive is not None:
                self.connectedinteractive.removevertex(self)
            self.removefromscene()
        else:
            super(InteractiveVertex, self).mousePressEvent(event)


class InteractiveShapeVertex(InteractiveVertex):
    radius = 10
    z_below = 100
    z_above = 105


class ReferenceInteractiveVertex(InteractiveVertex):
    radius = 10
    z_below = 100
    z_above = 105


class DrawingPoint(InteractiveVertexBase):
    isDeletable = True
    radius = 5
    z_below = 101
    z_above = 105

    def __init__(self, *args, **kwargs):
        super(DrawingPoint, self).__init__(*args, **kwargs)

    def refreshview(self):
        pass

    def copy(self):
        genericcopy = self.get_generic().copy(identical=False)
        return genericcopy.outputinteractive()


class StaticDrawingPoint(InteractiveVertexBase):
    radius = 5
    z_below = 100
    z_above = 105

    def __init__(self, *args, **kwargs):
        super(StaticDrawingPoint, self).__init__(*args, **kwargs)

    def refreshview(self):
        pass
