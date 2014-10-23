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
from math import pi, sin, cos
import numpy
class OutputSelection(qg.QDialog):
    def __init__(self):
        super(OutputSelection,self).__init__()
        self.Inkscape= qg.QRadioButton('Inkscape')
        self.CorelDraw= qg.QRadioButton('CorelDraw')
        self.RenderDXF = qg.QRadioButton('DXF')
        self.Center = qg.QCheckBox('Center')

        self.rotation = qg.QLineEdit()
        self.rotation.setAlignment(qc.Qt.AlignRight)
        self.rotation.setText(str(0))
        self.rotation.setValidator(qg.QDoubleValidator(-999.0, 999.0, 1, self.rotation))

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout1 = qg.QHBoxLayout()
        layout1.addWidget(self.Inkscape)
        layout1.addWidget(self.CorelDraw)
        layout1.addWidget(self.RenderDXF)
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)
        layout4 = qg.QHBoxLayout()
        layout4.addWidget(qg.QLabel('Rotation'))
        layout4.addWidget(self.rotation)
        layout3 = qg.QVBoxLayout()
        layout3.addLayout(layout1)
        layout3.addWidget(self.Center)
        layout3.addLayout(layout4)
        layout3.addLayout(layout2)
        
        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)
        self.Inkscape.setChecked(True)
        self.setLayout(layout3)
    def acceptdata(self):
        if self.Inkscape.isChecked():
            return popupcad.inkscape_mm_conversion,self.Center.isChecked(),float(self.rotation.text()),False
        elif self.CorelDraw.isChecked():
            return popupcad.coreldraw_mm_conversion,self.Center.isChecked(),float(self.rotation.text()),False
        elif self.RenderDXF.isChecked():
            return popupcad.inkscape_mm_conversion,self.Center.isChecked(),float(self.rotation.text()),True
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

    def renderprocess(self,filename,scaling,center = False,rotation = 0,render_dxf=False):
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

        t = qg.QTransform()
        if popupcad.flip_y:
            t.scale(1,-1)
        s = scaling
        t.scale(s,s)
        t.translate(0,-self.height())
        if center:
            v1 = numpy.array([-self.width()/2,-self.height()/2])
            theta = -rotation*pi/180
            R = numpy.array([[cos(theta),sin(theta)],[-sin(theta),cos(theta)]])
            v2 = R.dot(v1)
            t.translate(*v2)
        t.rotate(rotation)
        painter.setWorldTransform(t)

        self.render(painter)
        painter.end()
        
        self.loadprerenderstate(*state)
        self.update()
        if render_dxf:
            svg_to_dxf_files(filename)

def svg_to_dxf_files(*files):
    import subprocess,os
#    inkscape_path = 'C:\Program Files (x86)\Inkscape\inkscape.exe'
#    pstoedit_path = 'C:\Program Files\pstoedit\pstoedit.exe'
    inkscape_path = popupcad.settings.inkscape_path
    pstoedit_path = popupcad.settings.pstoedit_path

    export_string_1 = '''"{0}"'''.format(inkscape_path) + ''' --export-area-page -P {1} "{0}"'''
    export_string_2 = '''"{0}"'''.format(pstoedit_path) + ''' -dt -f "dxf:-polyaslines -mm" {1} "{0}"'''
    tempfilename = 'temp.ps'
    for input_file in files:
        print input_file
        output_file = input_file.replace('.svg','.dxf')
        run1=subprocess.call(export_string_1.format(input_file,tempfilename))
        run2=subprocess.call(export_string_2.format(output_file,tempfilename))
#        os.remove(input_file)
    os.remove(tempfilename)
        
if __name__=='__main__':
    import sys
    app = qg.QApplication(sys.argv)
    win  = OutputSelection()
    win.exec_()
#    mw.show()
#    mw.raise_()
    sys.exit(app.exec_())