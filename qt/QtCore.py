# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 07:42:22 2015

@author: danaukes
"""

import sys
argv = [item.lower() for item in sys.argv]

if '--pyqt4' in argv:
    from PyQt4.QtCore import *
#    from PyQt4.QtCore import QCoreApplication 
    from PyQt4.QtCore import Qt 
    from PyQt4.QtCore import pyqtSignal as Signal 
#    from PyQt4.QtCore import pyqtSlot as Slot 
#    from PyQt4.QtCore import pyqtProperty as Property 
#    from PyQt4.QtCore import QT_VERSION_STR as __version__
    
    Qt.ItemSelectionMode.ContainsItemShape = 0
    Qt.ItemSelectionMode.IntersectsItemShape = 1
    Qt.ItemSelectionMode.ContainsItemBoundingRect = 2
    Qt.ItemSelectionMode.IntersectsItemBoundingRect = 3
    
else:
    import PySide.QtCore
#    __version__ = PySide.QtCore.__version__ 
    from PySide.QtCore import * 
