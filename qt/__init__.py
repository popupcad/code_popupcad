# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import sys
argv = [item.lower() for item in sys.argv]
if 'qt4' in argv:
    loaded = 'PyQt4'
elif 'qt5' in argv:
    loaded = 'PyQt5'
elif 'pyside' in argv:
    loaded = 'PySide'
else:
    loaded = 'PySide'
