# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


class UndoRedo(object):

    def __init__(self, get_current_method, load_method):
        self.get_current_method = get_current_method
        self.load_method = load_method
#        self.restartundoqueue()

    def restartundoqueue(self):
        file1 = self.get_current_method()
        self.undoqueue = [file1.copy()]
        self.index = 0

    def savesnapshot(self):
        file1 = self.get_current_method()
        self.undoqueue = self.undoqueue[:self.index + 1]
        self.undoqueue.append(file1.copy())
        self.index = len(self.undoqueue) - 1

    def loadindex(self, ii):
        self.load_method(self.undoqueue[ii])
        self.index = ii

    def undo(self):
        self.index -= 1
        if self.index < 0:
            self.index = 0
        self.load_method(self.undoqueue[self.index])

    def redo(self):
        self.index += 1
        m = len(self.undoqueue)
        if self.index >= m:
            self.index = m - 1
        self.load_method(self.undoqueue[self.index])
