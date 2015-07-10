# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
import numpy
from popupcad.graphics2d.graphicsitems import Common
import popupcad
from popupcad.geometry.vertex import ShapeVertex


class GenericText(object):
    editable = ['*']
    deletable = ['*']
    hidden = ['id']

    def __init__(self, text, pos, font='Arial', fontsize=1):
        self.text = text
        self.pos = pos
        self.font = font
        self.fontsize = fontsize
        self.exteriors = []
        self.id = id(self)

    def copy(self, identical=True):
        new = type(self)(
            self.text,
            self.pos.copy(identical),
            self.font,
            self.fontsize)
        if identical:
            new.id = self.id
        return new

    def upgrade(self, *args, **kwargs):
        return self

    def isValid(self):
        return True

    def genpath(self,scaling):
        text = self.text
        p = qg.QPainterPath()

        font = qg.QFont(
            self.font,
            pointSize=self.fontsize * scaling)
        p.addText(
            qc.QPointF(
                0,
                1 *
                self.fontsize *
                popupcad.internal_argument_scaling *
                popupcad.view_scaling),
            font,
            text)

        p2 = qg.QPainterPath()
        exteriors = []
        exterior = None

        for ii in range(p.elementCount()):
            element = p.elementAt(ii)
            if popupcad.flip_y:
                dummy = -element.y
            else:
                dummy = element.y

            if element.isMoveTo():
                if exterior is not None:
                    p2.lineTo(exterior[0][0], exterior[0][1])
                    exteriors.append(exterior)
                exterior = [(element.x, dummy)]
                p2.moveTo(element.x, dummy)
            elif element.isLineTo():
                p2.lineTo(element.x, dummy)
                exterior.append((element.x, dummy))
            elif element.isCurveTo():
                p2.lineTo(element.x, dummy)
                exterior.append((element.x, dummy))

        if exterior is not None:
            exteriors.append(exterior)

        exteriors = [(numpy.array(item) + self.pos.getpos()).tolist()
                     for item in exteriors]
        self.exteriors_p = exteriors
        self.exteriors = self.buildvertices(exteriors)
        self.path = p2
        return p2

    def buildvertices(self, exteriors_p):
        exteriors = [[ShapeVertex(pos) for pos in exterior_p]
                     for exterior_p in exteriors_p]
        return exteriors

    def outputinteractive(self):
        tp = TextParent(self)
        return tp

    def outputshapely(self):
        import popupcad.geometry.customshapely as customshapely
        self.genpath(popupcad.internal_argument_scaling*popupcad.csg_processing_scaling)
        objs = [
            customshapely.ShapelyPolygon(
                exterior,
                []) for exterior in self.exteriors_p]
        if len(objs) > 1:
            obj1 = objs.pop(0)
            while objs:
                obj1 = obj1.symmetric_difference(objs.pop(0))
        else:
            obj1 = objs[0]
        return obj1

    def properties(self):
        from dev_tools.propertyeditor import PropertyEditor
        return PropertyEditor(self)


class TextParent(qg.QGraphicsPathItem, Common):
    isDeletable = True

    def __init__(self, generic, *args, **kwargs):
        super(TextParent, self).__init__(*args, **kwargs)
        self.generic = generic
        self.editchild = TextItem(generic, self)
        self.setFlag(qg.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(qg.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(qg.QGraphicsItem.ItemIsFocusable, True)
        self.pen = qg.QPen(
            qg.QColor.fromRgbF(
                0,
                0,
                0,
                1),
            1,
            qc.Qt.SolidLine,
            qc.Qt.RoundCap,
            qc.Qt.RoundJoin)
        self.pen.setCosmetic(True)
        self.brush = qg.QBrush(
            qg.QColor.fromRgbF(
                0, 0, 0, .25), qc.Qt.SolidPattern)
        self.setPen(self.pen)
        self.setBrush(self.brush)
        self.setPos(*self.generic.pos.getpos())
        self.setFlag(self.ItemSendsGeometryChanges, True)
        self.changed_trigger = False

#    def focusInEvent(self,*args,**kwargs):
#        self.editmode()
    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            if self.changed_trigger:
                self.changed_trigger = False
                self.scene().savesnapshot.emit()
            self.generic.pos.setpos(self.pos().toTuple())
        return super(TextParent, self).itemChange(change, value)

    def editmode(self):
        self.setPath(qg.QPainterPath())
        self.editchild.updatefont()
        self.editchild.setParentItem(self)
        self.editchild.resetTransform()
        if popupcad.flip_y:
            self.editchild.scale(1, -1)
        self.editchild.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        self.editchild.setFocus()

    def finish_edit(self):
        self.editchild.setTextInteractionFlags(qc.Qt.NoTextInteraction)
        self.generic.text = self.editchild.toPlainText()
        self.editchild.removefromscene()
        if self.generic.text == '':
            self.harddelete()
        self.refreshview()
#        self.scene().savesnapshot.emit()

    def refreshview(self):
        self.setPath(self.generic.genpath(popupcad.internal_argument_scaling *popupcad.view_scaling))

    def mouseDoubleClickEvent(self, event):
        self.editmode()

    def mousePressEvent(self, event):
        self.changed_trigger = True
        self.scene().itemclicked.emit(self.generic)
        super(TextParent, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.changed_trigger:
            self.changed_trigger = False
        super(TextParent, self).mouseReleaseEvent(event)

    def copy(self):
        genericcopy = self.generic.copy(identical=False)
        return genericcopy.outputinteractive()

    def output_dxf(self,model_space,layer = None):
        pass

class TextItem(qg.QGraphicsTextItem, Common):

    def __init__(self, generic, parent, *args, **kwargs):
        self.generic = generic
        super(TextItem, self).__init__(*args, **kwargs)
        self.setTextInteractionFlags(qc.Qt.TextEditorInteraction)
        self.parent = parent
        self.setPlainText(self.generic.text)
        self.updatefont()

    def focusOutEvent(self, event):
        self.parent.finish_edit()

    def updatefont(self):
        font = qg.QFont(
            self.generic.font,
            pointSize=self.generic.fontsize *
            popupcad.internal_argument_scaling *
            popupcad.view_scaling)
        font.setStyleStrategy(font.ForceOutline)
        self.setFont(font)
