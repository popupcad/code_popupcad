# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg
import popupcad


class ZoomHandling(object):

    def __init__(self, scene):
        self.setScene(scene)
        self.zoomToFit()
        self.setTransformationAnchor(self.NoAnchor)

    def updatescaleables(self):
        for item in self.scene().items():
            try:
                item.view_scale = 1 / self.zoom()
            except AttributeError:
                pass

    def resetTransform(self):
        qg.QGraphicsView.resetTransform(self)
        self.centerOn(0, 0)
        if popupcad.flip_y:
            self.scale(1, -1)
        self.updatescaleables()

    def fitInView(self, *args, **kwargs):
        qg.QGraphicsView.fitInView(self, *args, **kwargs)
        self.updatescaleables()

    def scale(self, *args, **kwargs):
        qg.QGraphicsView.scale(self, *args, **kwargs)
        self.updatescaleables()

    def create_fitted_scene_rect(self, buffer=.1):
        scene_rect = self.scene().itemsBoundingRect()
        if scene_rect.isEmpty():
            width, height = popupcad.view_initial_size
            s2 = popupcad.view_scaling
            scene_rect = qc.QRect(-width / 2  * s2, -height /2  *s2, width  *s2, height *s2)
        else:
            w = scene_rect.width()
            h = scene_rect.height()

            scene_rect.setLeft(scene_rect.left() - w * buffer)
            scene_rect.setRight(scene_rect.right() + w * buffer)
            scene_rect.setTop(scene_rect.top() - h * buffer)
            scene_rect.setBottom(scene_rect.bottom() + h * buffer)
        return scene_rect

    def fit_scene_rect(self, buffer=.1):
        scene_rect = self.create_fitted_scene_rect(buffer)
        values = scene_rect.x(),scene_rect.y(), scene_rect.width(), scene_rect.height()
        self.scene().setSceneRect(*values)
        return scene_rect

    def bound_zoom(self):
        currentzoom = self.zoom()
        if currentzoom > popupcad.zoom_max:
            dz = popupcad.zoom_max / currentzoom
            self.scale(dz, dz)
        elif currentzoom < popupcad.zoom_min:
            dz = popupcad.zoom_min / currentzoom
            self.scale(dz, dz)

    def zoomToFit(self, buffer=.1):
        self.resetTransform()
        scene_rect = self.scene().itemsBoundingRect()
        scene_rect = self.fit_scene_rect(buffer)
        self.fit_scene_rect(buffer)
        self.fitInView(scene_rect.x(),scene_rect.y(), scene_rect.width(), scene_rect.height(), qc.Qt.KeepAspectRatio)
        self.bound_zoom()

    def zoom(self):
        return self.transform().m11()

    def wheelEvent(self, event):
        p1 = event.pos()
        p2 = self.mapToScene(p1)

        if event.delta() < 0:
            zoom = 1. / popupcad.zoom_scale_factor
        else:
            zoom = popupcad.zoom_scale_factor

        newzoom = zoom * self.zoom()

        if newzoom > popupcad.zoom_max:
            zoom = popupcad.zoom_max / self.zoom()
        elif newzoom < popupcad.zoom_min:
            zoom = popupcad.zoom_min / self.zoom()

        self.scale(zoom, zoom)
        p3 = self.mapToScene(p1)

        dx = (p3 - p2).toTuple()
        self.translate(*dx)
        event.accept()


class ImagingSupport(object):

    def __init__(self, scene):
        self.setScene(scene)

    def raster(self, dest, filename, filetype='PNG'):
        import os
        e = self.scene().sceneRect()
        f = self.mapFromScene(e.bottomLeft())
        g = self.mapFromScene(e.topRight())
        rect = qc.QRect(f, g)
        im = qg.QImage(
            rect.width(),
            rect.height(),
            qg.QImage.Format.Format_ARGB32)
        painter = qg.QPainter(im)
        painter.setRenderHint(qg.QPainter.RenderHint.Antialiasing)
        self.scene().render(painter)
        filename = '{0}.{1}'.format(filename, filetype.lower())
        full_path = os.path.normpath(os.path.join(dest, filename))
        im.mirrored().save(full_path, filetype.upper())
        painter.end()
        return full_path


class MouseModes(object):

    def __init__(self, scene):
        self.setScene(scene)
        self.setRubberBandSelectionMode(qc.Qt.ItemSelectionMode.ContainsItemShape)
#        self.setRubberBandSelectionMode(qc.Qt.ItemSelectionMode.IntersectsItemShape)
        self.setRenderHints(
            qg.QPainter.Antialiasing | qg.QPainter.SmoothPixmapTransform)
        self.setDragMode(self.ScrollHandDrag)
        self.rubberband()
        self.scene().newpolygon.connect(self.restoredrag)
        self.scene().leavingeditmode.connect(self.restoredrag)
        self.scene().enteringeditmode.connect(self.turn_off_drag)

    def keyPressEvent(self, event):
        qg.QGraphicsView.keyPressEvent(self, event)
        if event.key() == qc.Qt.Key_Escape:
            self.scene().cancelcreate()
            self.scene().deselectall()
            self.restoredrag()
            event.accept()
        else:
            event.ignore()

    def turn_off_drag(self):
        self.lastdrag = self.dragMode()
        self.setDragMode(qg.QGraphicsView.DragMode.NoDrag)

    def restoredrag(self):
        self.setDragMode(self.lastdrag)
        if self.lastdrag == qg.QGraphicsView.DragMode.ScrollHandDrag:
            self.scene().setIsEnabled(False)
        else:
            self.scene().setIsEnabled(True)

    def scrollhand(self):
        self.lastdrag = qg.QGraphicsView.DragMode.ScrollHandDrag
        self.restoredrag()

    def rubberband(self):
        self.lastdrag = qg.QGraphicsView.DragMode.RubberBandDrag
        self.restoredrag()


class GraphicsView(ZoomHandling, ImagingSupport, MouseModes, qg.QGraphicsView):

    def __init__(self, scene, *args, **kwargs):
        qg.QGraphicsView.__init__(self, *args, **kwargs)
        ZoomHandling.__init__(self, scene)
        ImagingSupport.__init__(self, scene)
        MouseModes.__init__(self, scene)
        self.setSizePolicy(
            qg.QSizePolicy.Policy.MinimumExpanding,
            qg.QSizePolicy.Policy.MinimumExpanding)

    def sizeHint(self):
        return qc.QSize(400, 300)


class SimpleGraphicsView(ZoomHandling, ImagingSupport, qg.QGraphicsView):

    def __init__(self, scene):
        qg.QGraphicsView.__init__(self)
        ZoomHandling.__init__(self, scene)
        ImagingSupport.__init__(self, scene)

if __name__ == '__main__':
    import sys
    app = qg.QApplication(sys.argv)
    scene = popupcad.graphics2d.graphicsscene.GraphicsScene()
    widget = GraphicsView(scene)
    item = qg.QGraphicsRectItem(0, 0, 1000, 1000)
    scene.addItem(item)
    widget.show()
    sys.exit(app.exec_())
