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

    def renderprocess(self,filename):
        state = self.saveprerenderstate()
        self.prerender()
#        self.updatescenerect()        
        self.setSceneRect(self.itemsBoundingRect())
        generator = qs.QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(qc.QSize(self.width(), self.height()))
        generator.setResolution(90.0/popupcad.render_mm_scaling)
#        generator.setViewBox(self.sceneRect())
        generator.setTitle('SVG Generator Example Drawing')
        generator.setDescription('An SVG drawing created by the SVG Generator')

        painter = qg.QPainter() 
        
        painter.begin(generator)
        painter.setWorldMatrixEnabled(True)

        if popupcad.flip_y:
            t = qg.QTransform()
            t.scale(1,-1)
            s = popupcad.render_mm_scaling
            t.scale(s,s)
            t.translate(0,-self.height())
            painter.setWorldTransform(t)

        self.render(painter)
        painter.end()
        
        self.loadprerenderstate(*state)
        self.update()

        
        
