# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 11:08:00 2014

@author: danb0b
"""

import PySide.QtGui as qg
import PySide.QtCore as qc
class OperationList(qg.QWidget):
#    opchange = qc.Signal()
    unary_selected = qc.Signal()
    binary_selected = qc.Signal()
    
    def __init__(self,unaryops,binaryops,text_list):
        super(OperationList,self).__init__()

        self.unaryops = unaryops        
        self.binaryops = binaryops

#        self.addItems(text_list)
        self.combobox = qg.QComboBox()
        self.combobox.addItems(text_list)
        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Operation Type'))
        layout.addWidget(self.combobox)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.combobox.currentIndexChanged.connect(self.testchange)
    def is_unary(self):
        return self.combobox.currentText() in self.unaryops
    def is_binary(self):
        return self.combobox.currentText() in self.binaryops
    def setCurrentIndex(self,ii):
        self.combobox.setCurrentIndex(ii)
        if self.is_unary():
            self.unary_selected.emit()
        if self.is_binary():
            self.binary_selected.emit()
            
    def testchange(self):
#        self.opchange.emit()
        if self.is_unary():
            self.unary_selected.emit()
        if self.is_binary():
            self.binary_selected.emit()
    def currentText(self):
        return self.combobox.currentText()
    def currentIndex(self):
        return self.combobox.currentIndex()
        