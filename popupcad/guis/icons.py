# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import os
import glob
import qt
qc = qt.QtCore
qg = qt.QtGui
import popupcad

filenames = glob.glob(os.path.join(popupcad.supportfiledir,'icons','*.png'))

def build():
    icons = {}
    for filename in filenames:
        key = os.path.split(filename)[1]
        key = os.path.splitext(key)[0]
        icons[key] = qg.QIcon(filename)
    return icons