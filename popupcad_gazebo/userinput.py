# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

# -*- coding: utf-8 -*-
"""
Written by Aaron Gokaslan.
Email: aaronGokaslan<at>gmail.com.
Please see LICENSE.txt for full license.
"""

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.algorithms.python_syntax_formatter import PythonHighlighter

class UserInputIDE(qg.QDialog):

    def __init__(self):
        super(UserInputIDE, self).__init__()
        self.te = qg.QTextEdit()
#        self.te.setEnabled(False)
        self.ok = qg.QPushButton('Compile and Run Simulation')
        self.loadbtn = qg.QPushButton('Load a script')
        self.loadbtn.pressed.connect(self.loadFile)
        self.savebtn = qg.QPushButton('Save current script')
        self.savebtn.pressed.connect(self.saveFile)
        self.ok.pressed.connect(self.accept)
        layout = qg.QVBoxLayout()
        top_bar = qg.QHBoxLayout()
        top_bar.addWidget(self.loadbtn)
        top_bar.addWidget(self.savebtn)
        layout.addLayout(top_bar)        
        layout.addWidget(self.te)
        layout.addWidget(self.ok)
        self.setLayout(layout)
        PythonHighlighter(self.te.document())

    def appendText(self, text):
        current = self.te.toPlainText()
        current += text + "\n"
        self.te.setText(current)
        
    def sizeHint(self):
        return qc.QSize(800,600)
        
    def loadFile(self):
        from os.path import expanduser   
        home = expanduser("~")
        fname, _ = qg.QFileDialog.getOpenFileName(self, 'Open file',
            home)
        infile = open(fname, 'r')
        self.te.setPlainText(infile.read())
        infile.close()
    
    def saveFile(self):
        from os.path import expanduser
        home = expanduser("~")
        fname, _ = qg.QFileDialog.getSaveFileName(self, 'Save file',
            home)
        infile = open(fname, 'w')
        infile.write(self.te.toPlainText())
        infile.close()
        
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
