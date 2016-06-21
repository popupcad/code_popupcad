# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt

if qt.loaded == 'PyQt4':
    from PyQt4.QtSvg import * 
elif qt.loaded == 'PyQt5':
    from PyQt5.QtSvg import * 
elif qt.loaded == 'PySide':
    from PySide.QtSvg import * 
