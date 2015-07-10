# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 15:20:52 2015

@author: skylion
"""

# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtGui as qg
import PySide.QtCore as qc


#TODO change this to use a 
class UserInputIDE(qg.QDialog):

    def __init__(self):
        super(UserInputIDE, self).__init__()
        self.te = qg.QTextEdit()
#        self.te.setEnabled(False)
        self.ok = qg.QPushButton('ok')
        self.ok.pressed.connect(self.accept)
        layout = qg.QVBoxLayout()
        layout.addWidget(self.te)
        layout.addWidget(self.ok)
        self.setLayout(layout)

    def appendText(self, text):
        current = self.te.toPlainText()
        current += text + "\n"
        self.te.setText(current)
        from popupcad_gazebo import syntax
        syntax.PythonHighlighter(self.te.document())
        
    def sizeHint(self):
        return qc.QSize(800,600)
        
if __name__ == "__main__":
    import sys
    app = qg.QApplication(sys.argv)
    
    mw = UserInputIDE()
    mw.appendText('asdfasdfasdf\nasdfasdfasdfasdfasdfasdfasfd')
    mw.appendText('asdfasdfasdf')
    mw.appendText('asdfasdfasdf')
    mw.appendText('asdfasdfasdf')
    mw.te.setReadOnly(False)
    mw.te.document()
    mw.exec_()
    sys.exit(app.exec_())
