# -*- coding: utf-8 -*-
"""
Created on Tue May  5 19:29:06 2015

@author: danaukes
"""

import os
import popupcad
import PySide.QtGui as qg
import PySide.QtCore as qc

class RenderWidget(qg.QWidget):
    def __init__(self,rect_size):
        super(RenderWidget,self).__init__()

        self.gs = popupcad.graphics2d.graphicsscene.GraphicsScene()
        self.gv = popupcad.graphics2d.graphicsview.GraphicsView(self.gs)
        self.gv.setRenderHint(qg.QPainter.RenderHint.Antialiasing)
#        self.gv.setRenderHint(qg.QPainter.RenderHint.HighQualityAntialiasing,True)
#        self.gv.setRenderHint(qg.QPainter.RenderHint.SmoothPixmapTransform,True)
        self.gs.setBackgroundBrush(qg.QBrush(qg.QColor.fromRgbF(1,1,1,1)))
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
        directory,file = os.path.split(path)
        self.render_design(d,directory)
        
    def select_directory(self):
        path,selected_filter = qg.QFileDialog.getOpenFileName(self,'',dir = self.directory_name.text(),filter = '*.cad')
        print(path)
        if path!='':
            self.load_directory(path)

    def load_directory(self,path):
        self.directory_name.setText(path)
    
    def add_item_dict(self,output,layers):
        display_geometry = output.csg.to_generic_laminate().to_static() 
        for layer in layers:
            for geom in display_geometry[layer]:
                self.gs.addItem(geom)

    def raster(self,dest,filename,filetype = 'PNG'):
        e = self.gs.sceneRect()
        f = self.gv.mapFromScene(e.bottomLeft())
        g = self.gv.mapFromScene(e.topRight())
        rect = qc.QRect(f,g)
        im = qg.QImage(rect.width(),rect.height(),qg.QImage.Format.Format_ARGB32)
        painter = qg.QPainter(im)
        painter.setRenderHint(qg.QPainter.RenderHint.Antialiasing)
        self.gs.render(painter)
        filename = '{0}.{1}'.format(filename,filetype.lower())
        full_path = os.path.normpath(os.path.join(dest,filename))
        im.mirrored().save(full_path, filetype.upper())
        painter.end()
        
    def clear(self):
        for item in self.gs.items():
            self.gs.removeItem(item)
    
    def render_design(self,d,dest,filetype):
        for ii,op in enumerate(d.operations):
            for jj,out in enumerate(op.output):
                self.gs.clear()
                self.add_item_dict(out,d.return_layer_definition().layers)
                self.gv.zoomToFit(buffer = 0)
                filename = '{0:02.0f}_{1:02.0f}'.format(ii,jj)
                self.raster(dest,filename,filetype)


        
if __name__ == "__main__":
    import sys
    
    filter1 = '*.cad'
#    source = 'C:/Users/danaukes/popupCAD_files/designs'
#    source= os.path.normpath('C:/Users/danaukes/Desktop/source')
    destination= os.path.normpath('C:/Users/danaukes/Desktop')
    rect_size = 400,300
    app = qg.QApplication(sys.argv)
    widget = RenderWidget(rect_size)
#    widget.show()
    path = 'C:\\Users\\danaukes\\Desktop\\118391752.cad'
    d = popupcad.filetypes.design.Design.load_yaml(path)
    d.reprocessoperations()
    widget.render_design(d,destination)
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
#                widget.render_design(d,local_file_dir)    
#            except(Exception) as ex:
#                print(ex)
                
#    dirname = 'C:/Users/danaukes/popupCAD_files/designs'
#    filenames2 = ['asdfasdf.cad']         
##    for dirname, dirnames, filenames in os.walk(source):
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
##            widget.render_design(d,local_file_dir)
##            ii = 1
##            jj = 0
##            op = d.operations[ii]
##            out = op.output[jj]                
#            for ii,op in enumerate(d.operations):
#                for jj,out in enumerate(op.output):
##                    widget = Widget(rect_size)
##                    widget.show()
#                    self= widget
#                    for item in self.gs.items():
#                        self.gs.removeItem(item)
#                    self.gs.clear()
#                    self.gs.update()
#                    self.gv.resetCachedContent()
#                    self.add_item_dict(out,d.return_layer_definition().layers)
#                    self.gv.zoomToFit(buffer = 0)
#                    self.raster(local_file_dir,ii,jj)
#        except(Exception) as ex:
#            print(ex)

#    sys.exit(app.exec_())
