# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

class UndoRedo(object):
    def __init__(self,get_current_method,load_method):
        self.get_current_method = get_current_method
        self.load_method = load_method
#        self.restartundoqueue()
    def restartundoqueue(self):
        self.undoqueue = []
        self.redoqueue = []
        self.savesnapshot()
    def savesnapshot(self):
        file1 = self.get_current_method()
        self.undoqueue.append(file1.copy())
        self.redoqueue = []
    def undo(self):
        try:
            sketch = self.undoqueue.pop()
            self.redoqueue.append(self.get_current_method())
            self.load_method(sketch)
        except IndexError:
            print('beginning of undo queue')

    def redo(self):
        try:
            sketch = self.redoqueue.pop()
            self.undoqueue.append(self.get_current_method())
            self.load_method(sketch)
        except IndexError:
            print('end of redo queue')
        