# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:47:02 2015

@author: danaukes
"""

import sys
argv = [item.lower() for item in sys.argv]

if '--pyqt4' in argv:
#    from PyQt4.Qt import QKeySequence, QTextCursor
    from PyQt4.QtGui import *

    QGraphicsView.DragMode.NoDrag = 0
    QGraphicsView.DragMode.ScrollHandDrag = 1
    QGraphicsView.DragMode.RubberBandDrag = 2

else:
    from PySide.QtGui import *
