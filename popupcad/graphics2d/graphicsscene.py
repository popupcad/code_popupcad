# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt
import qt.QtCore as qc
import qt.QtGui as qg

import popupcad
from popupcad.graphics2d.static import Static
from popupcad.graphics2d.svg_support import SVGOutputSupport
from popupcad.geometry.vertex import DrawnPoint, ShapeVertex
from popupcad.graphics2d.interactivevertex import DrawingPoint, StaticDrawingPoint
from popupcad.graphics2d.text import TextParent, GenericText

from popupcad.graphics2d.interactivevertex import ReferenceInteractiveVertex
from popupcad.graphics2d.interactiveedge import ReferenceInteractiveEdge

import qt.qt_hacks as qh

class popupCADObjectSupport(object):

    def __init__(self):
        pass

    def removeItem(self, item):
        if item in self.items():
            qg.QGraphicsScene.removeItem(self, item)

    def addItem(self, item):
        qg.QGraphicsScene.addItem(self, item)
        try:
            item.updatescale()
        except AttributeError:
            pass

    def deleteall(self):
        for item in self.items():
            item.harddelete()
        self.update()

    def updateshape(self):
        for item in self.items():
            try:
                item.updateshape()
            except AttributeError:
                pass


class SketcherSupport(object):
    newpolygon = qc.Signal()
    itemclicked = qc.Signal(object)
    enteringeditmode = qc.Signal()
    leavingeditmode = qc.Signal()
    savesnapshot = qc.Signal()
    itemdeleted = qc.Signal()
    refresh_request = qc.Signal()
    constraint_update_request = qc.Signal(list)

    def __init__(self):
        self.setItemIndexMethod(self.NoIndex)
        self.constraints_on = False
        self.setSceneRect(qc.QRectF(0, 0, 1000, 1000))
        self.setBackgroundBrush(qg.QBrush(qg.QColor.fromRgbF(*popupcad.graphics_scene_background_color),qc.Qt.SolidPattern))
        self.temp = None
        self.extraobjects = []
        self.nextgeometry = None

    def connect_mouse_modes(self,view):
        self.newpolygon.connect(view.restoredrag)
        self.leavingeditmode.connect(view.restoredrag)
        self.enteringeditmode.connect(view.turn_off_drag)

    def get_sketch(self):
        return self._sketch

    def set_sketch(self, sketch):
        self._sketch = sketch

    sketch = property(get_sketch, set_sketch)

    def setIsEnabled(self, test):
        for item in self.items():
            if not isinstance(item, Static):
                item.setEnabled(test)

    def addpolygon(self, polygonclass):
        self.nextgeometry = polygonclass

    def keyPressEvent(self, event):
        qg.QGraphicsScene.keyPressEvent(self, event)
        if event.key() == qc.Qt.Key_Delete:
            self.savesnapshot.emit()
            self.delete_selected_items()
            self.itemdeleted.emit()
            event.accept()
        else:
            event.ignore()

    def cut_to_clipboard(self):
        self.copy_to_clipboard()
        self.delete_selected_items()

    def copy_to_clipboard(self):
        self.clipboard = [
            item for item in self.selectedItems() if hasattr(
                item,
                'copy')]

    def delete_selected_items(self):
        [item.softdelete() for item in self.selectedItems()]

    def paste_from_clipboard(self):
        [self.addItem(item.copy()) for item in self.clipboard]

    def deselectall(self):
        [item.setSelected(False) for item in self.selectedItems()]

    def mousePressEvent(self, event):
        pos = event.scenePos()

        if self.temp is not None:
            if event.button() == qc.Qt.LeftButton:
                self.temp.mousepress(pos)

        elif self.nextgeometry is not None:
            if event.button() == qc.Qt.LeftButton:
                if self.temp is None:
                    if self.nextgeometry == TextParent:
                        textpos = ShapeVertex(qh.to_tuple(pos),scaling = 1/popupcad.view_scaling)
                        text = GenericText('',textpos,font='Courier',fontsize=2)
                        temp = self.nextgeometry(text)
                        self.addItem(temp)
                        temp.editmode()

                    elif self.nextgeometry == DrawingPoint:
                        temp = self.nextgeometry(DrawnPoint(qh.to_tuple(pos),scaling = 1/popupcad.view_scaling))
                        self.addItem(temp)
                        self.setFocusItem(temp)
                        temp.updatescale()
                        self.childfinished()
                    else:
                        self.temp = self.nextgeometry()
                        self.addItem(self.temp)
                        self.setFocusItem(self.temp)
                        self.temp.mousepress(pos)
        else:
            qg.QGraphicsScene.mousePressEvent(self, event)
            self.leavingeditmode.emit()

    def mouseMoveEvent(self, event):
        pos = event.scenePos()
        if self.temp is not None:
            self.temp.mousemove(pos)
        else:
            qg.QGraphicsScene.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        pos = event.scenePos()
        if self.temp is not None:
            self.temp.mouserelease(pos)
        else:
            qg.QGraphicsScene.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        pos = event.pos()
        if self.temp is not None:
            self.temp.mousedoubleclick(pos)
        else:
            if not self.constraints_on:
                qg.QGraphicsScene.mouseDoubleClickEvent(self, event)

    def childfinished(self):
        self.newpolygon.emit()
        self.updatevertices()
        self.temp = None

    def cancelcreate(self):
        self.nextgeometry = None
        try:
            self.temp.harddelete()
        except AttributeError:
            pass
        self.temp = None

    def showvertices(self, constraints_on):
        self.constraints_on = constraints_on

    def update_extra_objects(self, extraobjects):
        self.extraobjects = extraobjects

    def updatevertices(self):
        self.removecontrolpoints()
        if self.constraints_on:
            for item in self.items():
                try:
                    item.updatemode(item.modes.mode_defined)
                except AttributeError:
                    pass
                try:
                    for child in item.children():
                        if child not in self.items():
                            self.addItem(child)
                except AttributeError:
                    pass
            for item in self.extraobjects:
                if item not in self.items():
                    self.addItem(item)
        else:
            for item in self.items():
                try:
                    for child in item.children():
                        child.removefromscene()
                except AttributeError:
                    pass
        self.views()[0].updatescaleables()

    def removerefgeoms(self):
        for item in self.items():
            if isinstance(item, Static):
                self.removeItem(item)
            if isinstance(item, StaticDrawingPoint):
                self.removeItem(item)
            if isinstance(item, ReferenceInteractiveVertex):
                self.removeItem(item)
            if isinstance(item, ReferenceInteractiveEdge):
                self.removeItem(item)

    def removecontrolpoints(self):
        for item in self.items():
            if isinstance(item, ReferenceInteractiveVertex):
                self.removeItem(item)
            if isinstance(item, ReferenceInteractiveEdge):
                self.removeItem(item)


class GraphicsScene(popupCADObjectSupport,SVGOutputSupport,SketcherSupport,qg.QGraphicsScene):
    if qt.pyqt_loaded:
        newpolygon = qc.Signal()
        itemclicked = qc.Signal(object)
        enteringeditmode = qc.Signal()
        leavingeditmode = qc.Signal()
        savesnapshot = qc.Signal()
        itemdeleted = qc.Signal()
        refresh_request = qc.Signal()
        constraint_update_request = qc.Signal(list)
    
    def __init__(self):
        qg.QGraphicsScene.__init__(self)
        popupCADObjectSupport.__init__(self)
        SketcherSupport.__init__(self)
#        self.update()


class SimpleGraphicsScene(popupCADObjectSupport, SVGOutputSupport, qg.QGraphicsScene):

    def __init__(self):
        qg.QGraphicsScene.__init__(self)
        popupCADObjectSupport.__init__(self)
