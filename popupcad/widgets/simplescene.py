# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtGui as qg    
from popupcad.graphics2d.graphicsscene import GraphicsScene
from popupcad.graphics2d.graphicsview import GraphicsView


class SimpleSceneDialog(qg.QDialog):
    def __init__(self,parent,items):
        super(SimpleSceneDialog,self).__init__(parent)
        
        self.scene = GraphicsScene()
        self.view = GraphicsView(self.scene)
        
        ok_button = qg.QPushButton('Ok')
        ok_button.pressed.connect(self.accept)
        cancel_button = qg.QPushButton('Cancel')
        cancel_button.pressed.connect(self.reject)

        mainlayout = qg.QVBoxLayout()
        mainlayout.addWidget(self.view)
        mainlayout.addWidget(ok_button)
        mainlayout.addWidget(cancel_button)

        self.setLayout(mainlayout)
        self.setModal(True)

        for item in items:
            self.scene.addItem(item)

if __name__ == "__main__":
    import sys
    app = qg.QApplication(sys.argv)
    window = SimpleSceneDialog(None,[])
    window.show()
    sys.exit(app.exec_())
