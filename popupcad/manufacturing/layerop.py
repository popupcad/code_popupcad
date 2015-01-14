# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.operation import Operation
import PySide.QtGui as qg
from popupcad.filetypes.listwidgetitem import ListWidgetItem
from popupcad.widgets.dragndroptree import DraggableTreeWidget,ParentItem,ChildItem


class Dialog(qg.QDialog):
            
    def __init__(self,operations,layerlist,index0=0,selectedop = None,selectedunary = None,selectedpair = None,selectedoutput = None,outputref = 0):
        super(Dialog,self).__init__()

        sp = qg.QSizePolicy()
        sp.setHorizontalPolicy(sp.Policy.Minimum)
        sp.setVerticalPolicy(sp.Policy.Minimum)
        if selectedop == None:
            selectedop = len(operations)-1
        if selectedunary == None:
            selectedunary = []
        if selectedpair == None:
            selectedpair = []
        if selectedoutput == None:
            selectedoutput = layerlist

        from popupcad.widgets.operationlist import OperationList
        self.le0 = OperationList(LayerOp.unaryoperationtypes,LayerOp.pairoperationtypes,LayerOp.displayorder)


        self.operations = operations
        self.operationselector = DraggableTreeWidget()
        self.operationselector.linklist(self.operations)
        self.operationselector.selectIndeces([(selectedop,outputref)])
        
        self.unarylayerselector = qg.QListWidget()
        self.unarylayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.unarylayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
        unaryitems = [ListWidgetItem(item,self.unarylayerselector) for item in layerlist]

        self.pairlayerselector = qg.QListWidget()
        self.pairlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.pairlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
        pairitems = [ListWidgetItem(item,self.pairlayerselector) for item in layerlist]

        self.outputlayerselector = qg.QListWidget()
        self.outputlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.outputlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
        outputitems = [ListWidgetItem(item,self.outputlayerselector) for item in layerlist]

        layout2 = qg.QVBoxLayout()
#        self.layout2.setContentsMargins(0,0,0,0)
        layout2.addWidget(qg.QLabel('Unary Operators'))
        layout2.addWidget(self.unarylayerselector)

        layout3 = qg.QVBoxLayout()
#        self.layout2.setContentsMargins(0,0,0,0)
        layout3.addWidget(qg.QLabel('Binary Operators'))
        layout3.addWidget(self.pairlayerselector)

        layout4 = qg.QHBoxLayout()
        layout4.addLayout(layout2)
        layout4.addLayout(layout3)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.le0)
        layout.addWidget(qg.QLabel('Parent Operation'))
        layout.addWidget(self.operationselector)
        layout.addLayout(layout4)
        layout.addWidget(qg.QLabel('Output Layers'))
        layout.addWidget(self.outputlayerselector)

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)

        layout.addLayout(layout2)

        self.setLayout(layout)   
        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)
        
        self.le0.unary_selected.connect(lambda:self.pairlayerselector.setEnabled(False))
        self.le0.binary_selected.connect(lambda:self.pairlayerselector.setEnabled(True))
        self.le0.setCurrentIndex(index0)
        
        [item.setSelected(item.customdata.id in selectedunary) for item in unaryitems]        
        [item.setSelected(item.customdata.id in selectedpair) for item in pairitems]        
        [item.setSelected(item.customdata.id in selectedoutput) for item in outputitems]        

    def acceptdata(self):
        operation_link1,outputref = self.operationselector.currentRefs()[0]
        function = self.le0.currentText()
        unary_layer_links = [item.customdata.id for item in self.unarylayerselector.selectedItems()]
        pair_layer_links = [item.customdata.id for item in self.pairlayerselector.selectedItems()]
        output_layer_links = [item.customdata.id for item in self.outputlayerselector.selectedItems()]
        
        return operation_link1,function,unary_layer_links,pair_layer_links,output_layer_links,outputref
        
class LayerOp(Operation):
    name = 'Layer Op'
    function = None
    pairoperationtypes = ['difference','symmetric_difference']    
    unaryoperationtypes = ['union','intersection']   
    displayorder = unaryoperationtypes + pairoperationtypes

    attr_init = 'operation_link1','function','unary_layer_links','pair_layer_links','output_layer_links','outputref'
    attr_init_k = tuple()
    attr_copy = 'id','customname'
    
    def __init__(self,*args,**kwargs):
        super(LayerOp,self).__init__()
        self.editdata(*args,**kwargs)
        self.id = id(self)

    def editdata(self,operation_link1,function,unary_layer_links,pair_layer_links,output_layer_links,outputref):
        super(LayerOp,self).editdata()
        self.operation_link1 = operation_link1
        self.function = function
        self.unary_layer_links = unary_layer_links        
        self.pair_layer_links = pair_layer_links
        self.output_layer_links = output_layer_links
        self.outputref = outputref

    def getoutputref(self):
        return self.outputref
        
    def parentrefs(self):
        return [self.operation_link1]

    def operate(self,design):
        if self.function in self.unaryoperationtypes:
            selectedinputlayers = [design.return_layer_definition().getlayer(link) for link in self.unary_layer_links]
            selectedoutputlayers = [design.return_layer_definition().getlayer(link) for link in self.output_layer_links]
            lsin=design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
            return lsin.unarylayeroperation(self.function,selectedinputlayers,selectedoutputlayers)
        elif self.function in self.pairoperationtypes:
            ls = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
            pair1 = [design.return_layer_definition().getlayer(link) for link in self.unary_layer_links]
            pair2 = [design.return_layer_definition().getlayer(link) for link in self.pair_layer_links]
            outputlayers = [design.return_layer_definition().getlayer(layerlink) for layerlink in self.output_layer_links]
            return ls.binarylayeroperation2(self.function,pair1,pair2,outputlayers)

    @classmethod        
    def buildnewdialog(cls,design,currentop):
        return Dialog(design.operations,design.return_layer_definition().layers)

    def buildeditdialog(self,design):
        operationindex = design.operation_index(self.operation_link1) 
        ii = self.displayorder.index(self.function)
        return Dialog(design.prioroperations(self),design.return_layer_definition().layers,ii,operationindex,self.unary_layer_links,self.pair_layer_links,self.output_layer_links,self.getoutputref())

    def upgrade(self,*args,**kwargs):
        from layerop2 import LayerOp2
        operation_links = {'parent':[(self.operation_link1,self.outputref)]}
        new = LayerOp2(operation_links,self.function,self.unary_layer_links,self.pair_layer_links,self.output_layer_links)
        new.customname = self.customname
        new.id = self.id
        return new
#    def copy(self):
#        return self.upgrade()