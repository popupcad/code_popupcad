# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 16:49:22 2015

@author: danaukes
"""

import popupcad
import time
import sys
import PySide.QtGui as qg
import PySide.QtCore as qc
app = qg.QApplication(sys.argv)

t1 = time.time()
t2 = time.time()
dt = t2-t1
t1=t2
print('start',dt)

design = popupcad.filetypes.design.Design.load_yaml('folded.cad')
design.reprocessoperations()
