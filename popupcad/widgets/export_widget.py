# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 06:12:45 2015

@author: danaukes
"""
import qt.QtCore as qc
import qt.QtGui as qg
import qt.QtSvg as qs
import popupcad
#from math import pi, sin, cos
#import numpy
import os

#from popupcad.filetypes.validators import StrictDoubleValidator

class DxfExportWidget(qg.QDialog):

    def __init__(self,folder = None):
        if folder is None:
            folder = popupcad.exportdir
        super(DxfExportWidget, self).__init__()

        button_accept = qg.QPushButton('Ok')
        button_reject= qg.QPushButton('Cancel')

        self.separate_layers = qg.QCheckBox('One layer per file')
        
        self.dirbox = qg.QLineEdit()
        self.dirbox.setText(folder)
        self.dirbutton = qg.QPushButton('...')
        layout0 = qg.QHBoxLayout()
        layout0.addWidget(self.dirbox)
        layout0.addWidget(self.dirbutton)
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button_accept)
        layout2.addWidget(button_reject)
        layout3 = qg.QVBoxLayout()
        layout3.addLayout(layout0)
        layout3.addWidget(self.separate_layers)
        layout3.addLayout(layout2)

        self.dirbutton.clicked.connect(self.selectExport)
        button_accept.clicked.connect(self.accept)
        button_reject.clicked.connect(self.reject)
        self.setLayout(layout3)

    def selectExport(self):
        directorypath = qg.QFileDialog.getExistingDirectory(self,"Select Directory",self.dirbox.text())
        if directorypath!='':
            directorypath = os.path.normpath(directorypath)
            self.dirbox.setText(directorypath)
        
    def accept_data(self):
        data = {}
        data['directory'] = self.dirbox.text()
        data['separate_layers'] = self.separate_layers.isChecked()
        return data
        
if __name__ == '__main__':
    import sys
    app = qg.QApplication(sys.argv)
    win = DxfExportWidget()
    win.exec_()
    sys.exit(app.exec_())
        