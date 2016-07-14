# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import sys
import os
packages_path = ['.']
packages_path = [os.path.normpath(os.path.abspath(item)) for item in packages_path]
sys.path.extend(packages_path)
print(packages_path)
[print(os.listdir(item)) for item in packages_path]

import qt.QtCore as qc
import qt.QtGui as qg

#must import sympy before pyqtgraph
import sympy
#must import pyqtgraph before creating app
import pyqtgraph

app = qg.QApplication([sys.argv[0]])
import popupcad
program = popupcad.filetypes.program.Program(app, *sys.argv)
program.editor.destroy()
#app.quit()
#sys.exit()