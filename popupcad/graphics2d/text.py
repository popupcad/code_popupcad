# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""


import qt.QtCore as qc
import qt.QtGui as qg
import numpy
from popupcad.graphics2d.graphicsitems import Common
import popupcad
import shapely.geometry as sg
import popupcad.algorithms.painterpath as pp
import qt.qt_hacks as qh

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
        new = type(self)(self.text,self.pos.copy(identical),self.font,self.fontsize)
        if identical:
            new.id = self.id
        return new

    def upgrade(self, *args, **kwargs):
        return self

    def isValid(self):
        return True

    def is_construction(self):
        return False

    def to_generic_polygons(self,add_shift = True):
        text = self.text
#        small font scalings actually produce different paths.  use 10pt font as invariant size
        internal_font = 10
        if text !='':
            p = qg.QPainterPath()
            font = qg.QFont(self.font,pointSize=internal_font)
            p.addText(qc.QPointF(0,internal_font),font,text)
            
            generic_polygons = pp.painterpath_to_generics(p,popupcad.text_approximation)
        else:
            generic_polygons = []
        T = numpy.eye(3)
        T[1,1]=-1
        generic_polygons = [item.transform(T) for item in generic_polygons]
        [item.scale(self.fontsize/internal_font) for item in generic_polygons]
        if add_shift:
            for item in generic_polygons:
                item.shift(self.pos.getpos())
        return generic_polygons
        
    def generic_polys_to_shapely(self,generic_polygons):
        shapelies = [item.to_shapely() for item in generic_polygons]
        
        if len(shapelies) > 1:
            obj1 = shapelies.pop(0)
            while shapelies:
                obj1 = obj1.symmetric_difference(shapelies.pop(0))
        elif len(shapelies) ==1 :
            obj1 = shapelies[0]
        else:
            obj1 = sg.Polygon()
        return obj1

    def to_shapely(self,add_shift = True):
        generic_polygons = self.to_generic_polygons(add_shift)
        shapely = self.generic_polys_to_shapely(generic_polygons)
        return shapely
        
    def to_generics(self,add_shift = True):
        shapely = self.to_shapely(add_shift)
        shapelies = popupcad.algorithms.csg_shapely.condition_shapely_entities(shapely)
        generics = [popupcad.algorithms.csg_shapely.to_generic(item) for item in shapelies]
        return generics

    def painterpath(self,add_shift = True):
        generics = self.to_generics(add_shift)
        p2 = qg.QPainterPath()
        [p2.addPath(item.painterpath()) for item in generics]
        return p2

    def outputinteractive(self):
        tp = TextParent(self)
        return tp

    def properties(self):
        from dev_tools.propertyeditor import PropertyEditor
        return PropertyEditor(self)
        
    def output_dxf(self,model_space,layer = None):
        generics = self.to_generics()
        [item.output_dxf(model_space,layer) for item in generics]

class TextParent(qg.QGraphicsPathItem, Common):
    isDeletable = True

    def __init__(self, generic, *args, **kwargs):
        super(TextParent, self).__init__(*args, **kwargs)
        self.generic = generic
        self.editchild = TextItem(generic, self)
        self.setFlag(qg.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(qg.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(qg.QGraphicsItem.ItemIsFocusable, True)
        self.pen = qg.QPen(qg.QColor.fromRgbF(0,0,0,1),1,qc.Qt.SolidLine,qc.Qt.RoundCap,qc.Qt.RoundJoin)
        self.pen.setCosmetic(True)
        self.brush = qg.QBrush(qg.QColor.fromRgbF(0, 0, 0, .25), qc.Qt.SolidPattern)
        self.setPen(self.pen)
        self.setBrush(self.brush)
        self.setPos(*self.generic.pos.getpos(scaling = popupcad.view_scaling))
        self.setFlag(self.ItemSendsGeometryChanges, True)
        self.changed_trigger = False

#    def focusInEvent(self,*args,**kwargs):
#        self.editmode()
    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            if self.changed_trigger:
                self.changed_trigger = False
                self.scene().savesnapshot.emit()
            self.generic.pos.setpos(qh.to_tuple(self.pos()))
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
        path = self.generic.painterpath(add_shift = False)
        self.setPath(path)
#        path, dummy = self.generic.genpath(popupcad.view_scaling)
#        self.setPath(path)

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
        font = qg.QFont(self.generic.font, pointSize=self.generic.fontsize * popupcad.view_scaling)
        font.setStyleStrategy(font.ForceOutline)
        self.setFont(font)
