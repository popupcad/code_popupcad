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

from popupcad.filetypes.enum import enum
from popupcad.algorithms.points import calctransformfrom2lines    
from popupcad.filetypes.sketch import Sketch

    
class Dialog(qg.QDialog):
    def __init__(self,design,prioroperations,sketch = None, subdesign = None,subopid = None,transformtype_x = None,transformtype_y = None,shift = 0,flip = False,scalex = 1.,scaley = 1.):
        super(Dialog,self).__init__()

        if sketch == None:
            self.sketch = Sketch()
        else:
            self.sketch = sketch

        if transformtype_x ==None:
            self.transformtype_x = PlaceOperation6.transformtypes.scale            
        else:
            self.transformtype_x = transformtype_x

        if transformtype_y ==None:
            self.transformtype_y = PlaceOperation6.transformtypes.scale            
        else:
            self.transformtype_y = transformtype_y

        self.combobox = qg.QComboBox()

        self.subdesign = subdesign
        self.subopid = subopid
        self.prioroperations = prioroperations
        self.design = design

        self.lineedit = qg.QLineEdit()
        self.lineedit.setReadOnly(True)
        button3 = qg.QPushButton('...')
        button3.pressed.connect(self.getfile)

        button_sketch = qg.QPushButton('Edit Sketch')
        button_sketch.pressed.connect(self.opensketch)

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
        templayout1.addWidget(self.radiobox_scale_x)        
        templayout1.addWidget(self.radiobox_custom_x)        
        templayout1.addWidget(self.scalex)        
        templayout2 = qg.QHBoxLayout()
        templayout2.addWidget(self.radiobox_scale_y)        
        templayout2.addWidget(self.radiobox_custom_y)        
        templayout2.addWidget(self.scaley)        

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

        layout3 = qg.QHBoxLayout()
        layout3.addWidget(self.lineedit)
        layout3.addWidget(button3)

        button1 = qg.QPushButton('Ok')
        button1.pressed.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.pressed.connect(self.reject)

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addLayout(layout3)
        layout.addWidget(self.combobox)
        layout.addWidget(button_sketch)
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

        if self.transformtype_x == PlaceOperation6.transformtypes.scale:
            self.radiobox_scale_x.setChecked(True)
        elif self.transformtype_x == PlaceOperation6.transformtypes.custom:
            self.radiobox_custom_x.setChecked(True)

        if self.transformtype_y == PlaceOperation6.transformtypes.scale:
            self.radiobox_scale_y.setChecked(True)
        elif self.transformtype_y == PlaceOperation6.transformtypes.custom:
            self.radiobox_custom_y.setChecked(True)

        if self.subdesign != None:
            self.validatename()
            
    def opensketch(self):
        from popupcad.guis.sketcher import Sketcher
        try:
            seededrefop = self.prioroperations[-1].id
        except IndexError:
            seededrefop = None
        self.sketcherdialog = Sketcher(self,self.sketch,self.design,accept_method=self.addsketchop,selectops = True)
        self.sketcherdialog.show()
        self.sketcherdialog.activateWindow()
        self.sketcherdialog.raise_() 
    def addsketchop(self,sketch,ii,jj):
        self.sketch = sketch
    def validatename(self):
        self.combobox.clear()
        self.combobox.addItems([str(op) for op in self.subdesign.operations])
        try:
            ii = self.subdesign.operation_index(self.subopid)
        except NoOperation:
            self.subopid = self.subdesign.findlastdesignop().id
            ii = self.subdesign.operation_index(self.subopid)
        self.combobox.setCurrentIndex(ii)                
        self.lineedit.setText(self.subdesign.get_basename())
    def getfile(self):
        design = Design.open(self)
        if design != None:
            self.subdesign = design
            self.validatename()
        else:
            self.subdesign = None
    def acceptdata(self):
        if self.radiobox_scale_x.isChecked():
            transformtype_x = PlaceOperation6.transformtypes.scale
        elif self.radiobox_custom_x.isChecked():
            transformtype_x = PlaceOperation6.transformtypes.custom

        if self.radiobox_scale_y.isChecked():
            transformtype_y = PlaceOperation6.transformtypes.scale
        elif self.radiobox_custom_y.isChecked():
            transformtype_y = PlaceOperation6.transformtypes.custom
            
        ii = self.combobox.currentIndex()
        self.subopid = self.subdesign.operations[ii].id                

        self.design.sketches[self.sketch.id] = self.sketch
        self.design.subdesigns[self.subdesign.id] = self.subdesign
        
        return self.sketch.id,self.subdesign.id,self.subopid,transformtype_x,transformtype_y,self.sb.value(),self.flip.isChecked(),float(self.scalex.text()),float(self.scaley.text())
            
        
class PlaceOperation6(Operation):
    name = 'PlacementOp'
    operationtypes = ['placement']
    transformtypes = enum(scale = 'scale',custom = 'custom')
    def copy(self,identical = True):
        new = PlaceOperation6(self.sketchid,self.subdesignid, self.subopid,self.transformtype_x,self.transformtype_y,self.shift,self.flip,self.scalex,self.scaley)
        new.customname = self.customname
        if identical:
            new.id = self.id
        return new
    def __init__(self,*args):
        super(PlaceOperation6,self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,sketchid,subdesignid,subopid,transformtype_x,transformtype_y,shift,flip,scalex,scaley):
        super(PlaceOperation6,self).editdata()
        self.sketchid = sketchid
        self.subdesignid = subdesignid
        self.subopid = subopid
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
            designgeometry = subdesign.operations[subdesign.operation_index(self.subopid)].output[self.getoutputref()].csg
        except AttributeError:
            subdesign.reprocessoperations()
            designgeometry = subdesign.operations[subdesign.operation_index(self.subopid)].output[self.getoutputref()].csg
            
        sketch = design.sketches[self.sketchid]

        if self.transformtype_x==self.transformtypes.scale:
            scale_x = None
        elif self.transformtype_x==self.transformtypes.custom:
            scale_x = self.scalex

        if self.transformtype_y==self.transformtypes.scale:
            scale_y = None
        elif self.transformtype_y==self.transformtypes.custom:
            scale_y = self.scaley

        lsout = Laminate(design.layerdef())
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
            
        for layerout,layerin in zip(design.layerdef().layers[outshift:],subdesign.layerdef().layers[::step][inshift:]):
            newgeoms = []
            for geom in sketch.operationgeometry:
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
        dialog = Dialog(design,design.prioroperations(self),sketch = sketch,subdesign = subdesign, subopid = self.subopid, transformtype_x = self.transformtype_x,transformtype_y = self.transformtype_y,shift=self.shift,flip = self.flip,scalex = self.scalex,scaley = self.scaley)
        return dialog
if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    sys.exit(app.exec_())    