# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import sys
import PySide.QtGui as qg
app = qg.QApplication(sys.argv[0])
import popupcad
plugins = []

try:
    import popupcad_manufacturing_plugins
    plugins.append(popupcad_manufacturing_plugins)
except ImportError:
    print('Manufacturing Plugin Not Found')

try:
    import popupcad_gazebo
    plugins.append(popupcad_gazebo)
except ImportError:
    print('Gazebo Plugin Not Found')

program = popupcad.filetypes.program.Program(app, plugins, *sys.argv)
sys.exit(app.exec_())