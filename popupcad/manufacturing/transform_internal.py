# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import sys
import PySide.QtGui as qg
import popupcad
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from dev_tools.enum import enum
from popupcad.widgets.listmanager import SketchListManager

class Dialog(qg.QDialog):

    def __init__(self,design,prioroperations,placeop = None):
        super(Dialog, self).__init__()

        if placeop is None:
            self.placeop=TransformInternal(None,None,TransformInternal.transformtypes.scale,TransformInternal.transformtypes.scale,0,False,1.,1.)
        else:
            self.placeop = placeop

        self.prioroperations = prioroperations
        self.design = design

        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(prioroperations)

        self.sketchwidget_from = SketchListManager(design)
        self.sketchwidget_to = SketchListManager(design)

        self.radiobox_scale_x = qg.QRadioButton('Scale X')
        self.radiobox_custom_x = qg.QRadioButton('Custom X')
        self.radiobox_scale_y = qg.QRadioButton('Scale Y')
        self.radiobox_custom_y = qg.QRadioButton('Custom Y')

        self.x_scale_option = qg.QButtonGroup()
        self.x_scale_option.addButton(self.radiobox_scale_x)
        self.x_scale_option.addButton(self.radiobox_custom_x)

        self.y_scale_option = qg.QButtonGroup()
        self.y_scale_option.addButton(self.radiobox_scale_y)
        self.y_scale_option.addButton(self.radiobox_custom_y)

#        custom_layout = qg.QVBoxLayout()
        self.scalex = qg.QLineEdit()
        self.scaley = qg.QLineEdit()

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
        layout5.addWidget(self.flip)

        layout4 = qg.QHBoxLayout()
        layout4.addWidget(qg.QLabel('Shift Layers'))
        self.sb = qg.QSpinBox()
        self.sb.setRange(-100, 100)
        self.sb.setSingleStep(1)
        layout4.addWidget(self.sb)

        button1 = qg.QPushButton('Ok')
        button1.clicked.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.clicked.connect(self.reject)

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Operations'))
        layout.addWidget(self.operation_list)
#        layout.addWidget(qg.QLabel('Sketch'))
        layout.addWidget(self.sketchwidget_from)
        layout.addWidget(self.sketchwidget_to)
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

        if self.placeop.transformtype_x == TransformInternal.transformtypes.scale:
            self.radiobox_scale_x.setChecked(True)
        elif self.placeop.transformtype_x == TransformInternal.transformtypes.custom:
            self.radiobox_custom_x.setChecked(True)

        if self.placeop.transformtype_y == TransformInternal.transformtypes.scale:
            self.radiobox_scale_y.setChecked(True)
        elif self.placeop.transformtype_y == TransformInternal.transformtypes.custom:
            self.radiobox_custom_y.setChecked(True)

        if self.placeop.sketch_links is not None:
            sketch_from = self.design.sketches[self.placeop.sketch_links['sketch_from'][0]]
            sketch_to = self.design.sketches[self.placeop.sketch_links['sketch_to'][0]]

            for ii in range(self.sketchwidget_from.itemlist.count()):
                item = self.sketchwidget_from.itemlist.item(ii)
                if item.value == sketch_from:
                    item.setSelected(True)
    
            for ii in range(self.sketchwidget_to.itemlist.count()):
                item = self.sketchwidget_to.itemlist.item(ii)
                if item.value == sketch_to:
                    item.setSelected(True)

        if self.placeop.operation_links is not None:
            id, jj = self.placeop.operation_links['from'][0]
            ii = design.operation_index(id)
            self.operation_list.selectIndeces([(ii, jj)])

        self.scalex.setText(str(self.placeop.scalex))
        self.scaley.setText(str(self.placeop.scaley))
        self.flip.setChecked(self.placeop.flip)
        self.sb.setValue(self.placeop.shift)
        self.sketchwidget_from.items_updated.connect(lambda:self.sketchwidget_to.refresh_list(retain_selection=True))
        self.sketchwidget_to.items_updated.connect(lambda:self.sketchwidget_from.refresh_list(retain_selection=True))
        
    def build_sketch_links(self):
        try:
            sketch_links = {}
            sketch_links['sketch_from']=[self.sketchwidget_from.itemlist.selectedItems()[0].value.id]
            sketch_links['sketch_to']=[self.sketchwidget_to.itemlist.selectedItems()[0].value.id]
            return sketch_links
        except IndexError:
            return None

    def acceptdata(self):
        if self.radiobox_scale_x.isChecked():
            transformtype_x = TransformInternal.transformtypes.scale
        elif self.radiobox_custom_x.isChecked():
            transformtype_x = TransformInternal.transformtypes.custom

        if self.radiobox_scale_y.isChecked():
            transformtype_y = TransformInternal.transformtypes.scale
        elif self.radiobox_custom_y.isChecked():
            transformtype_y = TransformInternal.transformtypes.custom

        ii, jj = self.operation_list.currentIndeces2()[0]
        opid = self.design.operations[ii].id
        opref = opid, jj
        operation_links = {'from':[opref]}
        sketch_links = self.build_sketch_links()
        
        shift = self.sb.value()
        flip = self.flip.isChecked()
        scale_x = float(self.scalex.text())
        scale_y = float(self.scaley.text())
                      
        return sketch_links, operation_links,transformtype_x, transformtype_y, shift, flip, scale_x, scale_y


class TransformInternal(Operation2):
    name = 'PlaceOp(Internal)'
    operationtypes = ['placement']
    transformtypes = enum(scale='scale', custom='custom')

    def copy(self):
        new = TransformInternal(self.sketch_links,self.operation_links,self.transformtype_x,self.transformtype_y,self.shift,self.flip,self.scalex,self.scaley)
        new.customname = self.customname
        new.id = self.id
        return new

    def __init__(self, *args):
        super(TransformInternal, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,sketch_links,operation_links,transformtype_x,transformtype_y,shift,flip,scalex,scaley):
        super(TransformInternal, self).editdata(operation_links, sketch_links,{})
        self.transformtype_x = transformtype_x
        self.transformtype_y = transformtype_y
        self.shift = shift
        self.flip = flip
        self.scalex = scalex
        self.scaley = scaley

    def operate(self, design):
        opref,output = self.operation_links['from'][0]
        CSG = design.op_from_ref(opref).output[output].csg

        sketch_from_id = self.sketch_links['sketch_from'][0]
        sketch_to_id = self.sketch_links['sketch_to'][0]

        sketch_from = design.sketches[sketch_from_id]
        sketch_to = design.sketches[sketch_to_id]
        
        for geom in sketch_from.operationgeometry:
            if not geom.is_construction():
                geom_from = geom
                break

        geoms_to = [geom for geom in sketch_to.operationgeometry if not geom.is_construction()]

        if self.transformtype_x == self.transformtypes.scale:
            scale_x = None
        elif self.transformtype_x == self.transformtypes.custom:
            scale_x = self.scalex

        if self.transformtype_y == self.transformtypes.scale:
            scale_y = None
        elif self.transformtype_y == self.transformtypes.custom:
            scale_y = self.scaley

        step = 1
        if self.flip:
            step = -1
        if self.shift > 0:
            outshift = self.shift
            inshift = 0
        elif self.shift < 0:
            outshift = 0
            inshift = -self.shift
        else:
            outshift = 0
            inshift = 0

        layerdef = design.return_layer_definition()
        return popupcad.algorithms.manufacturing_functions.transform2(layerdef,inshift,outshift,step,geom_from,geoms_to,CSG,scale_x,scale_y)

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(design, design.operations)
        return dialog

    def buildeditdialog(self, design):
        dialog = Dialog(design,design.prioroperations(self),self)
        return dialog
if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    sys.exit(app.exec_())
