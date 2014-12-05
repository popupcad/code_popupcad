# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import sys
import PySide.QtGui as qg
import numpy
import popupcad
import popupcad.filetypes
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.design import NoOperation
from popupcad.filetypes.design import Design
import popupcad.geometry.customshapely as customshapely
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.filetypes.enum import enum
from popupcad.algorithms.points import calctransformfrom2lines    
from popupcad.filetypes.sketch import Sketch
from  popupcad.widgets.listmanager import SketchListManager,DesignListManager

class Dialog(qg.QDialog):
    def __init__(self,design,prioroperations,sketch = None, subdesign = None,subopref = None,transformtype_x = None,transformtype_y = None,shift = 0,flip = False,scalex = 1.,scaley = 1.):
        super(Dialog,self).__init__()

        if transformtype_x ==None:
            self.transformtype_x = PlaceOperation7.transformtypes.scale            
        else:
            self.transformtype_x = transformtype_x

        if transformtype_y ==None:
            self.transformtype_y = PlaceOperation7.transformtypes.scale            
        else:
            self.transformtype_y = transformtype_y

        self.prioroperations = prioroperations
        self.design = design

        self.designwidget = DesignListManager(design)

        self.optree = DraggableTreeWidget()
        
        self.sketchwidget = SketchListManager(design)

        self.radiobox_scale_x= qg.QRadioButton('Scale X')
        self.radiobox_custom_x= qg.QRadioButton('Custom X')
        self.radiobox_scale_y= qg.QRadioButton('Scale Y')
        self.radiobox_custom_y= qg.QRadioButton('Custom Y')

        self.x_scale_option=qg.QButtonGroup()
        self.x_scale_option.addButton(self.radiobox_scale_x)
        self.x_scale_option.addButton(self.radiobox_custom_x)

        self.y_scale_option=qg.QButtonGroup()
        self.y_scale_option.addButton(self.radiobox_scale_y)
        self.y_scale_option.addButton(self.radiobox_custom_y)

#        custom_layout = qg.QVBoxLayout()
        self.scalex = qg.QLineEdit()
        self.scaley = qg.QLineEdit()
        self.scalex.setText(str(scalex))
        self.scaley.setText(str(scaley))
#        custom_layout.addWidget(self.scalex)        
#        custom_layout.addWidget(self.scaley)        

        templayout1 = qg.QHBoxLayout()
        templayout1.addStretch()        
        templayout1.addWidget(self.radiobox_scale_x)        
        templayout1.addWidget(self.radiobox_custom_x)        
        templayout1.addWidget(self.scalex)        
        templayout1.addStretch()        
        templayout2 = qg.QHBoxLayout()
        templayout2.addStretch()        
        templayout2.addWidget(self.radiobox_scale_y)        
        templayout2.addWidget(self.radiobox_custom_y)        
        templayout2.addWidget(self.scaley)        
        templayout2.addStretch()        

        layout5 = qg.QHBoxLayout()
        layout5.addWidget(qg.QLabel('Flip Layers'))
        self.flip = qg.QCheckBox()
        self.flip.setChecked(flip)
        layout5.addWidget(self.flip)

        layout4 = qg.QHBoxLayout()
        layout4.addWidget(qg.QLabel('Shift Layers'))
        self.sb = qg.QSpinBox()
        self.sb.setRange(-100,100)
        self.sb.setSingleStep(1)
        self.sb.setValue(shift)
        layout4.addWidget(self.sb)

#        layout3 = qg.QHBoxLayout()
#        layout3.addWidget(self.lineedit)
#        layout3.addWidget(button3)

        button1 = qg.QPushButton('Ok')
        button1.pressed.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.pressed.connect(self.reject)

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout = qg.QVBoxLayout()
#        layout.addWidget(qg.QLabel('Design'))
        layout.addWidget(self.designwidget)
        layout.addWidget(qg.QLabel('Sub-Design Operations'))
        layout.addWidget(self.optree)
#        layout.addWidget(qg.QLabel('Sketch'))
        layout.addWidget(self.sketchwidget)
        layout.addLayout(templayout1)
        layout.addLayout(templayout2)
        layout.addLayout(layout5)
        layout.addLayout(layout4)
        layout.addLayout(layout2)
        self.setLayout(layout)

        self.radiobox_scale_x.setChecked(False)
        self.radiobox_custom_x.setChecked(False)
        self.radiobox_scale_y.setChecked(False)
        self.radiobox_custom_y.setChecked(False)

        if self.transformtype_x == PlaceOperation7.transformtypes.scale:
            self.radiobox_scale_x.setChecked(True)
        elif self.transformtype_x == PlaceOperation7.transformtypes.custom:
            self.radiobox_custom_x.setChecked(True)

        if self.transformtype_y == PlaceOperation7.transformtypes.scale:
            self.radiobox_scale_y.setChecked(True)
        elif self.transformtype_y == PlaceOperation7.transformtypes.custom:
            self.radiobox_custom_y.setChecked(True)

#        if self.subdesign != None:
#            self.validatename()
        self.designwidget.itemlist.itemSelectionChanged.connect(self.loadoperations)

        for ii in range(self.designwidget.itemlist.count()):
            item = self.designwidget.itemlist.item(ii)
            if item.value==subdesign:
                item.setSelected(True)
                
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value==sketch:
                item.setSelected(True)

        self.loadoperations()
        try:
            if subopref != None: 
                id, jj = subopref
                if subdesign!=None:
                    ii = subdesign.operation_index(id)
                    self.optree.setCurrentIndeces(ii,jj)
        except NoOperation:
            pass

            
    def subdesign(self):
        try:
            return self.designwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None
            
    def loadoperations(self):
        if len(self.designwidget.itemlist.selectedItems())>0:
            self.optree.linklist(self.subdesign().operations)

    def acceptdata(self):
        if self.radiobox_scale_x.isChecked():
            transformtype_x = PlaceOperation7.transformtypes.scale
        elif self.radiobox_custom_x.isChecked():
            transformtype_x = PlaceOperation7.transformtypes.custom

        if self.radiobox_scale_y.isChecked():
            transformtype_y = PlaceOperation7.transformtypes.scale
        elif self.radiobox_custom_y.isChecked():
            transformtype_y = PlaceOperation7.transformtypes.custom
            
        ii,jj = self.optree.currentIndeces2()[0]  
        subopid = self.subdesign().operations[ii].id    
        subopref = subopid,jj
        return self.sketch().id,self.subdesign().id,subopref,transformtype_x,transformtype_y,self.sb.value(),self.flip.isChecked(),float(self.scalex.text()),float(self.scaley.text())
            
        
class PlaceOperation7(Operation):
    name = 'PlacementOp'
    operationtypes = ['placement']
    transformtypes = enum(scale = 'scale',custom = 'custom')
    def copy(self,identical = True):
        new = PlaceOperation7(self.sketchid,self.subdesignid, self.subopref,self.transformtype_x,self.transformtype_y,self.shift,self.flip,self.scalex,self.scaley)
        new.customname = self.customname
        if identical:
            new.id = self.id
        return new
    def __init__(self,*args):
        super(PlaceOperation7,self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,sketchid,subdesignid,subopref,transformtype_x,transformtype_y,shift,flip,scalex,scaley):
        super(PlaceOperation7,self).editdata()
        self.sketchid = sketchid
        self.subdesignid = subdesignid
        self.subopref = subopref
        self.transformtype_x = transformtype_x
        self.transformtype_y = transformtype_y
        self.shift = shift
        self.flip = flip
        self.scalex = scalex
        self.scaley = scaley

    def operate(self,design):
        import shapely.affinity as aff
        subdesign = design.subdesigns[self.subdesignid]

        locateline = subdesign.findlocateline()

        try:
            designgeometry = subdesign.operations[subdesign.operation_index(self.subopref[0])].output[self.subopref[1]].csg
        except AttributeError:
#            subdesign.reprocessoperations()
            designgeometry = subdesign.operations[subdesign.operation_index(self.subopref[0])].output[self.subopref[1]].csg
            
        sketch = design.sketches[self.sketchid]

        if self.transformtype_x==self.transformtypes.scale:
            scale_x = None
        elif self.transformtype_x==self.transformtypes.custom:
            scale_x = self.scalex

        if self.transformtype_y==self.transformtypes.scale:
            scale_y = None
        elif self.transformtype_y==self.transformtypes.custom:
            scale_y = self.scaley

        lsout = Laminate(design.return_layer_definition())
        step = 1
        if self.flip:
            step = -1
        if self.shift > 0:
            outshift = self.shift
            inshift = 0
        elif self.shift <0:
            outshift = 0
            inshift = -self.shift
        else:
            outshift = 0
            inshift = 0
            
        for layerout,layerin in zip(design.return_layer_definition().layers[outshift:],subdesign.return_layer_definition().layers[::step][inshift:]):
            newgeoms = []
            for geom in sketch.operationgeometry:
                if not geom.is_construction():
                    for designgeom in designgeometry.layer_sequence[layerin].geoms:
                        try:
                            newgeoms.append(aff.affine_transform(designgeom,calctransformfrom2lines(locateline.exteriorpoints(),geom.exteriorpoints(),scale_x = scale_x,scale_y = scale_y)))
                        except IndexError:
                            pass
            newgeoms = customshapely.unary_union_safe(newgeoms)
            newgeoms = popupcad.geometry.customshapely.multiinit(newgeoms)
            lsout.replacelayergeoms(layerout,newgeoms)
            
        return lsout
        
    def parentrefs(self):
        return []
    def subdesignrefs(self):
        return [self.subdesignid]
    def sketchrefs(self):
        return [self.sketchid]

    def fromQTransform(self,tin):
        tout = numpy.array([[tin.m11(),tin.m12(),tin.m13()],[tin.m21(),tin.m22(),tin.m23()],[tin.m31(),tin.m32(),tin.m33()]]).T
        return tout
    def toQTransform(self,tin):
        tout = qg.QTransform(tin[1][1],tin[1][2],tin[1][3],tin[2][1],tin[2][2],tin[2][3],tin[3][1],tin[3][2],tin[3][3])
        return tout
            
    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(design,design.operations)
        return dialog
    def buildeditdialog(self,design):
        sketch = design.sketches[self.sketchid]
        subdesign = design.subdesigns[self.subdesignid]
        dialog = Dialog(design,design.prioroperations(self),sketch = sketch,subdesign = subdesign, subopref = self.subopref, transformtype_x = self.transformtype_x,transformtype_y = self.transformtype_y,shift=self.shift,flip = self.flip,scalex = self.scalex,scaley = self.scaley)
        return dialog
if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    sys.exit(app.exec_())    