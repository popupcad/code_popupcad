# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:49:02 2015

@author: danaukes
"""

import sys
argv = [item.lower() for item in sys.argv]
import qt

if '--pyqt4' in argv:
    from PyQt4.QtSvg import * 
else:
    from PySide.QtSvg import * 
    