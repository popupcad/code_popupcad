# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
import PySide.QtCore as qc
import popupcad
import sys
import os
    
if __name__ == "__main__":

    app = qg.QApplication(sys.argv)
    app.setWindowIcon(popupcad.supportfiles.Icon('popupcad'))
    mw = popupcad.guis.editor.Editor()
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())