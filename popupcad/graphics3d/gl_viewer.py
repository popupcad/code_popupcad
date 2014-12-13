# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide
from PySide import QtCore
from PySide import QtGui
import PySide.QtCore as qc
import PySide.QtGui as qg
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy
#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')

class GLObjectViewer(qg.QWidget):
    def __init__(self,*args,**kwargs):
        super(GLObjectViewer,self).__init__(*args,**kwargs)
        self.slider = qg.QSlider()
        self.slider.setMinimum(1)
        self.slider.setMaximum(1000)
        self.slider.setTickInterval(1)
        layout = qg.QHBoxLayout()
        self.view = GLViewWidget(self)

        layout.addWidget(self.view)
        layout.addWidget(self.slider)
        self.slider.setValue(self.view.z_zoom)
        self.slider.valueChanged.connect(self.view.update_zoom)
        self.setLayout(layout)
    def screenshot(self):
        self.view.screenshot()


class GLViewWidget(gl.GLViewWidget):
    def __init__(self,*args,**kwargs):
        super(GLViewWidget,self).__init__(*args,**kwargs)        
        self.z_zoom=10
        self.setCameraPosition(distance=30000)
#        self.setMinimumSize(300,300)
        self.setSizePolicy(qg.QSizePolicy.Policy.MinimumExpanding,qg.QSizePolicy.Policy.MinimumExpanding)
#        c = pg.mkColor(120,120,200)
        c = pg.mkColor(1,1,1)
#        print(c)
        self.setBackgroundColor(c)
            
    def clear(self):
        while len(self.items)>0:
            self.removeItem(self.items[0])
            
    def add_grid(self):
        g = gl.GLGridItem()
        g.scale(2,2,1)
        self.addItem(g)
    def screenshot(self):
        import popupcad
        import os
        time = popupcad.basic_functions.return_formatted_time()
        filename = os.path.normpath(os.path.join(popupcad.exportdir,'3D_screenshot_'+time+'.png'))

        self.grabFrameBuffer().save(filename)

        
    def update_object(self,zvalue,tris,layers):
        self.tris = tris
        self.layers = layers
        self.zvalue = zvalue
        self.build_object()

    def update_zoom(self,value):
        self.z_zoom = value
        self.build_object()
        
    def build_object(self):
        self.clear()
#        self.add_grid()
        for layer in self.layers:
            tri = numpy.array(self.tris[layer])
            if len(tri)>0:
                z = numpy.ones((tri.shape[0],tri.shape[1],1))*self.zvalue[layer]*self.z_zoom
                tri = numpy.concatenate((tri,z),2)
                color = layer.color
#                print(color)
                colors = numpy.zeros((tri.shape[0],3,4))
                for ii in range(tri.shape[0]):
                    for jj in range(3):
                        colors[ii,jj] = color
                m = gl.GLMeshItem(vertexes = tri,vertexColors = colors,edgeColor = (1,1,1,1))
                self.addItem(m)

    def add_default_item(self):
        verts = numpy.empty((36, 3, 3), dtype=numpy.float32)
        theta = numpy.linspace(0, 2*numpy.pi, 37)[:-1]
        verts[:,0] = numpy.vstack([2*numpy.cos(theta), 2*numpy.sin(theta), [0]*36]).T
        verts[:,1] = numpy.vstack([4*numpy.cos(theta+0.2), 4*numpy.sin(theta+0.2), [-1]*36]).T
        verts[:,2] = numpy.vstack([4*numpy.cos(theta-0.2), 4*numpy.sin(theta-0.2), [1]*36]).T
            
        colors = numpy.random.random(size=(verts.shape[0], 3, 4))
        m2 = gl.GLMeshItem(vertexes=verts, vertexColors=colors, smooth=False, shader='balloon', 
                           drawEdges=True, edgeColor=(1, 1, 0, 1))
        m2.translate(-5, 5, 0)
        self.addItem(m2)
    def sizeHint(self):
        return qc.QSize(300,300)
        
        
if __name__ == '__main__':
    import sys
    app = qg.QApplication(sys.argv)
    mw = GLObjectViewer()
    mw.view.add_default_item()
    mw.show()
#    sys.exit(app.exec_())        