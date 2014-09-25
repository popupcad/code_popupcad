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

    def __init__(self,*args,**kwargs):

            
        super(DrawingPoint,self).__init__(*args,**kwargs)


        self.makemoveable(True)

    
    def refreshview(self):
        pass


