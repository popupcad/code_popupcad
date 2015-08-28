# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

#import popupcad
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.userinput import UserInputIDE

class CodeExecOperation(Operation2):
    name = 'Code Execution Operation'
    code = ""    
    
    def __init__(self, *args):
        super(CodeExecOperation, self).__init__()
        self.id = id(self)
        self.editdata(*args)

    def copy(self):
        new = type(self)(self.code)
        new.id = self.id
        new.customname = self.customname
        return new

    def editdata(self, code):
        super(CodeExecOperation, self).editdata({}, {}, {})
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
        return mw

    def operate(self, design):
        result = None
        my_locals = {'design':design,'result':result}
        exec(self.code,globals(),my_locals)
#        print(my_loc`als)
        result = my_locals['result']
        return result