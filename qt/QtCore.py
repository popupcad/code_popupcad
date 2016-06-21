# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt

if qt.loaded == 'PyQt4':
    from PyQt4.QtCore import *
    from PyQt4.QtCore import Qt 
    from PyQt4.QtCore import pyqtSignal as Signal 

elif qt.loaded == 'PyQt5':
    from PyQt5.QtCore import *
    from PyQt5.QtCore import Qt 
    from PyQt5.QtCore import pyqtSignal as Signal 

elif qt.loaded == 'PySide':
    import PySide.QtCore
    from PySide.QtCore import * 