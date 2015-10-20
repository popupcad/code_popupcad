# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
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
        super(OutputSelection, self).__init__()
        self.Inkscape = qg.QRadioButton('Inkscape')
        self.CorelDraw = qg.QRadioButton('CorelDraw')
        self.Center = qg.QCheckBox('Center')

        self.rotation = qg.QLineEdit()
        self.rotation.setAlignment(qc.Qt.AlignRight)
        self.rotation.setText(str(0))
        self.rotation.setValidator(
            qg.QDoubleValidator(-999.0, 999.0, 1, self.rotation))

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

        self.dirbutton.clicked.connect(self.selectExport)
        button1.clicked.connect(self.accept)
        button2.clicked.connect(self.reject)
        self.Inkscape.setChecked(True)
        self.setLayout(layout3)

    def acceptdata(self):
        if self.Inkscape.isChecked():
            return popupcad.inkscape_mm_conversion, self.Center.isChecked(), float(
                self.rotation.text()), self.dirbox.text()
        elif self.CorelDraw.isChecked():
            return popupcad.coreldraw_mm_conversion, self.Center.isChecked(), float(
                self.rotation.text()), self.dirbox.text()
        else:
            raise Exception

    def selectExport(self):
        directorypath = qg.QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.dirbox.text())
        directorypath = os.path.normpath(directorypath)
        self.dirbox.setText(directorypath)


class SVGOutputSupport(object):

    def screenShot(self):
        win = OutputSelection()
        accepted = win.exec_()
        if accepted:
            time = popupcad.basic_functions.return_formatted_time()
            self.renderprocess(
                '2D_screenshot_' +
                time +
                '.svg',
                *
                win.acceptdata())

    def renderprocess(
            self,
            basename,
            scaling,
            center,
            rotation,
            exportdir):
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
            pen.setWidth(pen.width() / scaling)
            item.setPen(pen)
            item.setSelected(False)

        filename = os.path.normpath(os.path.join(exportdir, basename))
        self.setSceneRect(self.itemsBoundingRect())
        generator = qs.QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(qc.QSize(self.width(), self.height()))
        generator.setResolution(90.0 / scaling)
        generator.setTitle('SVG Generator Example Drawing')
        generator.setDescription('An SVG drawing created by the SVG Generator')

        painter = qg.QPainter()

        painter.begin(generator)
        painter.setWorldMatrixEnabled(True)

        t = qg.QTransform()
        if popupcad.flip_y:
            t.scale(1, -1)
        s = scaling
        t.scale(s, s)
        t.translate(0, -self.height())
        if center:
            v1 = numpy.array([-self.width() / 2, -self.height() / 2])
            theta = -rotation * pi / 180
            R = numpy.array(
                [[cos(theta), sin(theta)], [-sin(theta), cos(theta)]])
            v2 = R.dot(v1)
            t.translate(*v2)
        t.rotate(rotation)
        painter.setWorldTransform(t)

        self.render(painter)
        painter.end()

        for item in selected:
            item.setSelected(True)
        for item, mode in zip(self.items(), tempmodes):
            pen = item.pen()
            pen.setWidth(pen.width() * scaling)
            item.setPen(pen)
            try:
                item.updatemode(mode)
            except AttributeError:
                pass
        self.setBackgroundBrush(tempbrush)

        self.update()

if __name__ == '__main__':
    app = qg.QApplication(sys.argv)
    win = OutputSelection()
    win.exec_()
    sys.exit(app.exec_())
