# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.guis.sketcher import Sketcher
import sys
import PySide.QtGui as qg
if __name__=='__main__':
    
    app = qg.QApplication(sys.argv)
    sketch = popupcad.filetypes.sketch.Sketch.load_yaml('testpoints.sketch')
    mw = Sketcher(None, sketch)
    #mw.loadsketch(sketch)
    #mw.show()
    geom1 = mw.sketch.operationgeometry[0]
    geom2 = mw.sketch.operationgeometry[1]
    
    #item = mw.scene.itemAt(-17239.488120, 29782.449730)
    
    #sys.exit(app.exec_())
