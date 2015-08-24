# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 11:40:37 2015

@author: danaukes
"""

import popupcad
from popupcad.guis.sketcher import Sketcher
import sys
import PySide.QtGui as qg

app = qg.QApplication(sys.argv)
sketch = popupcad.filetypes.sketch.Sketch.load_yaml('testpoints.sketch')
mw = Sketcher(None, sketch)
#mw.loadsketch(sketch)
#mw.show()
geom1 = mw.sketch.operationgeometry[0]
geom2 = mw.sketch.operationgeometry[1]

#item = mw.scene.itemAt(-17239.488120, 29782.449730)

#sys.exit(app.exec_())
