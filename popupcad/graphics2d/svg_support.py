# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg
import PySide.QtSvg as qs
import popupcad

class OutputSelection(qg.QDialog):
    def __init__(self):
        super(OutputSelection,self).__init__()
        self.Inkscape= qg.QRadioButton('Inkscape')
        self.CorelDraw= qg.QRadioButton('CorelDraw')

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout1 = qg.QHBoxLayout()
        layout1.addWidget(self.Inkscape)
        layout1.addWidget(self.CorelDraw)
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)
        layout3 = qg.QVBoxLayout()
        layout3.addLayout(layout1)
        layout3.addLayout(layout2)
        
        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)
        self.Inkscape.setChecked(True)
        self.setLayout(layout3)
    def acceptdata(self):
        if self.Inkscape.isChecked():
            return popupcad.inkscape_mm_conversion
        elif self.CorelDraw.isChecked():
            return popupcad.coreldraw_mm_conversion
        else:
            raise(Exception('nothing selected'))
class SVGOutputSupport(object):
    def saveprerenderstate(self):
        tempmodes = []
        for item in self.items():
            try:
                tempmodes.append(item.mode)
            except AttributeError:
                tempmodes.append(None)
                
        selected = self.selectedItems()
        tempbrush = self.backgroundBrush()
        return tempmodes, selected,tempbrush

    def prerender(self):
        self.setBackgroundBrush(qg.QBrush())
        for item in self.items():
            try:
                item.updatemode(item.modes.mode_render)
            except AttributeError:
                pass
            item.setSelected(False)

    def loadprerenderstate(self,tempmodes,selected,tempbrush):
        for item in selected:
            item.setSelected(True)
        for item,mode in zip(self.items(),tempmodes):
            try:
                item.updatemode(mode)
            except AttributeError:
                pass
        self.setBackgroundBrush(tempbrush)

    def renderprocess(self,filename,scaling):
        state = self.saveprerenderstate()
        self.prerender()
#        self.updatescenerect()        
        self.setSceneRect(self.itemsBoundingRect())
        generator = qs.QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(qc.QSize(self.width(), self.height()))
        generator.setResolution(90.0/scaling)
#        generator.setViewBox(self.sceneRect())
        generator.setTitle('SVG Generator Example Drawing')
        generator.setDescription('An SVG drawing created by the SVG Generator')

        painter = qg.QPainter() 
        
        painter.begin(generator)
        painter.setWorldMatrixEnabled(True)

        if popupcad.flip_y:
            t = qg.QTransform()
            t.scale(1,-1)
            s = scaling
            t.scale(s,s)
            t.translate(0,-self.height())
            painter.setWorldTransform(t)

        self.render(painter)
        painter.end()
        
        self.loadprerenderstate(*state)
        self.update()

        
        
if __name__=='__main__':
    import sys
    app = qg.QApplication(sys.argv)
    win  = OutputSelection()
    win.exec_()
#    mw.show()
#    mw.raise_()
    sys.exit(app.exec_())