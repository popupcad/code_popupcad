# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.materials.laminatesheet import Laminate
from popupcad.filetypes.operation import Operation
import PySide.QtGui as qg
from popupcad.filetypes.listwidgetitem import ListWidgetItem
from popupcad.widgets.dragndroptree import DraggableTreeWidget,ParentItem,ChildItem


class Dialog(qg.QDialog):
            
    def __init__(self,unaryoperationtypes,pairoperationtypes,operations,layerlist,index0=0,selectedop = None,selectedunary = None,selectedpair = None,selectedoutput = None,outputref = 0):
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

        self.unaryoperationtypes = unaryoperationtypes        
        self.pairoperationtypes = pairoperationtypes
        
        self.le0 = qg.QComboBox()
        self.le0.addItems(unaryoperationtypes+pairoperationtypes)

        self.operations = operations
        self.operationselector = DraggableTreeWidget()
        self.operationselector.linklist(self.operations)
        self.operationselector.selectIndeces([(selectedop,outputref)])
        
        self.unarylayerselector = qg.QListWidget()
        self.unarylayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.unarylayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
#        unaryitems = self.additems(self.unarylayerselector,layerlist)            
        unaryitems = [ListWidgetItem(item,self.unarylayerselector) for item in layerlist]

        self.pairlayerselector = qg.QListWidget()
        self.pairlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.pairlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
#        pairitems = self.additems(self.pairlayerselector,layerlist)            
        pairitems = [ListWidgetItem(item,self.pairlayerselector) for item in layerlist]

        self.outputlayerselector = qg.QListWidget()
        self.outputlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.outputlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
#        outputitems = self.additems(self.outputlayerselector,layerlist)            
        outputitems = [ListWidgetItem(item,self.outputlayerselector) for item in layerlist]

        layout = qg.QVBoxLayout()
        layout.addWidget(self.le0)
        layout.addWidget(self.operationselector)
        layout.addWidget(self.unarylayerselector)
        layout.addWidget(self.pairlayerselector)
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
        
        self.le0.setCurrentIndex(index0)
        self.le0.currentIndexChanged.connect(self.changelayout)
        self.changelayout()
        
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
        
    def changelayout(self):
        if self.le0.currentText() in self.unaryoperationtypes:
            self.pairlayerselector.hide()
        else:
            self.pairlayerselector.show()
            
class LayerOp(Operation):
    name = 'Layer Op'
    function = None
    pairoperationtypes = ['difference','symmetric_difference']    
    unaryoperationtypes = ['union','intersection']   

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
            selectedinputlayers = [design.layerdef().getlayer(link) for link in self.unary_layer_links]
            selectedoutputlayers = [design.layerdef().getlayer(link) for link in self.output_layer_links]
            lsin=design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
            return lsin.unarylayeroperation(self.function,selectedinputlayers,selectedoutputlayers)
        elif self.function in self.pairoperationtypes:
            ls = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
            pair1 = [design.layerdef().getlayer(link) for link in self.unary_layer_links]
            pair2 = [design.layerdef().getlayer(link) for link in self.pair_layer_links]
            outputlayers = [design.layerdef().getlayer(layerlink) for layerlink in self.output_layer_links]
            return ls.binarylayeroperation2(self.function,pair1,pair2,outputlayers)

    @classmethod        
    def buildnewdialog(cls,design,currentop):
        return Dialog(cls.unaryoperationtypes,cls.pairoperationtypes,design.operations,design.layerdef().layers)

    def buildeditdialog(self,design):
        operationindex = design.operation_index(self.operation_link1) 
        return Dialog(self.unaryoperationtypes,self.pairoperationtypes,design.prioroperations(self),design.layerdef().layers,(self.unaryoperationtypes+self.pairoperationtypes).index(self.function),operationindex,self.unary_layer_links,self.pair_layer_links,self.output_layer_links,self.getoutputref())
