# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from shapely import speedups
if speedups.available:
    speedups.enable()

import sys

if hasattr(sys, 'frozen'):
    pass
else:
    import clear_compiled
    clear_compiled.clear_compiled()

import PySide.QtGui as qg
import PySide.QtCore as qc
import popupcad
import os

if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    app.setWindowIcon(popupcad.supportfiles.Icon('popupcad'))
    mw = popupcad.guis.editor.Editor()
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())