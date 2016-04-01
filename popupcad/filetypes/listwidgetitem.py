# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg

class ListWidgetItem(qg.QListWidgetItem):

    def __init__(self, data, *args, **kwargs):
        super(ListWidgetItem, self).__init__(str(data), *args, **kwargs)
        self.customdata = data
        self.setData(qc.Qt.ItemDataRole.UserRole, data)

    def setCustomData(self, data):
        self.setData(qc.Qt.ItemDataRole.UserRole, data)

    def readCustomData(self):
        return self.data(qc.Qt.ItemDataRole.UserRole)
