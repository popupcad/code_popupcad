# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
import popupcad

icon={}
icon['3dview']='printapede.png'
icon['angle']='angle.png'
icon['bufferop']='bufferop.png'
icon['circle']='circle.png'
icon['distance']='distance.png'
icon['distancex']='distancex.png'
icon['distancey']='distancey.png'
icon['equal']='equal.png'
icon['export']='export.png'
icon['hingefoldop']='hingefoldop.png'
icon['horizontal']='horizontal.png'
icon['icons']='icons.png'
icon['import']='import.png'
icon['joinedges']='triangulate.png'
icon['layerop']='layerop.png'
icon['layers']='layers.png'
icon['line']='line.png'
icon['locate']='locate.png'
icon['metaop']='metaop.png'
icon['new']='new.png'
icon['open']='open.png'
icon['operations']='operations.png'
icon['pan']='hand.png'
icon['parallel']='parallel.png'
icon['perpendicular']='perpendicular.png'
icon['placeop']='placeop.png'
icon['pointline']='pointline.png'
icon['polygon']='polygon.png'
icon['polygons']='polygons.png'
icon['polyline']='polyline.png'
icon['popupcad']='printapede.png'
icon['quit']='quit.png'
icon['rectangle']='rectangle.png'
icon['redo']='redo.png'
icon['refresh']='refresh.png'
icon['save']='save.png'
icon['saveas']='save.png'
icon['select']='pointer.png'
icon['undo']='undo.png'
icon['vertical']='vertical.png'
icon['outersheet']='outersheet.png'
icon['outerweb']='outerweb.png'
icon['autosupport']='autosupport.png'
icon['firstpass']='firstpass.png'
icon['secondpass']='secondpass.png'
icon['autobridge']='autobridge.png'
icon['showconstraints']='showconstraints.png'

class Icon(qg.QIcon):
    def __init__(self,label,*args,**kwargs):
        import os
        filename = os.path.normpath(os.path.join(popupcad.supportfiledir,popupcad.supportfiles.icon[label]))
        super(Icon,self).__init__(filename,*args,**kwargs)
