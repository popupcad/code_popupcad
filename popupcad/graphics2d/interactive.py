# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.graphics2d.graphicsitems import Common
from popupcad.graphics2d.graphicsitems import CommonShape
from popupcad.graphics2d.modes import Modes


class InteractiveModes(Modes):
    modelist = []
    modelist.append('mode_defined')
    modelist.append('mode_edit')
    modelist.append('mode_selectable_edges')
    modelist.append('mode_render')


class Interactive(Common, CommonShape, qg.QGraphicsPathItem):
    z_value = 15
    isDeletable = True
    linewidth = 3.0
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    brushstyle = qc.Qt.SolidPattern
    nobrush = qc.Qt.NoBrush
    modes = InteractiveModes()

    boundingrectbuffer = 2

    pendefinedcolor = qg.QColor.fromRgbF(0, 0, 1, 1)
    peneditcolor = qg.QColor.fromRgbF(1, 0, 0, 1)
    penrendercolor = qg.QColor.fromRgbF(0, 0, 0, 1)
    penselectioncolor = qg.QColor.fromRgbF(0, 0, 1, 1)

    brushdefinedcolor = qg.QColor.fromRgbF(1, 1, 0, .25)
    brusheditcolor = qg.QColor.fromRgbF(1, 1, 0, .25)
    brushselectioncolor = qg.QColor.fromRgbF(1, 1, 0, .25)

    pens = {}
    pens[
        modes.mode_defined] = qg.QPen(
        pendefinedcolor,
        linewidth,
        style,
        capstyle,
        joinstyle)
    pens[
        modes.mode_edit] = qg.QPen(
        peneditcolor,
        linewidth,
        style,
        capstyle,
        joinstyle)
    pens[
        modes.mode_render] = qg.QPen(
        penrendercolor,
        1.,
        style,
        capstyle,
        joinstyle)
    pens[
        modes.mode_selectable_edges] = qg.QPen(
        penselectioncolor,
        linewidth,
        style,
        capstyle,
        joinstyle)

    brushes = {}
    brushes[modes.mode_defined] = qg.QBrush(brushdefinedcolor, brushstyle)
    brushes[modes.mode_edit] = qg.QBrush(brusheditcolor, brushstyle)
    brushes[modes.mode_render] = nobrush
    brushes[
        modes.mode_selectable_edges] = qg.QBrush(
        brushselectioncolor,
        brushstyle)

    nobrushes = {}
    nobrushes[modes.mode_defined] = nobrush
    nobrushes[modes.mode_edit] = nobrush
    nobrushes[modes.mode_render] = nobrush
    nobrushes[modes.mode_selectable_edges] = nobrush

    def __init__(self, generic, *args, **kwargs):
        self.generic = generic
        self.selectableedges = []
        super(Interactive, self).__init__(*args, **kwargs)
        self.updatehandles()
        self.changed_trigger = False
        self.setZValue(self.z_value)
        self.setAcceptHoverEvents(True)
        self.updatemode(self.modes.mode_defined)
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsFocusable, True)

    def updatescale(self):
        try:
            self.set_view_scale(1 / self.scene().views()[0].zoom())
        except (IndexError, AttributeError):
            pass

    def exterior(self):
        return self.generic.get_exterior_handles()

    def focusOutEvent(self, event):
        super(Interactive, self).focusOutEvent

    def handles(self):
        return self.generic.get_handles()

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

    def allchildren(self):
        return list(
            set(self.childItems() + self.handles() + self.selectableedges))

    def painterpath(self):
        return self.generic.painterpath()

    def exteriorpoints(self):
        return self.generic.exteriorpoints()

    def hidechildren(self, children):
        for child in children:
            try:
                self.scene().removeItem(child)
            except AttributeError:
                pass

    def showchildren(self, children):
        for child in children:
            try:
                self.scene().addItem(child)
            except AttributeError:
                pass

    def updatechildhandles(self, children):
        for child in children:
            child.updateshape()

    def updatehandles(self):
        for edge in self.selectableedges:
            edge.harddelete()
        self.create_selectable_edges()
        for handle in self.handles():
            handle.setconnection(self)
        for edge in self.selectableedges:
            edge.setconnection(self)
        self.updateshape()

    def querybrush(self):
        return self.brushes[self.mode]

    def querypen(self):
        pen = self.pens[self.mode]
        pen.setCosmetic(True)
        return pen

    def copy(self):
        genericcopy = self.generic.copy(identical=False)
        return genericcopy.outputinteractive()

    def reset(self):
        self.updatemode(self.modes.mode_defined)

    def updatemode(self, mode):
        self.mode = getattr(self.modes, mode)
        self.setPen(self.querypen())
        self.setBrush(self.querybrush())
        self.update()
        self.refreshview()

    def refreshview(self):
        #        for handle in self.handles():
        #            handle.notify()
        self.setEnabled(True)
        self.setZValue(self.z_value)

        if self.mode == self.modes.mode_edit:
            self.showchildren(self.handles())
            for handle in self.handles():
                try:
                    handle.updatescale()
                except AttributeError:
                    pass
        else:
            self.hidechildren(self.handles())

    def mousePressEvent(self, event):
        self.changed_trigger = True
        self.moved_trigger = False
        if self.mode == self.modes.mode_edit:
            add = (
                event.modifiers() & qc.Qt.KeyboardModifierMask.ControlModifier) != 0
            if add:
                self.addvertex(event.scenePos())
        self.scene().itemclicked.emit(self.generic)
        super(Interactive, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        import numpy
        if self.changed_trigger:
            self.changed_trigger = False
            self.moved_trigger = True
            self.scene().savesnapshot.emit()
        dp = event.scenePos() - event.lastScenePos()
        dp = tuple(numpy.array(dp.toTuple()) / popupcad.view_scaling)
        self.generic.constrained_shift(dp, self.constraintsystem())
        self.scene().updateshape()
        super(Interactive, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.changed_trigger = False
        if self.moved_trigger:
            self.scene().constraint_update_request.emit(self.generic.vertices())
            self.moved_trigger = False
        super(Interactive, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(Interactive, self).mouseDoubleClickEvent(event)
        if self.mode == self.modes.mode_defined:
            self.updatemode(self.modes.mode_edit)
            self.scene().enteringeditmode.emit()
        elif self.mode == self.modes.mode_edit:
            self.updatemode(self.modes.mode_defined)
        elif self.mode == self.modes.mode_selectable_edges:
            pass
        else:
            pass
        super(Interactive, self).mouseDoubleClickEvent(event)

    def addvertex(self, qpoint):
        from popupcad.geometry.vertex import ShapeVertex
        import numpy
        v = ShapeVertex(numpy.array(qpoint.toTuple())/popupcad.view_scaling)
        self.generic.addvertex_exterior(v, special=True)
        self.updatehandles()
        self.refreshview()

    def removevertex(self, interactivevertex):
        self.generic.removevertex(interactivevertex.get_generic())
        self.updatehandles()
        self.refreshview()

    def updateshape(self):
        super(Interactive, self).updateshape()
        self.updatechildhandles(self.handles() + self.selectableedges)

    def children(self):
        return self.handles() + self.selectableedges

    def update_bounding_rect(self):
        pass
#
#    def customshape(self):
#        path = self.path()
#        s = qg.QPainterPathStroker()
#        s.setWidth(10 * self.view_scale)
#        return s.createStroke(path)


class InteractivePoly(Interactive):
    pass


class InteractiveCircle(Interactive):
    pass


class InteractiveRect2Point(Interactive):
    pass


class InteractivePath(Interactive):
    brushes = Interactive.nobrushes.copy()

    def create_selectable_edges(self):
        self.create_selectable_edge_path()

#    def shape(self):
#        return self.customshape()

#    def boundingRect(self):
#        return self.shape().boundingRect()

    def updateshape(self):
        super(InteractivePath, self).updateshape()
        self.update_bounding_rect()
        
    def update_bounding_rect(self):
        s = qg.QPainterPathStroker()
        s.setWidth(10 * self.view_scale)
#        self.prepareGeometryChange()
        self._bounding_rect = s.createStroke(self.path()).boundingRect()
        
    def boundingRect(self):
        return self._bounding_rect

class InteractiveLine(Interactive):
    brushes = Interactive.nobrushes.copy()

    def create_selectable_edges(self):
        self.create_selectable_edge_path()

#    def shape(self):
#        return self.customshape()
#
#    def boundingRect(self):
#        return self.shape().boundingRect()

    def updateshape(self):
        from math import atan2, pi
        (x1, y1), (x2, y2) = self.generic.exteriorpoints(
            scaling=popupcad.view_scaling)
        dx = x2 - x1
        dy = y2 - y1
        l = ((dx)**2 + (dy)**2)**.5
        q = atan2(dy, dx)
        d = q * 180 / pi
        self.resetTransform()
        path = qg.QPainterPath()
        poly = qg.QPolygonF([qc.QPointF(0, 0), qc.QPointF(l, 0)])
        path.addPolygon(poly)
        self.setPath(path)
        self.rotate(d)
        xy = self.mapFromScene(x1, y1)
        self.translate(xy.x(), xy.y())
        self.update()
        self.updatechildhandles(self.handles() + self.selectableedges)
        self.update_bounding_rect()

    def update_bounding_rect(self):
        #update bounding_rect        
        s = qg.QPainterPathStroker()
        s.setWidth(10 * self.view_scale)
#        self.prepareGeometryChange()
        self._bounding_rect = s.createStroke(self.path()).boundingRect()

    def boundingRect(self):
        return self._bounding_rect
