# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:06:44 2015

@author: danaukes
"""

import sys
argv = [item.lower() for item in sys.argv]
if 'qt4' in argv:
    loaded = 'PyQt4'
elif 'qt5' in argv:
    loaded = 'PyQt5'
else:
    loaded = 'PySide'
