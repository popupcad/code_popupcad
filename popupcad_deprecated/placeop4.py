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
    def __init__(self,design,prioroperations,sketch = None, subdesign = None,subopid = None,transformtype = None,shift = 0,flip = False):
        super(Dialog,self).__init__()

        if sketch == None:
            self.sketch = Sketch()
        else:
            self.sketch = sketch

        if transformtype ==None:
            self.transformtype = PlaceOperation4.transformtypes.place            
        else:
            self.transformtype = transformtype

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

        self.radiobox_place= qg.QRadioButton('Place')
        self.radiobox_stretch = qg.QRadioButton('Stretch')
        self.radiobox_scale= qg.QRadioButton('Scale')

        layout_stretch_scale = qg.QHBoxLayout()
        layout_stretch_scale.addWidget(self.radiobox_place)        
        layout_stretch_scale.addWidget(self.radiobox_stretch)        
        layout_stretch_scale.addWidget(self.radiobox_scale)        

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
        layout.addLayout(layout_stretch_scale)
        layout.addLayout(layout5)
        layout.addLayout(layout4)
        layout.addLayout(layout2)
        self.setLayout(layout)

        self.radiobox_place.setChecked(False)
        self.radiobox_scale.setChecked(False)
        self.radiobox_stretch.setChecked(False)
        if self.transformtype == PlaceOperation4.transformtypes.place:
            self.radiobox_place.setChecked(True)
        elif self.transformtype == PlaceOperation4.transformtypes.stretch:
            self.radiobox_stretch.setChecked(True)
        elif self.transformtype == PlaceOperation4.transformtypes.scale:
            self.radiobox_scale.setChecked(True)

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
    def addsketchop(self,sketch):
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
    def accept(self):
        if self.subdesign != None:
            if self.radiobox_scale.isChecked():
                transformtype = PlaceOperation4.transformtypes.scale
            elif self.radiobox_stretch.isChecked():
                transformtype = PlaceOperation4.transformtypes.stretch
            elif self.radiobox_place.isChecked():
                transformtype = PlaceOperation4.transformtypes.place
            ii = self.combobox.currentIndex()
            self.subopid = self.subdesign.operations[ii].id                

            self.design.sketches[self.sketch.id] = self.sketch
            self.design.subdesigns[self.subdesign.id] = self.subdesign
            
            self.acceptdata = self.sketch.id,self.subdesign.id,self.subopid,transformtype,self.sb.value(),self.flip.isChecked()
            super(Dialog,self).accept()
        else:
            qg.QMessageBox('Please Select a Design')
            
        
class PlaceOperation4(Operation):
    name = 'PlacementOp'
    operationtypes = ['placement']
    transformtypes = enum(place = 'place',stretch = 'stretch',scale = 'scale')
    def copy(self,identical = True):
        new = PlaceOperation4(self.sketchid,self.subdesignid, self.subopid,self.transformtype,self.shift,self.flip)
        new.customname = self.customname
        if identical:
            new.id = self.id
        return new

    def __init__(self,*args):
        super(PlaceOperation4,self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,sketchid,subdesignid,subopid,transformtype,shift,flip):
        super(PlaceOperation4,self).editdata()
        self.sketchid = sketchid
        self.subdesignid = subdesignid
        self.subopid = subopid
        self.transformtype = transformtype
        self.shift = shift
        self.flip = flip

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

        if self.transformtype==self.transformtypes.place:
            scale_x = 1.
            scale_y = 1.
        elif self.transformtype==self.transformtypes.stretch:
            scale_x = None
            scale_y = 1.
        if self.transformtype==self.transformtypes.scale:
            scale_x = None
            scale_y = None

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
                for designgeom in designgeometry.layer_sequence[layerin].geoms:
                    newgeoms.append(aff.affine_transform(designgeom,calctransformfrom2lines(locateline.exteriorpoints(),geom.exteriorpoints(),scale_x = scale_x,scale_y = scale_y)))
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
    def new(cls,parent,design,currentop,newsignal):
        dialog = Dialog(design,design.operations)

        if dialog.exec_()==dialog.Accepted:
            operation = cls(*dialog.acceptdata)
            newsignal.emit(operation)

    def edit(self,parent,design,editedsignal):
        sketch = design.sketches[self.sketchid]
        subdesign = design.subdesigns[self.subdesignid]
        dialog = Dialog(design,design.prioroperations(self),sketch = sketch,subdesign = subdesign, subopid = self.subopid, transformtype = self.transformtype,shift=self.shift,flip = self.flip)
        
        if dialog.exec_()==dialog.Accepted:
            self.editdata(*dialog.acceptdata)
            editedsignal.emit(self)

    def upgrade(self):
        return self.copy()

if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    sys.exit(app.exec_())    