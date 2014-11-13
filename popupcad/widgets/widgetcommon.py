# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
import popupcad

class WidgetCommon(object):
    def showhide2(self,window,action):
        if action.isChecked():
            window.show()
        else:
            window.hide()

    def buildToolbarMenu(self,actions,name):
        toolbar= qg.QToolBar(name)

        menu = qg.QMenu(name)

        for actiondata in actions:
            self.addItem(toolbar,menu,actiondata)
        return toolbar,menu
    
    def addToolbarMenu(self,actions,name):
        toolbar, menu = self.buildToolbarMenu(actions,name)            
        toolbar.setIconSize(qc.QSize(popupcad.settings.toolbar_icon_size,popupcad.settings.toolbar_icon_size))
        toolbar.setToolButtonStyle(qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setParent(self)
        self.addToolBar(qc.Qt.ToolBarArea.TopToolBarArea,toolbar)
        self.menuBar().addMenu(menu)
        return toolbar,menu
        
    def addToolbar(self,actions,name):
        toolbar, menu = self.buildToolbarMenu(actions,name)            
        toolbar.setIconSize(qc.QSize(popupcad.settings.toolbar_icon_size,popupcad.settings.toolbar_icon_size))
        toolbar.setToolButtonStyle(qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setParent(self)
        self.addToolBar(qc.Qt.ToolBarArea.TopToolBarArea,toolbar)
        return toolbar
        
    def addMenu(self,actions,name):
        toolbar, menu = self.buildToolbarMenu(actions,name)            
        self.menuBar().addMenu(menu)
        return menu

    def addItem(self,toolbar,menu,actiondata):
        if actiondata == None:
            toolbar.addSeparator()
            menu.addSeparator()
        elif actiondata.has_key('submenu'):
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

            menu.addMenu(submenu)
        else:
            action = self.buildaction(**actiondata)
            toolbar.addAction(action)
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
    