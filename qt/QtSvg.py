# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:49:02 2015

@author: danaukes
"""

import qt

if qt.loaded == 'PyQt4':
    from PyQt4.QtSvg import * 
elif qt.loaded == 'PyQt5':
    from PyQt5.QtSvg import * 
else:
    from PySide.QtSvg import * 
    