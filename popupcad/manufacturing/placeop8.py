# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import sys
import qt
qc = qt.QtCore
qg = qt.QtGui
import numpy
import popupcad
import popupcad.filetypes
from popupcad.filetypes.operation2 import Operation2
from popupcad.filetypes.design import NoOperation
#from popupcad.filetypes.design import Design
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from dev_tools.enum import enum
#from popupcad.filetypes.sketch import Sketch
from popupcad.widgets.listmanager import SketchListManager, DesignListManager


class Dialog(qg.QDialog):

    def __init__(
            self,
            design,
            prioroperations,
            sketch=None,
            subdesign=None,
            subopref=None,
            transformtype_x=None,
            transformtype_y=None,
            shift=0,
            flip=False,
            scalex=1.,
            scaley=1.):
        super(Dialog, self).__init__()

        if transformtype_x is None:
            self.transformtype_x = PlaceOperation8.transformtypes.scale
        else:
            self.transformtype_x = transformtype_x

        if transformtype_y is None:
            self.transformtype_y = PlaceOperation8.transformtypes.scale
        else:
            self.transformtype_y = transformtype_y

        self.prioroperations = prioroperations
        self.design = design

        self.designwidget = DesignListManager(design)

        self.optree = DraggableTreeWidget()

        self.sketchwidget = SketchListManager(design)

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
        self.sb.setRange(popupcad.gui_negative_infinity, popupcad.gui_positive_infinity)
        self.sb.setSingleStep(1)
        self.sb.setValue(shift)
        layout4.addWidget(self.sb)

#        layout3 = qg.QHBoxLayout()
#        layout3.addWidget(self.lineedit)
#        layout3.addWidget(button3)

        button1 = qg.QPushButton('Ok')
        button1.clicked.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.clicked.connect(self.reject)

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

        if self.transformtype_x == PlaceOperation8.transformtypes.scale:
            self.radiobox_scale_x.setChecked(True)
        elif self.transformtype_x == PlaceOperation8.transformtypes.custom:
            self.radiobox_custom_x.setChecked(True)

        if self.transformtype_y == PlaceOperation8.transformtypes.scale:
            self.radiobox_scale_y.setChecked(True)
        elif self.transformtype_y == PlaceOperation8.transformtypes.custom:
            self.radiobox_custom_y.setChecked(True)

        self.designwidget.itemlist.itemSelectionChanged.connect(
            self.loadoperations)

        for ii in range(self.designwidget.itemlist.count()):
            item = self.designwidget.itemlist.item(ii)
            if item.value == subdesign:
                item.setSelected(True)

        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value == sketch:
                item.setSelected(True)

        self.loadoperations()
        try:
            if subopref is not None:
                id, jj = subopref
                if subdesign is not None:
                    ii = subdesign.operation_index(id)
                    self.optree.selectIndeces([(ii, jj)])
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
        if len(self.designwidget.itemlist.selectedItems()) > 0:
            self.optree.linklist(self.subdesign().operations)

    def acceptdata(self):
        if self.radiobox_scale_x.isChecked():
            transformtype_x = PlaceOperation8.transformtypes.scale
        elif self.radiobox_custom_x.isChecked():
            transformtype_x = PlaceOperation8.transformtypes.custom

        if self.radiobox_scale_y.isChecked():
            transformtype_y = PlaceOperation8.transformtypes.scale
        elif self.radiobox_custom_y.isChecked():
            transformtype_y = PlaceOperation8.transformtypes.custom

        ii, jj = self.optree.currentIndeces2()[0]
        subopid = self.subdesign().operations[ii].id
        subopref = subopid, jj
        sketch_links = {'place': [self.sketch().id]}
        design_links = {'subdesign': [self.subdesign().id]}
        return sketch_links, design_links, subopref, transformtype_x, transformtype_y, self.sb.value(
        ), self.flip.isChecked(), float(self.scalex.text()), float(self.scaley.text())


class PlaceOperation8(Operation2):
    name = 'PlaceOp'
    transformtypes = enum(scale='scale', custom='custom')

    def copy(self):
        new = PlaceOperation8(
            self.sketch_links,
            self.design_links,
            self.subopref,
            self.transformtype_x,
            self.transformtype_y,
            self.shift,
            self.flip,
            self.scalex,
            self.scaley)
        new.customname = self.customname
        new.id = self.id
        return new

    def upgrade_special(self,design):
        subdesign = design.subdesigns[self.design_links['subdesign'][0]]
        sub_sketch_id = subdesign.findlocatesketch_id()
        from popupcad.manufacturing.transform_external import TransformExternal
        sketch_links = {}
        sketch_links['sketch_to'] = self.sketch_links['place']        
        new = TransformExternal(
            sketch_links,
            self.design_links,
            self.subopref,
            sub_sketch_id,
            self.transformtype_x,
            self.transformtype_y,
            self.shift,
            self.flip,
            self.scalex,
            self.scaley)
        new.customname = self.customname
        new.id = self.id
        return new

    def __init__(self, *args):
        super(PlaceOperation8, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(
            self,
            sketch_links,
            design_links,
            subopref,
            transformtype_x,
            transformtype_y,
            shift,
            flip,
            scalex,
            scaley):
        super(PlaceOperation8, self).editdata({}, sketch_links, design_links)
#        self.sketchid = sketchid
#        self.subdesignid = subdesignid
        self.subopref = subopref
        self.transformtype_x = transformtype_x
        self.transformtype_y = transformtype_y
        self.shift = shift
        self.flip = flip
        self.scalex = scalex
        self.scaley = scaley

    def operate(self, design):
        subdesign = design.subdesigns[self.design_links['subdesign'][0]]

        sketch_to_id = self.sketch_links['place'][0]
        sketch_to = design.sketches[sketch_to_id]

        operation_ref, output_index = self.subopref
        csg_laminate = subdesign.operations[subdesign.operation_index(operation_ref)].output[output_index].csg

        geom_from = subdesign.findlocateline()

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

    def fromQTransform(self, tin):
        tout = numpy.array([[tin.m11(), tin.m12(), tin.m13()], [
                           tin.m21(), tin.m22(), tin.m23()], [tin.m31(), tin.m32(), tin.m33()]]).T
        return tout

    def toQTransform(self, tin):
        tout = qg.QTransform(
            tin[1][1],
            tin[1][2],
            tin[1][3],
            tin[2][1],
            tin[2][2],
            tin[2][3],
            tin[3][1],
            tin[3][2],
            tin[3][3])
        return tout

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(design, design.operations)
        return dialog

    def buildeditdialog(self, design):
        sketch = design.sketches[self.sketch_links['place'][0]]
        subdesign = design.subdesigns[self.design_links['subdesign'][0]]
        dialog = Dialog(
            design,
            design.prioroperations(self),
            sketch=sketch,
            subdesign=subdesign,
            subopref=self.subopref,
            transformtype_x=self.transformtype_x,
            transformtype_y=self.transformtype_y,
            shift=self.shift,
            flip=self.flip,
            scalex=self.scalex,
            scaley=self.scaley)
        return dialog
if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    sys.exit(app.exec_())
