# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
import shapely.ops as ops
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.sketch import Sketch
import popupcad.widgets
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.design import NoOperation
import popupcad.geometry.customshapely as customshapely
import popupcad.widgets.listmanager as listmanager
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.manufacturing.nulloperation import NullOp


class Dialog(qg.QDialog):
    def __init__(self,cls,design,operations,selectedopindex=None,outputref = 0,selectedoutput = None,sketch = None,operation_type_index = 0):
        super(Dialog,self).__init__()
        self.design = design
        self.operations = [NullOp()]+operations
        self.cls = cls

        self.optree = DraggableTreeWidget()
        self.optree.linklist(self.operations)
        if selectedopindex!=None:
            selectedopindex = selectedopindex+1
        else:
            selectedopindex = 0
        
        self.optree.setCurrentIndeces(selectedopindex,outputref)        

        self.sketchwidget = listmanager.build_sketchlist(self.design)
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value==sketch:
                item.setSelected(True)
        
        if selectedoutput == None:
            selectedoutput = [item.id for item in design.return_layer_definition().layers]
        self.outputlayerselector = qg.QListWidget()
        self.outputlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.outputlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
        outputitems = [popupcad.filetypes.listwidgetitem.ListWidgetItem(item,self.outputlayerselector) for item in design.return_layer_definition().layers]
        [item.setSelected(item.customdata.id in selectedoutput) for item in outputitems]        

        from  popupcad.widgets.operationlist import OperationList
        self.operationtypeselector = OperationList([],cls.operationtypes,cls.operationtypes)
#        self.operationtypeselector.addItems(cls.operationtypes)
        self.operationtypeselector.setCurrentIndex(operation_type_index)        

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')
        buttonlayout = qg.QHBoxLayout()
        buttonlayout.addWidget(button1)
        buttonlayout.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.sketchwidget)
        layout.addWidget(self.operationtypeselector)
        layout.addWidget(qg.QLabel('Parent Operation'))
        layout.addWidget(self.optree)
        layout.addWidget(qg.QLabel('Select Layers'))
        layout.addWidget(self.outputlayerselector)
        layout.addLayout(buttonlayout)
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

        ii,outputref = self.optree.currentIndeces()
        ii -= 1
        if ii==-1:
            operation_link1, outputref = None,0
        else:
            operation_link1, outputref = self.optree.currentRefs()[0]
        
        layer_links = [item.customdata.id for item in self.outputlayerselector.selectedItems()]

        operation_type_index = self.operationtypeselector.currentIndex()

        function = self.cls.operationtypes[operation_type_index]
        outputref = 0
        return sketchid, operation_link1,layer_links,function,outputref

class SketchOperation2(Operation):
    name = 'SketchOperation2'
    operationtypes = ['union','intersection','difference','symmetric_difference']  

    def copy(self):
        new = type(self)(self.sketchid,self.operation_link1,self.layer_links,self.function,self.outputref)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SketchOperation2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,sketchid,operation_link1,layer_links,function,outputref):        
        super(SketchOperation2,self).editdata()
        self.sketchid = sketchid
        self.operation_link1 = operation_link1
        self.layer_links = layer_links
        self.function = function       
        self.outputref = outputref
        self.name = 'Sketch '+ function

    def getoutputref(self):
        return self.outputref

    def operate(self,design):
        operationgeom = design.sketches[self.sketchid].output_csg()
        layers = [design.return_layer_definition().getlayer(item) for item in self.layer_links]        

        try:
            laminate1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        except NoOperation:
            laminate1 = Laminate(design.return_layer_definition())
        
        laminate2 = Laminate(design.return_layer_definition())
        for layer in layers:
            laminate2.replacelayergeoms(layer,[operationgeom])

        lsout = laminate1.binaryoperation(laminate2,self.function)
        return lsout

    def parentrefs(self):
        if self.operation_link1==None:
            return []
        else:
            return [self.operation_link1]
    def sketchrefs(self):
        return [self.sketchid]

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(cls,design,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        sketch = design.sketches[self.sketchid]
        operation_type_index = self.operationtypes.index(self.function)
        if self.operation_link1!=None:
            selectedindex = design.operation_index(self.operation_link1)
        else:
            selectedindex = None
        dialog = Dialog(self,design,design.prioroperations(self),selectedindex,self.outputref,self.layer_links,sketch,operation_type_index)
        return dialog
