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

    def buildToolbar(self,actions,name='toolbar',area=qc.Qt.ToolBarArea.TopToolBarArea,size=48,style=qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon):
        toolbar= qg.QToolBar(name)
        toolbar.setIconSize(qc.QSize(size,size))
        toolbar.setToolButtonStyle(style)
        for actiondata in actions:
            self.addToolbarItem(toolbar,actiondata)
        toolbar.setParent(self)
        self.addToolBar(area,toolbar)
        return toolbar
            
    def buildMenu(self,actions,name):
        menu= self.menuBar().addMenu(name)
        for actiondata in actions:
            self.addMenuItem(menu,actiondata)
        return menu

    def addToolbarItem(self,toolbar,actiondata):
        if actiondata == None:
            toolbar.addSeparator()
        else:
            if actiondata.has_key('submenu'):
                submenu = self.buildSubmenu(actiondata)
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
                tb.setPopupMode(tb.ToolButtonPopupMode.InstantPopup)
                tb.setToolButtonStyle(qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                toolbar.addWidget(tb)
                
            else:
                action = self.buildaction(**actiondata)
                toolbar.addAction(action)

    def addMenuItem(self,menu,actiondata):
            if actiondata == None:
                menu.addSeparator()
            else:
                if actiondata.has_key('submenu'):
                    submenu = self.buildSubmenu(actiondata)
                    menu.addMenu(submenu)
                else:
                    action = self.buildaction(**actiondata)
                    menu.addAction(action)                      

    def buildSubmenu(self,actiondata):
        subactions = actiondata['submenu']
        actions = [self.buildaction(**item) for item in subactions]
        submenu = qg.QMenu(actiondata['text'])
        for action in actions:
            submenu.addAction(action)
        return submenu
        
    def buildaction(self,text = '',kwargs = {},prepmethod = None):
        action = qg.QAction(text,self,**kwargs)
        if prepmethod!=None:
            prepmethod(action)
        return action
        
    @staticmethod
    def builddialog(widget):
        layout = qg.QVBoxLayout()
        layout.addWidget(widget)        
        
        dialog = qg.QDialog()
        dialog.setLayout(layout)
        dialog.setModal(True)
        return dialog
    