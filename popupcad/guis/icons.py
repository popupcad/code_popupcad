# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 23:00:35 2015

@author: danaukes
"""

import os
import glob
import PySide.QtGui as qg
import popupcad

filenames = glob.glob(os.path.join(popupcad.supportfiledir,'icons','*.png'))

def build():
    icons = {}
    for filename in filenames:
        key = os.path.split(filename)[1]
        key = os.path.splitext(key)[0]
        icons[key] = qg.QIcon(filename)
    return icons