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
import os
import sys
class OutputSelection(qg.QDialog):
    def __init__(self):
        super(OutputSelection,self).__init__()
        self.Inkscape= qg.QRadioButton('Inkscape')
        self.CorelDraw= qg.QRadioButton('CorelDraw')
        self.RenderDXF = qg.QRadioButton('DXF')
        self.Center = qg.QCheckBox('Center')
        
        self.Inkscape.clicked.connect(self.checkradio)
        self.CorelDraw.clicked.connect(self.checkradio)
        self.RenderDXF.clicked.connect(self.checkradio)

        self.rotation = qg.QLineEdit()
        self.rotation.setAlignment(qc.Qt.AlignRight)
        self.rotation.setText(str(0))
        self.rotation.setValidator(qg.QDoubleValidator(-999.0, 999.0, 1, self.rotation))

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')
        
        self.dirbox = qg.QLineEdit()
        self.dirbox.setText(popupcad.exportdir)
        self.dirbutton = qg.QPushButton('...')
        layout0 = qg.QHBoxLayout()
        layout0.addWidget(self.dirbox)
        layout0.addWidget(self.dirbutton)
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
        layout3.addLayout(layout0)
        layout3.addLayout(layout1)
        layout3.addWidget(self.Center)
        layout3.addLayout(layout4)
        layout3.addLayout(layout2)
        
        self.dirbutton.pressed.connect(self.selectExport)
        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)
        self.Inkscape.setChecked(True)
        self.setLayout(layout3)
        self.RenderDXF.setEnabled(sys.platform=='win32')
        
    def checkradio(self):
        if self.RenderDXF.isChecked():
            self.rotation.setText(str(0))
            self.rotation.setEnabled(False)
        else:
            self.rotation.setEnabled(True)
            
    def acceptdata(self):
        if self.Inkscape.isChecked():
            return popupcad.inkscape_mm_conversion,self.Center.isChecked(),float(self.rotation.text()),False,self.dirbox.text()
        elif self.CorelDraw.isChecked():
            return popupcad.coreldraw_mm_conversion,self.Center.isChecked(),float(self.rotation.text()),False,self.dirbox.text()
        elif self.RenderDXF.isChecked():
            return popupcad.inkscape_mm_conversion,self.Center.isChecked(),float(self.rotation.text()),True,self.dirbox.text()
        else:
            raise(Exception('nothing selected'))
            
    def selectExport(self):
        directorypath= qg.QFileDialog.getExistingDirectory(self, "Select Directory",self.dirbox.text() )
        directorypath=os.path.normpath(directorypath)
        self.dirbox.setText(directorypath)
        
class SVGOutputSupport(object):
    def screenShot(self):
        win = OutputSelection()
        accepted = win.exec_()
        if accepted:
            time = popupcad.basic_functions.return_formatted_time()
            self.renderprocess('2D_screenshot_'+time+'.svg',*win.acceptdata())

    def renderprocess(self,basename,scaling,center,rotation,render_dxf,exportdir):
#        save prerender state        
        tempmodes = []
        for item in self.items():
            try:
                tempmodes.append(item.mode)
            except AttributeError:
                tempmodes.append(None)
                
        selected = self.selectedItems()
        tempbrush = self.backgroundBrush()

#        prerender
        self.setBackgroundBrush(qg.QBrush())
        for item in self.items():
            try:
                item.updatemode(item.modes.mode_render)
            except AttributeError:
                pass
            pen = item.pen()
            pen.setWidth(pen.width()/scaling)
            item.setPen(pen)
            item.setSelected(False)

        filename = os.path.normpath(os.path.join(exportdir,basename))
        self.setSceneRect(self.itemsBoundingRect())
        generator = qs.QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(qc.QSize(self.width(), self.height()))
        generator.setResolution(90.0/scaling)
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
        if not render_dxf and center:
            v1 = numpy.array([-self.width()/2,-self.height()/2])
            theta = -rotation*pi/180
            R = numpy.array([[cos(theta),sin(theta)],[-sin(theta),cos(theta)]])
            v2 = R.dot(v1)
            t.translate(*v2)
        t.rotate(rotation)
        painter.setWorldTransform(t)

        self.render(painter)
        painter.end()

        for item in selected:
            item.setSelected(True)
        for item,mode in zip(self.items(),tempmodes):
            pen = item.pen()
            pen.setWidth(pen.width()*scaling)
            item.setPen(pen)
            try:
                item.updatemode(mode)
            except AttributeError:
                pass
        self.setBackgroundBrush(tempbrush)


        self.update()
        if render_dxf:
            xshift = 0
            yshift = 0
            if center:
                xshift = -self.width()/2/popupcad.internal_argument_scaling
                yshift = -self.height()/2/popupcad.internal_argument_scaling
            svg_to_dxf_files([filename],xshift,yshift)

def svg_to_dxf_files(filenames,xshift=0,yshift=0):
    import subprocess,os
    inkscape_path = popupcad.local_settings.inkscape_path
    pstoedit_path = popupcad.local_settings.pstoedit_path

    export_string_1 = '''"{0}"'''.format(inkscape_path) + ''' --export-area-page -P "{1}" "{0}"'''
    export_string_2 = '''"{0}" -xshift {1} -yshift {2} -dt -f '''.format(pstoedit_path,xshift*72/25.4,yshift*72/25.4)+'''"dxf:-polyaslines -mm" "{1}" "{0}"'''
    for input_file in filenames:
        dirname = os.path.dirname(input_file)
        tempfilename = os.path.join(dirname,'temp.ps')
        print(input_file)
        output_file = input_file.replace('.svg','.dxf')
    
        run1=subprocess.Popen(export_string_1.format(input_file,tempfilename),stdout = subprocess.PIPE,stderr = subprocess.PIPE)
        out1,err1 = run1.communicate()
        run2=subprocess.Popen(export_string_2.format(output_file,tempfilename),stdout = subprocess.PIPE,stderr = subprocess.PIPE)
        out2,err2 = run2.communicate()
    os.remove(tempfilename)
        
if __name__=='__main__':
    app = qg.QApplication(sys.argv)
    win  = OutputSelection()
    win.exec_()
    sys.exit(app.exec_())