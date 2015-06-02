# -*- coding: utf-8 -*-
"""
Created on Fri May 22 14:09:06 2015

@author: danaukes
"""

import sys
import popupcad

plugins = []
try:
    import popupcad_manufacturing_plugins
    plugins.append(popupcad_manufacturing_plugins)
except ImportError:
    print('Manufacturing Plugin Not Found')

if __name__ == "__main__":
    program = popupcad.filetypes.program.Program(plugins,*sys.argv)
    sys.exit(program.app.exec_())