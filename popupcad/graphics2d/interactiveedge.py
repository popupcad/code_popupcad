# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
import PySide.QtCore as qc
import PySide.QtGui as qg
from . import modes
from popupcad.graphics2d.graphicsitems import Common
from math import atan2, pi


class EdgeBase(Common):

    def __init__(self):
        self.states = modes.EdgeVertexStates()
        self.modes = modes.EdgeVertexModes()
        self.defaultpen = qg.QPen(
            qg.QColor.fromRgbF(
                0,
                0,
                0,
                0),
            0.0,
            qc.Qt.PenStyle.NoPen)

    def updatemode(self, mode):
        self.mode = mode
        self.setPen(self.querypen())
        self.update()

    def updatestate(self, state):
        self.state = state
        self.setPen(self.querypen())
        self.update()

    def setLine(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        l = ((dx)**2 + (dy)**2)**.5
        q = atan2(dy, dx)
        d = q * 180 / pi
        self.resetTransform()
        qg.QGraphicsLineItem.setLine(self, 0, 0, l, 0)
        self.rotate(d)
#        r = (x1**2+y1**2)**.5
        xy = self.mapFromScene(x1, y1)
        self.translate(xy.x(), xy.y())


class HighlightedEdge(qg.QGraphicsLineItem, EdgeBase):
    isDeletable = False
    z_below = 52
    linewidth = 2
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin

    def __init__(self, *args, **kwargs):
        super(HighlightedEdge, self).__init__(*args, **kwargs)
        EdgeBase.__init__(self)

        self.state = self.states.state_neutral
        self.updatemode(self.modes.mode_normal)
        self.updatestate(self.states.state_neutral)
        self.setAcceptHoverEvents(False)
        self.setZValue(self.z_below)

    def querypen(self):
        if self.mode == self.modes.mode_render:
            pen = qg.QPen(
                qg.QColor.fromRgbF(
                    0,
                    0,
                    0,
                    1),
                0,
                qc.Qt.PenStyle.NoPen)
        else:
            if self.state == self.states.state_hover:
                pen = qg.QPen(
                    qg.QColor.fromRgbF(
                        1, .5, 0, 1), self.linewidth, self.style, self.capstyle, self.joinstyle)
            if self.state == self.states.state_pressed:
                pen = qg.QPen(
                    qg.QColor.fromRgbF(
                        1,
                        0,
                        0,
                        1),
                    self.linewidth,
                    self.style,
                    self.capstyle,
                    self.joinstyle)
            if self.state == self.states.state_neutral:
                pen = qg.QPen(
                    qg.QColor.fromRgbF(
                        0,
                        0,
                        0,
                        1),
                    self.linewidth,
                    self.style,
                    self.capstyle,
                    self.joinstyle)
        pen.setCosmetic(True)
        return pen

    def setLine(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        l = ((dx)**2 + (dy)**2)**.5
        qg.QGraphicsLineItem.setLine(self, 0, 0, l, 0)


class InteractiveEdge(qg.QGraphicsLineItem, EdgeBase):
    isDeletable = False
    neutral_buffer = 20
    hover_buffer = 30
    z_below = 50
    z_above = 51
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    defaultcolor = qg.QColor.fromRgbF(0, 0, 0, .1)
    nopen = qc.Qt.NoPen
    boundingrectbuffer = 2

    def __init__(self, generic, *args, **kwargs):
        qg.QGraphicsLineItem.__init__(self, *args, **kwargs)
        EdgeBase.__init__(self)

        self.generic = generic

        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsFocusable, True)
        self.setFlag(self.ItemIsSelectable, True)
        self.highlightededge = HighlightedEdge()
        self.highlightededge.setParentItem(self)

        self.state = self.states.state_neutral
        self.updatemode(self.modes.mode_normal)
        self.updatestate(self.states.state_neutral)
        self.setZValue(self.z_below)

        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsFocusable, True)
        self.connectedinteractive = None

        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, False)

        self.changed_trigger = False

#    def shape(self, *args, **kwargs):
#        return super(InteractiveEdge, self).shape(*args, **kwargs)

    def querypen(self):
        if self.mode == self.modes.mode_render:
            return self.nopen
        else:
            hoverpen = qg.QPen(
                self.defaultcolor,
                self.hover_buffer *
                self.view_scale,
                self.style,
                self.capstyle,
                self.joinstyle)
            neutralpen = qg.QPen(
                self.defaultcolor,
                self.neutral_buffer *
                self.view_scale,
                self.style,
                self.capstyle,
                self.joinstyle)

            if self.state == self.states.state_hover:
                return hoverpen
            elif self.state == self.states.state_pressed:
                return hoverpen
            elif self.state == self.states.state_neutral:
                return neutralpen

        return neutralpen

    def set_view_scale(self, view_scale):
        self._view_scale = view_scale
        self.setPen(self.querypen())
        self.update_bounding_rect()

    def get_view_scale(self):
        try:
            return self._view_scale
        except AttributeError:
            self._view_scale = 1
            return self._view_scale

    view_scale = property(get_view_scale,set_view_scale)

#    def boundingRect(self):
#        rect = super(InteractiveEdge, self).boundingRect()
#        a = self.boundingrectbuffer * self.view_scale
#        rect.adjust(-a, -a, a, a)
#        return rect

    def boundingRect(self):
        return self._bounding_rect
        
    def updatescale(self):
        try:
            self.set_view_scale(1 / self.scene().views()[0].zoom())
        except AttributeError:
            pass

    def get_generic(self):
        return self.generic

    def setconnection(self, connectedinteractive):
        self.connectedinteractive = connectedinteractive

    def updatemode(self, mode):
        super(InteractiveEdge, self).updatemode(mode)
        self.highlightededge.updatemode(mode)

    def updatestate(self, state):
        super(InteractiveEdge, self).updatestate(state)
        self.highlightededge.updatestate(state)

    def setLine(self, *args, **kwargs):
        EdgeBase.setLine(self, *args, **kwargs)
        self.highlightededge.setLine(*args, **kwargs)

    def updateshape(self):
        point1 = self.generic.vertex1.getpos(popupcad.view_scaling)
        point2 = self.generic.vertex2.getpos(popupcad.view_scaling)
        self.setLine(point1[0], point1[1], point2[0], point2[1])
        self.update_bounding_rect()
        
    def update_bounding_rect(self):
#        update bounding rect
        rect = super(InteractiveEdge, self).boundingRect()
        a = self.boundingrectbuffer * self.view_scale
        rect.adjust(-a, -a, a, a)
        self._bounding_rect = rect

    def hoverEnterEvent(self, event):
        super(InteractiveEdge, self).hoverEnterEvent(event)
        if self.connectedinteractive is not None:
            #            siblings = list(set(self.connectedinteractive.selectableedges)-set([self]))
            self.setZValue(self.z_above)
#            for sibling in siblings:
#                sibling.setZValue(sibling.z_below)
        self.updatestate(self.states.state_hover)

    def hoverLeaveEvent(self, event):
        super(InteractiveEdge, self).hoverLeaveEvent(event)
        self.updatestate(self.states.state_neutral)
        self.setZValue(self.z_below)

    def mousePressEvent(self, event):
        self.changed_trigger = True
        self.moved_trigger = False
        self.updatestate(self.states.state_pressed)
        if self.ItemIsSelectable == (self.ItemIsSelectable & self.flags()):
            super(InteractiveEdge, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        import numpy
        if self.connectedinteractive.mode is not None:
            if self.connectedinteractive.mode == self.connectedinteractive.modes.mode_edit:
                if self.changed_trigger:
                    self.changed_trigger = False
                    self.moved_trigger = True
                    self.scene().savesnapshot.emit()
                dp = event.scenePos() - event.lastScenePos()
                dp = tuple(numpy.array(dp.toTuple()) / popupcad.view_scaling)
                self.generic.constrained_shift(dp, self.constraintsystem())
#                self.updateshape()
#                try:
#                    self.connectedinteractive.updateshape()
#                except AttributeError:
#                    pass
                self.scene().updateshape()

    def mouseReleaseEvent(self, event):
        self.updatestate(self.states.state_hover)
        if self.ItemIsSelectable == (self.ItemIsSelectable & self.flags()):
            super(InteractiveEdge, self).mouseReleaseEvent(event)
        self.changed_trigger = False
        if self.moved_trigger:
            self.scene().refresh_request.emit()
            self.moved_trigger = False


#    def notify(self):
#        pass


class ReferenceInteractiveEdge(InteractiveEdge):
    pass
