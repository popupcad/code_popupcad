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

design = popupcad.filetypes.design.Design.load_yaml('C:\\Users\\danaukes\\Dropbox\\downloads\\SLL03-backup.cad')

print(len(design.operations))
t2 = time.time()
dt = t2-t1
t1=t2
print('loaded. reprocessing...',dt)

design.reprocessoperations()

t2 = time.time()
dt = t2-t1
t1=t2
print('reprocessed. linking...',dt)

treewidget = popupcad.widgets.dragndroptree.DirectedDraggableTreeWidget()
treewidget.enable()
treewidget.setnetworkgenerator(design.network)
treewidget.linklist(design.operations)

t2 = time.time()
dt = t2-t1
t1=t2
print('linked. deleting...',dt)

while not not design.operations:
    treewidget.selectIndeces([(-1,0)])
    treewidget.deleteCurrent()
    
    t2 = time.time()
    dt = t2-t1
    t1=t2
    print('deleted...',dt)

