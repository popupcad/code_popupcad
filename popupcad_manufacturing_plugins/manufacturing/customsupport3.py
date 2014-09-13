# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.operation import Operation

import PySide.QtCore as qc
import PySide.QtGui as qg

from popupcad.materials.laminatesheet import Layer,Laminate
from popupcad.filetypes.validators import StrictDoubleValidator
from popupcad.filetypes.enum import enum
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.widgets.dragndroptree import DraggableTreeWidget
import popupcad.widgets.listmanager as listmanager
from popupcad.filetypes.listwidgetitem import ListWidgetItem

from .. import algorithms

class Dialog(qg.QDialog):
    def __init__(self,design,operationlist,device_index=0,support_width = 1.0,support_out = 1.0,hole_radius = 1.0,cut_width = 1.0,deviceoutputref = 0,sketch = None,selectedoutput = None):
        super(Dialog,self).__init__()
        self.design = design
        self.operationlist = operationlist

        self.device_index = DraggableTreeWidget()
        self.device_index.linklist(self.operationlist)
        self.device_index.setCurrentIndeces(device_index,deviceoutputref)
        
        self.sketchwidget = listmanager.build_sketchlist(self.design)
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value==sketch:
                item.setSelected(True)
        
        if selectedoutput == None:
            selectedoutput = [item.id for item in design.layerdef().layers]
        self.outputlayerselector = qg.QListWidget()
        self.outputlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.outputlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
        outputitems = [ListWidgetItem(item,self.outputlayerselector) for item in design.layerdef().layers]
        [item.setSelected(item.customdata.id in selectedoutput) for item in outputitems]        

        self.support_width = qg.QLineEdit()
        self.support_width.setAlignment(qc.Qt.AlignRight)
        self.support_width.setText(str(support_width))
        v = StrictDoubleValidator(0, 1e6, 4,self.support_width)
        self.support_width.setValidator(v)
        
        self.support_out = qg.QLineEdit()
        self.support_out.setAlignment(qc.Qt.AlignRight)
        self.support_out.setText(str(support_out))
        v = StrictDoubleValidator(0, 1e6, 4,self.support_out)
        self.support_out.setValidator(v)

        self.hole_radius = qg.QLineEdit()
        self.hole_radius.setAlignment(qc.Qt.AlignRight)
        self.hole_radius.setText(str(hole_radius))
        v = StrictDoubleValidator(0, 1e6, 4,self.hole_radius)
        self.hole_radius.setValidator(v)

        self.cut_width = qg.QLineEdit()
        self.cut_width.setAlignment(qc.Qt.AlignRight)
        self.cut_width.setText(str(cut_width))
        v = StrictDoubleValidator(0, 1e6, 4,self.cut_width)
        self.cut_width.setValidator(v)

        layout = qg.QVBoxLayout()

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        gridlayout = qg.QGridLayout()
        gridlayout.addWidget(qg.QLabel('Support Width'),1,1)
        gridlayout.addWidget(self.support_width,1,2)
        gridlayout.addWidget(qg.QLabel('Support Out'),2,1)
        gridlayout.addWidget(self.support_out,2,2)
        gridlayout.addWidget(qg.QLabel('Hole Radius'),3,1)
        gridlayout.addWidget(self.hole_radius,3,2)
        gridlayout.addWidget(qg.QLabel('CutWidth'),4,1)
        gridlayout.addWidget(self.cut_width,4,2)
        gridlayout.addWidget(button1,5,1)
        gridlayout.addWidget(button2,5,2)

        layout.addWidget(self.device_index)
        layout.addWidget(self.sketchwidget)
        layout.addWidget(self.outputlayerselector)
        layout.addLayout(gridlayout)

        self.setLayout(layout)    

        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        sketchid =  self.sketch().id
        opid,outputref= self.device_index.currentRefs()[0]
        layer_links = [item.customdata.id for item in self.outputlayerselector.selectedItems()]
        
        return opid,sketchid,layer_links,float(self.support_width.text()),float(self.support_out.text()),float(self.hole_radius.text()),float(self.cut_width.text()),outputref

class CustomSupport3(Operation):
    name = 'Custom Support'
    outputtypes = enum(device = 201,supports = 202,cuts = 203)    
    
    def __init__(self,*args):
        super(CustomSupport3,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,device_link,sketch_link,layer_links,support_width,support_out,hole_radius,cut_width,deviceoutputref):
        super(CustomSupport3,self).editdata()
        self.device_link= device_link
        self.sketch_link = sketch_link
        self.layer_links = layer_links
        self.support_width= support_width
        self.support_out= support_out
        self.hole_radius= hole_radius
        self.cut_width= cut_width
        self.deviceoutputref = deviceoutputref

    def copy(self):
        new = type(self)(self.device_link,self.sketch_link,self.layer_links,self.support_width,self.support_out,self.hole_radius,self.cut_width,self.deviceoutputref)
        new.id = self.id
        new.customname = self.customname
        return new

    def parentrefs(self):
        return [self.device_link]

    @classmethod
    def buildnewdialog(cls,design,currentoperation):
        dialog = Dialog(design,design.operations)
        return dialog

    def buildeditdialog(self,design):        
        device_index= design.operation_index(self.device_link)
        sketch = design.sketches[self.sketch_link]
        dialog = Dialog(design,design.prioroperations(self),device_index,self.support_width,self.support_out,self.hole_radius,self.cut_width,self.deviceoutputref,sketch,self.layer_links)
        return dialog

    def generate(self,design):
        operationgeom = design.sketches[self.sketch_link].output_csg()
        layers = [design.layerdef().getlayer(item) for item in self.layer_links]        
        support = Laminate(design.layerdef())
        for layer in layers:
            support.replacelayergeoms(layer,[operationgeom])
        
        device = design.op_from_ref(self.device_link).output[self.deviceoutputref].csg
        modified_device,supports,cuts = algorithms.modify_device.modify_device(device,support,self.support_width*popupcad.internal_argument_scaling,self.support_out*popupcad.internal_argument_scaling,self.hole_radius*popupcad.internal_argument_scaling,self.cut_width*popupcad.internal_argument_scaling)
        s = OperationOutput(supports,'supports',self)
        c = OperationOutput(cuts,'cuts',self)
        d = OperationOutput(modified_device,'device',self)
        self.output = [d,s,c]
