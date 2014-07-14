# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg

class WidgetCommon(object):
    def showhide(self,window):
        if window.isHidden():
            window.show()
        else:
            window.hide()

    def buildActions(self,actions,name='toolbar',area=qc.Qt.ToolBarArea.TopToolBarArea,size=48,style=qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon,addtoolbar= True,addmenu = True):
        if addmenu:
            menu= self.menuBar().addMenu(name)
        if addtoolbar:
            toolbar= qg.QToolBar(name,self)
            toolbar.setIconSize(qc.QSize(size,size))
            toolbar.setToolButtonStyle(style)
            self.addToolBar(area,toolbar)

        for actiondata in actions:
            if actiondata == None:
                if addtoolbar:
                    toolbar.addSeparator()
                if addmenu:
                    menu.addSeparator()
            else:
                if actiondata.has_key('submenu'):
                    subactions = actiondata.pop('submenu')
                    actions = [self.buildaction(item) for item in subactions]
                    submenu = qg.QMenu(actiondata['text'])
                    for action in actions:
                        submenu.addAction(action)
                    if addtoolbar:
                        tb = qg.QToolButton()
                        try:
                            tb.setIcon(actiondata['kwargs']['icon'])
                        except KeyError:
                            pass

                        try:
                            tb.setText(actiondata['text'])
                        except KeyError:
                            pass

                        tb.setMenu(submenu)
#                        tb.setPopupMode(tb.ToolButtonPopupMode.MenuButtonPopup)
                        tb.setPopupMode(tb.ToolButtonPopupMode.InstantPopup)
                        tb.setToolButtonStyle(qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                        toolbar.addWidget(tb)
                    if addmenu:
                        menu.addMenu(submenu)
                    
                else:
                    action = self.buildaction(actiondata)
                    
                    if addtoolbar:
                        toolbar.addAction(action)
                    if addmenu:
                        menu.addAction(action)   

    def buildaction(self,actiondata):
        kwargs = actiondata['kwargs']
        text= actiondata['text']
        action = qg.QAction(text,self,**kwargs)

        try:
            prepmethod = actiondata['prepmethod']
            prepmethod(action)
        except KeyError:
            pass
        
        return action
        
    @staticmethod
    def builddialog(widget):
        layout = qg.QVBoxLayout()
        layout.addWidget(widget)        
        
        dialog = qg.QDialog()
        dialog.setLayout(layout)
        dialog.setModal(True)
        return dialog
    