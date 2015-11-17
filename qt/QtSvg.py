# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:49:02 2015

@author: danaukes
"""

import qt

if qt.pyqt_loaded:
    from PyQt4.QtSvg import * 
else:
    from PySide.QtSvg import * 
    