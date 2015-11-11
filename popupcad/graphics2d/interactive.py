# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
import qt
import qt.QtCore as qc
import qt.QtGui as qg
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
    _line_width = 3.0
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    brushstyle = qc.Qt.SolidPattern
    modes = InteractiveModes()

    pen_colors = {}
    pen_colors[modes.mode_defined] = (0, 0, 1, 1)
    pen_colors[modes.mode_edit] = (1, 0, 0, 1)
    pen_colors[modes.mode_render] = (0, 0, 0, 1)
    pen_colors[modes.mode_selectable_edges] = (0, 0, 1, 1)

    brush_colors = {}
    brush_colors[modes.mode_defined] = (1, 1, 0, .25)
    brush_colors[modes.mode_edit] = (1, 1, 0, .25)
    brush_colors[modes.mode_render] = (1,1,1,1)
    brush_colors[modes.mode_selectable_edges] = (1, 1, 0, .25)

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
        self.prepareGeometryChange()
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

    def exteriorpoints(self,scaling=1):
        return self.generic.exteriorpoints(scaling)

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
        brush =  qg.QBrush(qg.QColor.fromRgbF(*self.brush_colors[self.mode]), self.brushstyle)
        return brush
        
    def get_line_width(self):
        return self._line_width*self.view_scale
        
    line_width = property(get_line_width)

    def querypen(self):
        pen = qg.QPen(qg.QColor.fromRgbF(*self.pen_colors[self.mode]),self.line_width, self.style,self.capstyle,self.joinstyle)
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
        self.update_bounding_rect()

    def children(self):
        return self.handles() + self.selectableedges

    def update_bounding_rect(self,path=None):
#        update bounding_rect        
        s = qg.QPainterPathStroker()
        s.setWidth(self.line_width*2)
        if path is None:
            path = self.path()
        self._bounding_rect = s.createStroke(path).boundingRect()

    def boundingRect(self):
        return self._bounding_rect


class InteractivePoly(Interactive):
    pass


class InteractiveCircle(Interactive):
    pass


class InteractiveRect2Point(Interactive):
    pass


class InteractivePath(Interactive):
    def querybrush(self):
        return qc.Qt.NoBrush

    def create_selectable_edges(self):
        self.create_selectable_edge_path()
        
class InteractiveLine(Interactive):
    def querybrush(self):
        return qc.Qt.NoBrush

    def create_selectable_edges(self):
        self.create_selectable_edge_path()

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
        self.update_bounding_rect(path)
        self.setPath(path)
        self.rotate(d)
        xy = self.mapFromScene(x1, y1)
        self.translate(xy.x(), xy.y())
        self.update()
        self.updatechildhandles(self.handles() + self.selectableedges)


