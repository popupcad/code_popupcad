# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import sys

if hasattr(sys, 'frozen'):
    pass
else:
    import clear_compiled
    clear_compiled.clear_compiled()
    
import PySide.QtGui as qg

import popupcad
import popupcad_deprecated
popupcad.deprecated = popupcad_deprecated
sys.modules['popupcad.deprecated'] = popupcad_deprecated

if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    app.setWindowIcon(popupcad.supportfiles.Icon('popupcad'))
    mw = popupcad.guis.upgrader.Editor()
    if len(sys.argv)>1:
        mw.open(filename = sys.argv[1])
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())
    
