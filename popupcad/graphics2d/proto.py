# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.graphics2d.graphicsitems import Common,CommonShape
from popupcad.geometry.vertex import ShapeVertex
from popupcad.filetypes.genericshapes import GenericPoly,GenericPolyline,GenericLine,GenericCircle,GenericTwoPointRect
import popupcad

class Proto(Common):
    z_value = 20
    isDeletable = True
    minradius = 20

    basicpen = qg.QPen(qg.QColor.fromRgbF(0,0,0,1), 1.0, qc.Qt.SolidLine,qc.Qt.RoundCap, qc.Qt.RoundJoin)        
    basicpen.setCosmetic(True)
    
    basicbrush = qg.QBrush(qg.QColor.fromRgbF(1, 1, 0, .25), qc.Qt.SolidPattern)
    nobrush = qc.Qt.NoBrush
  
    def __init__(self,*args,**kwargs):
        super(Proto,self).__init__(*args,**kwargs)
        self.setZValue(self.z_value)
        self.generic = self.shape_class([],[],False,False)
        self.temphandle= None        
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsMovable,True)
        self.setFlag(self.ItemIsSelectable,True)
        self.setFlag(self.ItemIsFocusable,True)
        self.setPen(self.basicpen)
        self.setBrush(self.basicbrush)

    def painterpath(self):
        ep = self.exteriorpoints()
        ip = self.generic.interiorpoints()
        return self.generic.gen_painterpath(ep,ip)
            
    def exteriorpoints(self):
        ep = self.generic.exteriorpoints()
        if self.temphandle!=None:
            ep.append(self.temphandle.pos().toTuple())
        return ep

    def toInteractive(self):
        return self.generic

    def deltemphandle(self):
        if not not self.temphandle:
            self.temphandle.setParentItem(None)
            del self.temphandle
            self.temphandle = None

    def checkdist(self,point0,point1):
        return not popupcad.algorithms.points.twopointsthesame(point0,point1,self.minradius/self.scene().views()[0].zoom())

    def finish_definition(self):
        scene = self.scene()
        self.deltemphandle()
        generic = self.toInteractive()
        scene.addItem(generic.outputinteractive())
        self.harddelete()
        scene.childfinished()

    def mousedoubleclick(self,point):
        self.finish_definition()
        self.updateshape()

    def mouserelease(self,point):
        pass

    def mousemove(self,point):
        if not not self.temphandle:
            self.temphandle.setPos(point)
        self.updateshape()

class ProtoMultiPoint(Proto):
    def addhandle(self,handle):
        if not self.generic.get_exterior():
            self.generic.addvertex_exterior(handle.get_generic())
            self.temphandle = None
        else:
            if handle.pos().toTuple() != self.generic.get_exterior()[-1].getpos():
                if self.checkdist(handle.pos().toTuple(),self.generic.get_exterior()[-1].getpos()):
                    self.generic.addvertex_exterior(handle.get_generic())
                    self.temphandle = None
        
    def mousepress(self,point):
        if not self.temphandle:
            a = ShapeVertex()
            a.setpos(point.toTuple())
            self.temphandle = a.gen_interactive()
            self.temphandle.setParentItem(self)
            self.temphandle.updatescale()
            self.addhandle(self.temphandle)
        else:
            self.addhandle(self.temphandle)
        if not self.temphandle:
            a = ShapeVertex()
            a.setpos(point.toTuple())
            self.temphandle = a.gen_interactive()
            self.temphandle.setParentItem(self)
            self.temphandle.updatescale()

        self.updateshape()
    def mousedoubleclick(self,point):
        if len(self.generic.get_exterior())>2:
            self.finish_definition()
            self.updateshape()
        

class ProtoTwoPoint(Proto):
    def addhandle(self,handle):
        if len(self.generic.get_exterior())==0:
            self.generic.addvertex_exterior(handle.get_generic())
            self.temphandle = None
            return True
        elif len(self.generic.get_exterior())==1:
            if handle.pos().toTuple() != self.generic.get_exterior()[-1].getpos():
                if self.checkdist(handle.pos().toTuple(),self.generic.get_exterior()[-1].getpos()):
                    self.generic.addvertex_exterior(handle.get_generic())
                    self.temphandle = None
                    return True
        else:
            raise(Exception('should never get here'))
            self.temphandle = None
            return True
            
    def mousepress(self,point):
        if not self.temphandle:
            a = ShapeVertex()
            a.setpos(point.toTuple())
            self.temphandle = a.gen_interactive()
            self.temphandle.setParentItem(self)
            self.temphandle.updatescale()
            
        if len(self.generic.get_exterior())==0:
            self.addhandle(self.temphandle)
            a = ShapeVertex()
            a.setpos(point.toTuple())
            self.temphandle = a.gen_interactive()
            self.temphandle.setParentItem(self)
            self.temphandle.updatescale()
            self.updateshape()
            return
            
        elif len(self.generic.get_exterior())==1:
            if self.addhandle(self.temphandle):
                self.finish_definition()
                self.updateshape()
                return

            else:
                return
        else:
            raise(Exception('should never get here'))
            self.finish_definition()
            self.updateshape()
            return
        self.updateshape()
        

class ProtoPoly(ProtoMultiPoint,CommonShape,qg.QGraphicsPathItem):
    shape_class = GenericPoly

class ProtoPath(ProtoMultiPoint,CommonShape,qg.QGraphicsPathItem):
    basicbrush = Proto.nobrush
    shape_class = GenericPolyline
    
class ProtoLine(ProtoTwoPoint,CommonShape,qg.QGraphicsPathItem):
    basicbrush = Proto.nobrush
    shape_class = GenericLine
    
class ProtoCircle(ProtoTwoPoint,CommonShape,qg.QGraphicsPathItem):
    shape_class = GenericCircle

class ProtoRect2Point(ProtoTwoPoint,CommonShape,qg.QGraphicsPathItem):
    shape_class = GenericTwoPointRect
        
            