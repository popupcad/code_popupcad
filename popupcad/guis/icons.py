# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import os
import glob

import qt.QtCore as qc
import qt.QtGui as qg
import popupcad

#necessary to implement this as a function because otherwise in some cases loading this package fails because qt hasn't been loaded first
def get_icons():
    filenames = glob.glob(os.path.join(popupcad.supportfiledir,'icons','*.png'))
    
    icons = {}
    for filename in filenames:
        key = os.path.split(filename)[1]
        key = os.path.splitext(key)[0]
        icons[key] = qg.QIcon(filename)
    return icons
