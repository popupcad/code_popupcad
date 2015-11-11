# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt
import qt.QtCore as qc
import qt.QtGui as qg

class ErrorLog(qg.QWidget):

    def __init__(self):
        super(ErrorLog, self).__init__()
        self.te = qg.QTextEdit()
#        self.te.setEnabled(False)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.te)
        self.setLayout(layout)

    def appendText(self, text):
        current = self.te.toPlainText()
        current += '\n' + text
        self.te.setText(current)
    def sizeHint(self):
        return qc.QSize(800,600)
if __name__ == "__main__":
    import sys
    app = qg.QApplication(sys.argv)
    mw = ErrorLog()
    mw.appendText('asdfasdfasdf\nasdfasdfasdfasdfasdfasdfasfd')
    mw.appendText('asdfasdfasdf')
    mw.appendText('asdfasdfasdf')
    mw.appendText('asdfasdfasdf')
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())
