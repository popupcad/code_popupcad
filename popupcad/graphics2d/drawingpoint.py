# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from . import modes
from .graphicsitems import Common	
from interactivevertexbase import InteractiveVertexBase

class DrawingPoint(InteractiveVertexBase):
    isDeletable = True
    radius = 5
    z_below = 101
    z_above = 105
    def __init__(self,*args,**kwargs):
        super(DrawingPoint,self).__init__(*args,**kwargs)
    def refreshview(self):
        pass

class StaticDrawingPoint(InteractiveVertexBase):
    radius = 5
    z_below = 100
    z_above = 105
    def __init__(self,*args,**kwargs):
        super(StaticDrawingPoint,self).__init__(*args,**kwargs)
    def refreshview(self):
        pass
