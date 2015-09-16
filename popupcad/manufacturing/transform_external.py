# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import sys
import PySide.QtGui as qg
import popupcad
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from dev_tools.enum import enum
from popupcad.widgets.listmanager import SketchListManager, DesignListManager


class Dialog(qg.QDialog):

    def __init__(self,design,prioroperations,placeop = None):
        super(Dialog, self).__init__()

        if placeop is None:
            self.placeop=TransformExternal(None,None,None,None,TransformExternal.transformtypes.scale,TransformExternal.transformtypes.scale,0,False,1.,1.)
        else:
            self.placeop = placeop

        self.prioroperations = prioroperations
        self.design = design

        self.designwidget = DesignListManager(design)

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
        layout.addWidget(self.designwidget)
        layout.addWidget(qg.QLabel('Operations'))
        layout.addWidget(self.operation_list)
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

        if self.placeop.transformtype_x == TransformExternal.transformtypes.scale:
            self.radiobox_scale_x.setChecked(True)
        elif self.placeop.transformtype_x == TransformExternal.transformtypes.custom:
            self.radiobox_custom_x.setChecked(True)

        if self.placeop.transformtype_y == TransformExternal.transformtypes.scale:
            self.radiobox_scale_y.setChecked(True)
        elif self.placeop.transformtype_y == TransformExternal.transformtypes.custom:
            self.radiobox_custom_y.setChecked(True)

        self.designwidget.itemlist.itemSelectionChanged.connect(self.loadoperations)
        
        if self.placeop.sketch_links is not None:
            sketch_to = self.design.sketches[self.placeop.sketch_links['sketch_to'][0]]

            for ii in range(self.sketchwidget_to.itemlist.count()):
                item = self.sketchwidget_to.itemlist.item(ii)
                if item.value == sketch_to:
                    item.setSelected(True)

        self.loadoperations()

        try:
            subdesign = design.subdesigns[self.placeop.design_links['subdesign'][0]]
            for ii in range(self.designwidget.itemlist.count()):
                item = self.designwidget.itemlist.item(ii)
                if item.value == subdesign:
                    item.setSelected(True)            
            
            if self.placeop.subopref is not None:
                id, jj = self.placeop.subopref
                ii = subdesign.operation_index(id)
                self.operation_list.selectIndeces([(ii, jj)])

            sketch_from = subdesign.sketches[self.placeop.sub_sketch_id]
            for ii in range(self.sketchwidget_from.itemlist.count()):
                item = self.sketchwidget_from.itemlist.item(ii)
                if item.value == sketch_from:
                    item.setSelected(True)            
        except TypeError:
            pass

        self.scalex.setText(str(self.placeop.scalex))
        self.scaley.setText(str(self.placeop.scaley))
        self.flip.setChecked(self.placeop.flip)
        self.sb.setValue(self.placeop.shift)
        
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

    def build_sketch_links(self):
        try:
            sketch_links = {}
            sketch_links['sketch_to']=[self.sketchwidget_to.itemlist.selectedItems()[0].value.id]
            return sketch_links
        except IndexError:
            return None            
            
    def loadoperations(self):
        if len(self.designwidget.itemlist.selectedItems()) > 0:
            self.operation_list.linklist(self.subdesign().operations)
            self.sketchwidget_from.update_list(self.subdesign().sketches)

    def acceptdata(self):
        if self.radiobox_scale_x.isChecked():
            transformtype_x = TransformExternal.transformtypes.scale
        elif self.radiobox_custom_x.isChecked():
            transformtype_x = TransformExternal.transformtypes.custom

        if self.radiobox_scale_y.isChecked():
            transformtype_y = TransformExternal.transformtypes.scale
        elif self.radiobox_custom_y.isChecked():
            transformtype_y = TransformExternal.transformtypes.custom

        ii, jj = self.operation_list.currentIndeces2()[0]
        sketch_links = self.build_sketch_links()
        subopid = self.subdesign().operations[ii].id
        subopref = subopid, jj
        sub_sketch_id = self.sketchwidget_from.itemlist.selectedItems()[0].value.id
        design_links = {'subdesign': [self.subdesign().id]}
        
        shift = self.sb.value()
        flip = self.flip.isChecked()
        scale_x = float(self.scalex.text())
        scale_y = float(self.scaley.text())
                      
        return sketch_links, design_links,subopref,sub_sketch_id,transformtype_x, transformtype_y, shift, flip, scale_x, scale_y


class TransformExternal(Operation2):
    name = 'External Transform'
    transformtypes = enum(scale='scale', custom='custom')

    def copy(self):
        new = TransformExternal(self.sketch_links,self.design_links,self.subopref,self.sub_sketch_id,self.transformtype_x,self.transformtype_y,self.shift,self.flip,self.scalex,self.scaley)
        new.customname = self.customname
        new.id = self.id
        return new

    def __init__(self, *args):
        super(TransformExternal, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,sketch_links,design_links,subopref,sub_sketch_id,transformtype_x,transformtype_y,shift,flip,scalex,scaley):
        super(TransformExternal, self).editdata({}, sketch_links, design_links)
        self.subopref = subopref
        self.sub_sketch_id = sub_sketch_id
        self.transformtype_x = transformtype_x
        self.transformtype_y = transformtype_y
        self.shift = shift
        self.flip = flip
        self.scalex = scalex
        self.scaley = scaley

    def operate(self, design):
        subdesign = design.subdesigns[self.design_links['subdesign'][0]]

        sketch_from_id = self.sub_sketch_id
        sketch_to_id = self.sketch_links['sketch_to'][0]

        sketch_from = subdesign.sketches[sketch_from_id]
        sketch_to = design.sketches[sketch_to_id]
        operation_ref, output_index = self.subopref
        csg_laminate = subdesign.operations[subdesign.operation_index(operation_ref)].output[output_index].csg
        
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

        layerdef_from = subdesign.return_layer_definition()
        layerdef_to = design.return_layer_definition()
        return popupcad.algorithms.manufacturing_functions.transform_csg(layerdef_from,layerdef_to,inshift,outshift,step,geom_from,geoms_to,csg_laminate,scale_x,scale_y)

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(design, design.operations)
        return dialog

    def buildeditdialog(self, design):
        dialog = Dialog(design,design.prioroperations(self),self)
        return dialog

    def to_internal_transform(self,sketch_mapping_dict,op_mapping_dict):
        from popupcad.manufacturing.transform_internal import TransformInternal
        sketch_links = self.sketch_links.copy()
        sketch_links['sketch_from'] = [sketch_mapping_dict[self.sub_sketch_id]]
        operation_link = self.subopref
        operation_link = op_mapping_dict[operation_link[0]],operation_link[1]
        operation_links = {'from':[operation_link]}
        new = TransformInternal(sketch_links,operation_links,self.transformtype_x,self.transformtype_y,self.shift,self.flip,self.scalex,self.scaley)
        new.customname = self.customname
        return new

if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    sys.exit(app.exec_())

