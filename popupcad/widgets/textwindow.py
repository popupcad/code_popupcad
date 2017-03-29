# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


import qt.QtCore as qc
import qt.QtGui as qg

class TextWindow(qg.QWidget):

    def __init__(self):
        super(TextWindow, self).__init__()
        self.te = qg.QTextEdit()
#        self.te.setEnabled(False)

        layout = qg.QVBoxLayout()
        layout2 = qg.QHBoxLayout()
        self.close_button = qg.QPushButton('Close')
        layout.addWidget(self.te)
        layout2.addStretch()
        layout2.addWidget(self.close_button)
        layout2.addStretch()
        layout.addLayout(layout2)
        self.setLayout(layout)

        self.close_button.clicked.connect(self.close)
        
    def appendText(self, text):
        current = self.te.toPlainText()
        current += '\n' + text
        self.te.setText(current)
    def sizeHint(self):
        return qc.QSize(640,480)
if __name__ == "__main__":
    import sys
    app = qg.QApplication(sys.argv)
    mw = TextWindow()
    mw.appendText('asdfasdfasdf\nasdfasdfasdfasdfasdfasdfasfd')
    mw.appendText('asdfasdfasdf')
    mw.appendText('asdfasdfasdf')
    mw.appendText('asdfasdfasdf')
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())
