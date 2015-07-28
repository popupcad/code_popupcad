# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.operation2 import Operation2

class CodeExecOperation(Operation2):
    name = 'Code Execution Operation'
    code = ""    
    
    def __init__(self, *args):
        super(MultiValueOperation3, self).__init__()
        self.id = id(self)
        self.editdata(*args)

    def copy(self):
        new = type(self)(
            self.operation_links.copy(),
            self.code)
        new.id = self.id
        new.customname = self.customname
        return new

    def editdata(self, operation_links, code):
        super(CodeExecOperation, self).editdata(operation_links, {}, {})
        self.code = code
        
    @classmethod
    def buildnewdialog(cls, design, currentop):
        mw = UserInputIDE()
        mw.setWindowTitle('Internal Python IDE')
        mw.te.setReadOnly(False)
        return mw
        
    def buildeditdialog(self, design):
        mw = UserInputIDE()
        mw.setWindowTitle('Internal Python IDE')
        mw.te.setReadOnly(False)
        mw.te.setPlainText(self.code)     
        return dialog

    def operate(self, design):
        exec(self.code)