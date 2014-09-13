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
    def __init__(self,unaryoperationtypes,pairoperationtypes,operationlist,index0,operationindeces1=None,operationindeces2 = None):
        super(Dialog,self).__init__()
        
        self.unaryoperationtypes = unaryoperationtypes        
        self.pairoperationtypes = pairoperationtypes
        if operationindeces1 ==None:
            operationindeces1 = []
        if operationindeces2 ==None:
            operationindeces2 = []
        
        self.le0 = qg.QComboBox()
        self.le0.addItems(unaryoperationtypes+pairoperationtypes)

        self.operationlist = operationlist

        self.unarylistwidget = DraggableTreeWidget()
        self.unarylistwidget.linklist(self.operationlist)
        self.unarylistwidget.setSelectionMode(qg.QListWidget.SelectionMode.ExtendedSelection)
        self.unarylistwidget.selectIndeces(operationindeces1)

        self.pairlistwidget = DraggableTreeWidget()
        self.pairlistwidget.linklist(self.operationlist)
        self.pairlistwidget.setSelectionMode(qg.QListWidget.SelectionMode.ExtendedSelection)
        self.pairlistwidget.selectIndeces(operationindeces2)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.le0)
        layout.addWidget(self.unarylistwidget)
        layout.addWidget(self.pairlistwidget)

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

    def acceptdata(self):
        unaryparents = self.unarylistwidget.currentRefs()
        pairparents = self.pairlistwidget.currentRefs()
        function = self.le0.currentText()
        return unaryparents, pairparents, function

    def changelayout(self):
        if self.le0.currentText() in self.unaryoperationtypes:
            self.pairlistwidget.hide()
        else:
            self.pairlistwidget.show()
            
class LaminateOperation(Operation):
    name = 'Laminate Op'
    unaryoperationtypes = ['union','intersection']    
    pairoperationtypes = ['difference','symmetric_difference']    
    attr_init = 'operation_links1','operation_links2','function'
    attr_init_k = tuple()
    attr_copy = 'id','customname'
    
    def __init__(self,*args,**kwargs):
        super(LaminateOperation,self).__init__()
        self.editdata(*args,**kwargs)
        self.id = id(self)
        
    def editdata(self,operation_links1,operation_links2,function):
        super(LaminateOperation,self).editdata()
        self.operation_links1 = operation_links1
        self.operation_links2 = operation_links2
        self.function = function

    def operate(self,design):
        if self.function in self.unaryoperationtypes:
            laminates = [design.op_from_ref(link).output[ii].csg for link,ii in self.operation_links1]
            laminateout = Laminate.unaryoperation(laminates,self.function)
            return laminateout
        elif self.function in self.pairoperationtypes:
            laminates1 = [design.op_from_ref(link).output[ii].csg for link,ii in self.operation_links1]
            laminate1 = Laminate.unaryoperation(laminates1,'union')
            laminates2 = [design.op_from_ref(link).output[ii].csg for link,ii in self.operation_links2]
            laminate2 = Laminate.unaryoperation(laminates2,'union')
            return laminate1.binaryoperation(laminate2,self.function)
        
    @classmethod
    def buildnewdialog(cls,design,currentop):
        return Dialog(cls.unaryoperationtypes,cls.pairoperationtypes,design.operations,0)

    def buildeditdialog(self,design):
        operationindeces1 = [(design.operation_index(ref),ii) for ref,ii in self.operation_links1]
        operationindeces2 = [(design.operation_index(ref),ii) for ref,ii in self.operation_links2]
        return Dialog(self.unaryoperationtypes,self.pairoperationtypes,design.prioroperations(self),(self.unaryoperationtypes+self.pairoperationtypes).index(self.function),operationindeces1,operationindeces2)

    def parentrefs(self):
        if self.function in self.unaryoperationtypes:
            return [ref for ref,ii in self.operation_links1]
        else:
            return [ref for ref,ii in self.operation_links1 + self.operation_links2]
