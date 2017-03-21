# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import os
import popupcad

import qt
import qt.QtCore as qc
import qt.QtGui as qg
from popupcad.graphics2d.graphicsscene import SimpleGraphicsScene
from popupcad.graphics2d.graphicsview import SimpleGraphicsView


class RenderWidget(qg.QWidget):

    def __init__(self, rect_size):
        super(RenderWidget, self).__init__()

#        gs = popupcad.graphics2d.graphicsscene.GraphicsScene()
#        gs = qg.QGraphicsScene()
#        gs.setBackgroundBrush(qg.QBrush(qg.QColor.fromRgbF(1, 1, 1, 1)))
#        self.gv = popupcad.graphics2d.graphicsview.GraphicsView(gs)
        self.gv = SimpleGraphicsView()
        gs = SimpleGraphicsScene(self.gv)
        self.gv.setScene(gs)
        self.gv.finish_init()
        
        self.gv.setRenderHint(qg.QPainter.Antialiasing)
#        self.gv.setRenderHint(qg.QPainter.HighQualityAntialiasing,True)
#        self.gv.setRenderHint(qg.QPainter.SmoothPixmapTransform,True)
#        self.gs.setBackgroundBrush(qg.QBrush(qg.QColor.fromRgbF(1,1,1,0.1)))
#        self.gs.setBackgroundBrush(qg.QBrush())

        self.directory_name = qg.QLineEdit()
        self.directory_button = qg.QPushButton('...')
        self.render_button = qg.QPushButton('render')

        layout = qg.QVBoxLayout()
#        layout.addWidget(self.gv)
        layout.addWidget(self.directory_name)
        layout.addWidget(self.directory_button)
        layout.addWidget(self.render_button)

        self.setLayout(layout)
        self.gv.setMinimumSize(*rect_size)
        self.gv.setMaximumSize(*rect_size)

        self.directory_button.clicked.connect(self.select_directory)
        self.render_button.clicked.connect(self.render)

    def render(self):
        path = self.directory_name.text()
        d = popupcad.filetypes.design.Design.load_yaml(path)
        d.reprocessoperations()
        directory, file = os.path.split(path)
        self.raster_design(d, directory)

    def select_directory(self):
        if qt.loaded == 'PySide':
            filename, selectedfilter = qg.QFileDialog.getOpenFileName(self, '', dir=self.directory_name.text(), filter='*.cad')
        elif qt.loaded == 'PyQt5':
            filename, selectedfilter = qg.QFileDialog.getOpenFileName(self, '', dir=self.directory_name.text(), filter='*.cad')
        else:
            filename = qg.QFileDialog.getOpenFileName(self, '', dir=self.directory_name.text(), filter='*.cad')
        
        print(filename)
        if filename != '':
            self.load_directory(filename)

    def load_directory(self, path):
        self.directory_name.setText(path)

    def clear(self):
        for item in self.gv.scene().items():
            self.gv.scene().removeItem(item)

    def raster_design(self, d, dest, filetype='png'):
        d.raster(destination=dest, filetype=filetype, gv=self.gv)

if __name__ == "__main__":
    import sys

    filter1 = '*.cad'
#    source = 'C:/Users/danaukes/popupCAD_files/designs'
#    source= os.path.normpath('C:/Users/danaukes/Desktop/source')
    destination = os.path.normpath('C:/Users/danaukes/Desktop')
    rect_size = 400, 300
    app = qg.QApplication(sys.argv)
    widget = RenderWidget(rect_size)
    widget.show()
#    path = 'C:\\Users\\danaukes\\Desktop\\118391752.cad'
#    d = popupcad.filetypes.design.Design.load_yaml(path)
#    d.reprocessoperations()
#    widget.raster_design(d,destination)
#    for dirname, dirnames, filenames in os.walk(source):
#        filenames2 = glob.glob(os.path.normpath(os.path.join(dirname,filter1)))
#        relpath = os.path.relpath(dirname,source)
#        local_dir = os.path.normpath(os.path.join(destination,relpath))
#        if not os.path.exists(local_dir):
#            os.mkdir(local_dir)
#        for filename in filenames2:
#            try:
#                full_path = os.path.normpath(os.path.join(dirname,filename))
#                d = popupcad.filetypes.design.Design.load_yaml(full_path)
#                d.reprocessoperations()
#                local_file = os.path.split(filename)[1]
#                local_file_root = os.path.splitext(local_file)[0]
#                local_file_dir = os.path.normpath(os.path.join(local_dir,local_file))
#                if not os.path.exists(local_file_dir):
#                    os.mkdir(local_file_dir)
#                widget.raster_design(d,local_file_dir)
#            except(Exception) as ex:
#                print(ex)

#    dirname = 'C:/Users/danaukes/popupCAD_files/designs'
#    filenames2 = ['asdfasdf.cad']
# for dirname, dirnames, filenames in os.walk(source):
##        filenames2 = glob.glob(os.path.normpath(os.path.join(dirname,filter1)))
#    relpath = os.path.relpath(dirname,source)
#    local_dir = os.path.normpath(os.path.join(destination,relpath))
#    if not os.path.exists(local_dir):
#        os.mkdir(local_dir)
#    for filename in filenames2:
#        try:
#            full_path = os.path.normpath(os.path.join(dirname,filename))
#            d = popupcad.filetypes.design.Design.load_yaml(full_path)
#            d.reprocessoperations()
#            local_file = os.path.split(filename)[1]
#            local_file_root = os.path.splitext(local_file)[0]
#            local_file_dir = os.path.normpath(os.path.join(local_dir,local_file))
#            if not os.path.exists(local_file_dir):
#                os.mkdir(local_file_dir)
# widget.raster_design(d,local_file_dir)
##            ii = 1
##            jj = 0
##            op = d.operations[ii]
##            out = op.output[jj]
#            for ii,op in enumerate(d.operations):
#                for jj,out in enumerate(op.output):
##                    widget = Widget(rect_size)
# widget.show()
#                    self= widget
#                    for item in self.gv.scene().items():
#                        self.gv.scene().removeItem(item)
#                    self.gv.scene().clear()
#                    self.gv.scene().update()
#                    self.gv.resetCachedContent()
#                    self.add_item_dict(out,d.return_layer_definition().layers)
#                    self.gv.zoomToFit(buffer = 0)
#                    self.raster(local_file_dir,ii,jj)
#        except(Exception) as ex:
#            print(ex)

#    sys.exit(app.exec_())
