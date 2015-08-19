# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 23:00:35 2015

@author: danaukes
"""

import os
import PySide.QtCore as qc
import PySide.QtGui as qg
import popupcad.supportfiles
icons = {}
for key,value in popupcad.supportfiles.icon.items():
    icons[key] = qg.QIcon(os.path.normpath(os.path.join(popupcad.supportfiledir,value)))
