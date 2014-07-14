# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
import PySide.QtCore as qc

class ListWidgetItem(qg.QListWidgetItem):
    def __init__(self,data,*args,**kwargs):
        super(ListWidgetItem,self).__init__(str(data),*args,**kwargs)
        self.customdata = data
        self.setData(qc.Qt.ItemDataRole.UserRole,data)
    def setCustomData(self,data):
        self.setData(qc.Qt.ItemDataRole.UserRole,data)
    def readCustomData(self):
        return self.data(qc.Qt.ItemDataRole.UserRole)
