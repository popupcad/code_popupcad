# -*- coding: utf-8 -*-
"""
Created on Fri May 22 14:09:06 2015

@author: danaukes
"""

import sys
import popupcad

if __name__ == "__main__":
    args = sys.argv.copy()
    args.append('--deprecated')
    program = popupcad.filetypes.program.Program(*args)
    sys.exit(program.app.exec_())
    
