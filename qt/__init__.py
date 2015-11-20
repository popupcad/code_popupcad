# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:06:44 2015

@author: danaukes
"""

import sys
argv = [item.lower() for item in sys.argv]
if '--pyqt4' in argv:
    loaded = 'PyQt4'
    pyqt_loaded = True
    pyside_loaded = False
else:
    loaded = 'PySide'
    pyqt_loaded = False
    pyside_loaded = True
