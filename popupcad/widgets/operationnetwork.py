# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
import qt
import qt.QtCore as qc
import qt.QtGui as qg
import matplotlib
import matplotlib.pyplot as plt
plt.ion()
matplotlib.rcParams['backend.qt4']=qt.loaded
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy

spacing = .25

arrow_style = {}
arrow_style['color'] = 'black'
arrow_style['alpha'] = 1
arrow_style['zorder']=1
arrow_style['arrowstyle']=matplotlib.patches.ArrowStyle.Simple(head_length=10, head_width=10,tail_width = 1)
arrow_style['mutation_scale'] = 1
arrow_style['linewidth'] = 1
arrow_style['connectionstyle'] = matplotlib.patches.ConnectionStyle.Arc3(rad=-0.5)
arrow_style['shrinkA'] = 10
arrow_style['shrinkB'] = 10

text_style = {}
text_style['bbox']=None
text_style['clip_on']=True
text_style['size']=16
text_style['alpha'] = 1.0
text_style['color']='k'
text_style['family']='sans-serif'
text_style['fontweight'] = 'normal'
text_style['zorder'] = 2
text_style['horizontalalignment'] = 'right'
text_style['verticalalignment'] = 'center'

circle_style = {}
circle_style['s']=100
circle_style['c']='r'
circle_style['marker']='o'
circle_style['cmap']=None
circle_style['vmin']=None
circle_style['vmax']=None
circle_style['alpha']=1
circle_style['linewidths']=None
circle_style['label']=None
circle_style['zorder']= 0

class GraphView(qg.QWidget):
    def __init__(self, name='Name', title='Title', graph_title='Graph Title', parent = None):
        super(GraphView, self).__init__(parent)

        self.name = name
        self.graph_title = graph_title

        self.dpi = 100
        self.fig = Figure((5.0, 3.0), dpi = self.dpi, facecolor = (1,1,1), edgecolor = (0,0,0))
        self.axes = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas,self)
        self.layout = qg.QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.layout.setStretchFactor(self.canvas, 1)
        self.setLayout(self.layout)
        self.canvas.show()

    def clear(self):
        self.axes.clear()
    def plot(self,*args,**kwargs):
        self.axes.plot(*args,**kwargs)
    def draw(self):
        self.canvas.draw()
    def add_patch(self,patch):
        self.axes.add_patch(patch)
    def scatter(self,*args,**kwargs):
        self.axes.scatter(*args,**kwargs)
    def text(self,*args,**kwargs):
        self.axes.text(*args,**kwargs)


def action_method(parentwidget):
    from matplotlib.patches import FancyArrowPatch
    plt.ion()
    operations = parentwidget.design.operations
    ids = [operation.id for operation in operations]
    labels = dict([(operation.id,str(operation)) for operation in operations])
    links = []
    for child in operations:
        parentrefs = child.parentrefs()
        for parentref in parentrefs:
            links.append([parentref,child.id])
    edges = [(item[0],item[1]) for item in links]

    y = numpy.r_[spacing*len(ids):0:-1*spacing]
    xy = numpy.c_[y*0,y]    
    pos = dict([(item,pos) for item,pos in zip(ids,xy)])

    w = GraphView(parentwidget)
    w.axes.autoscale(True)
    labelpos = dict((key,value+[-0.1,0]) for key,value in pos.items())

    w.clear()
    for link,(x,y) in labelpos.items():
        w.text(x, y,labels[link],**text_style)
    for edge in edges:
        w.add_patch(FancyArrowPatch(pos[edge[0]],pos[edge[1]],**arrow_style))
    circlepos = numpy.array([item for item in pos.values()])
    w.scatter(circlepos[:,0],circlepos[:,1],**circle_style)        
    w.axes.axis('equal')
    w.axes.axis('off')
    w.draw()
    return w

if __name__ == '__main__':

    mbox = [['Dan','Sara'],['Dan','Bill'],['Sara','Bill']]
    labels= {}
    labels['Sara']='Sara'
    labels['Dan']='Dan'
    labels['Bill']='Bill'
    order = ['Dan','Sara','Bill']
    action_method(mbox,labels,order)
