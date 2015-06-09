# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
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