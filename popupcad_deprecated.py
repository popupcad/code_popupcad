# -*- coding: utf-8 -*-
"""
Created on Fri May 22 14:09:06 2015

@author: danaukes
"""

import sys
import popupcad

if __name__ == "__main__":
    args = list(sys.argv)
    args.append('--deprecated')
    program = popupcad.filetypes.program.Program(*args)
    try:
        import popupcad_manufacturing_plugins
        popupcad_manufacturing_plugins.initialize(program.editor)
    except ImportError:
        print('Manufacturing Plugin Not Found')
    sys.exit(program.app.exec_())
    
