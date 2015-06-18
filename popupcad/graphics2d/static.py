# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.graphics2d.graphicsitems import Common
from popupcad.graphics2d.graphicsitems import CommonShape


class Static(Common):
    pen_color = (.2, .2, .2, 1)
    linewidth = 1.0
    style = qc.Qt.SolidLine
    capstyle = qc.Qt.RoundCap
    joinstyle = qc.Qt.RoundJoin
    brush_color = (.5, .5, .5, .25)
    brushpattern = qc.Qt.SolidPattern

    z_value = 10
    isDeletable = False

    def __init__(self, generic, *args, **kwargs):

        try:
            self.pen_color = kwargs.pop('pen_color ')
        except KeyError:
            pass
        try:
            self.brush_color = kwargs.pop('brush_color')
        except KeyError:
            pass

        self.generic = generic
        super(Static, self).__init__(*args, **kwargs)
        self.setZValue(self.z_value)
        self.setAcceptHoverEvents(True)
        self.setselectable(False)
        pen = qg.QPen(
            qg.QColor.fromRgbF(
                *self.pen_color),
            self.linewidth,
            self.style,
            self.capstyle,
            self.joinstyle)
        pen.setCosmetic(True)
        self.setPen(pen)
        brush = qg.QBrush(
            qg.QColor.fromRgbF(
                *self.brush_color),
            self.brushpattern)
        self.setBrush(brush)
        self.refreshview()
        self.updateshape()

    def painterpath(self):
        return self.generic.painterpath()

    def exteriorpoints(self):
        return self.generic.exteriorpoints()

    def setselectable(self, test):
        self.selectable = test

    def refreshview(self):
        self.setEnabled(True)
        self.setZValue(self.z_value)

        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemIsSelectable, False)
        self.setFlag(self.ItemIsFocusable, False)

        if self.selectable:
            self.setFlag(self.ItemIsSelectable, True)


class StaticPoly(Static, CommonShape, qg.QGraphicsPathItem):
    pass


class StaticCircle(Static, CommonShape, qg.QGraphicsPathItem):
    pass


class StaticRect2Point(Static, CommonShape, qg.QGraphicsPathItem):
    pass


class StaticPath(Static, CommonShape, qg.QGraphicsPathItem):

    def __init__(self, *args, **kwargs):
        super(StaticPath, self).__init__(*args, **kwargs)
        self.setBrush(qc.Qt.NoBrush)


class StaticLine(Static, CommonShape, qg.QGraphicsPathItem):

    def __init__(self, *args, **kwargs):
        super(StaticLine, self).__init__(*args, **kwargs)
        self.setBrush(qc.Qt.NoBrush)
