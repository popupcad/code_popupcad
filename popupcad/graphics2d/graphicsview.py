# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg
import popupcad

class GraphicsView(qg.QGraphicsView):
    zoom_max = popupcad.zoom_max
    zoom_default = popupcad.zoom_default
    zoom_min = popupcad.zoom_min
    scale_factor = 1.2
    def __init__(self,*args,**kwargs):
        super(GraphicsView,self).__init__(*args,**kwargs)
#        self.setMinimumWidth(200)
        self.setSizePolicy(qg.QSizePolicy.Policy.MinimumExpanding,qg.QSizePolicy.Policy.MinimumExpanding)
#        self.setRubberBandSelectionMode(qc.Qt.ItemSelectionMode.IntersectsItemShape)
        self.setRubberBandSelectionMode(qc.Qt.ItemSelectionMode.ContainsItemShape)
        self.setRenderHints(qg.QPainter.Antialiasing | qg.QPainter.SmoothPixmapTransform)
        self.setDragMode(self.ScrollHandDrag)
        self.resetTransform()
        self.rubberband()        
        self.scene().newpolygon.connect(self.restoredrag)
        self.scene().leavingeditmode.connect(self.restoredrag)
        self.scene().enteringeditmode.connect(self.turn_off_drag)
        self.zoomToFit()
            
    def keyPressEvent(self,event):
        super(GraphicsView,self).keyPressEvent(event)
        if event.key() == qc.Qt.Key_Escape:
            self.scene().cancelcreate()
            self.scene().deselectall()
            self.restoredrag()

    def updatescaleables(self):
        [item.setcustomscale(1/self.zoom()) for item in self.scene().items() if hasattr(item,'setcustomscale')]

    def wheelEvent(self,event):
        super(GraphicsView,self).wheelEvent(event)
        if event.delta()<0:
            zoom = 1./self.scale_factor
        else:
            zoom = self.scale_factor

        newzoom = zoom*self.zoom()

        if newzoom>self.zoom_max:
            zoom=self.zoom_max/self.zoom()
        elif newzoom<self.zoom_min:
            zoom=self.zoom_min/self.zoom()
            
        self.scale(zoom,zoom)

    def mousePressEvent(self, event):
        super(GraphicsView,self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(GraphicsView,self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super(GraphicsView,self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self,event):
        super(GraphicsView,self).mouseDoubleClickEvent(event)
    
    def turn_off_drag(self):
        self.lastdrag = self.dragMode()
        self.setDragMode(qg.QGraphicsView.DragMode.NoDrag)

    def restoredrag(self):
        self.setDragMode(self.lastdrag)
        if self.lastdrag==qg.QGraphicsView.DragMode.ScrollHandDrag:
            self.scene().setIsEnabled(False)
        else:
            self.scene().setIsEnabled(True)

    def scrollhand(self):
        self.lastdrag = qg.QGraphicsView.DragMode.ScrollHandDrag
        self.restoredrag()

    def rubberband(self):
        self.lastdrag = qg.QGraphicsView.DragMode.RubberBandDrag
        self.restoredrag()

    def zoomToFit(self):
        scene = self.scene()
        for item in scene.items():
            item.resetTransform()
        self.resetTransform()
        scene.setSceneRect(scene.itemsBoundingRect())
        scene_rect = scene.sceneRect()
        self.fitInView(scene_rect, qc.Qt.KeepAspectRatio)

        if scene_rect.width()==0 and scene_rect.height()==0:
            currentzoom = self.zoom()
            if currentzoom>self.zoom_default:
                dz = self.zoom_default/currentzoom
                self.scale(dz,dz)
            elif currentzoom<self.zoom_min:
                dz = self.zoom_min/currentzoom
                self.scale(dz,dz)            
        else:
            currentzoom = self.zoom()
            if currentzoom>self.zoom_max:
                dz = self.zoom_max/currentzoom
                self.scale(dz,dz)
            elif currentzoom<self.zoom_min:
                dz = self.zoom_min/currentzoom
                self.scale(dz,dz)
        self.scale(1/self.scale_factor,1/self.scale_factor)
        
    def resetTransform(self):
        super(GraphicsView,self).resetTransform()
        self.centerOn(0,0)
        if popupcad.flip_y:
            self.scale(1,-1)
        self.updatescaleables()                
    
    def fitInView(self,*args,**kwargs): 
        super(GraphicsView,self).fitInView(*args,**kwargs)
        self.updatescaleables()                

    def scale(self,*args,**kwargs):
        super(GraphicsView,self).scale(*args,**kwargs)
        self.updatescaleables()  
        
    def zoom(self):
        return self.transform().m11()

    def sizeHint(self):
        return qc.QSize(400,300)
        