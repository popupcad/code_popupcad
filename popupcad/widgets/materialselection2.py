# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg

from popupcad.widgets.dragndroplist import DraggableListWidget, UserData


class CompositeMakeup(DraggableListWidget):

    def __init__(self):
        super(CompositeMakeup, self).__init__()
        self.setDragDropMode(self.DragDropMode.DragDrop)


class AvailableMaterials(DraggableListWidget):

    def __init__(self):
        super(AvailableMaterials, self).__init__()
        self.setDragDropMode(self.DragDropMode.DragOnly)

if __name__ == '__main__':
    import sys
    app = qg.QApplication(sys.argv)

    list1 = range(10)
    list1 = [UserData(str(item)) for item in list1]

    widget1 = AvailableMaterials()
    widget2 = CompositeMakeup()
    mw = qg.QWidget()
    layout = qg.QVBoxLayout()
    layout.addWidget(widget1)
    layout.addWidget(widget2)
    mw.setLayout(layout)

    widget1.linklist(list1)
    mw.show()
