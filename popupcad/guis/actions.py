# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import popupcad
import sys

import qt.QtCore as qc
import qt.QtGui as qg
import popupcad.guis.icons

class MenuSystem(object):
    shortcut_interpretation={}
    shortcut_interpretation['Ctrl+N']=qg.QKeySequence.New
    shortcut_interpretation['Ctrl+O']=qg.QKeySequence.Open
    shortcut_interpretation['Ctrl+S']=qg.QKeySequence.Save
    shortcut_interpretation['Ctrl+Shift+S']=qg.QKeySequence.SaveAs    
    shortcut_interpretation['Ctrl+Z']=qg.QKeySequence.Undo
    shortcut_interpretation['Ctrl+Y']=qg.QKeySequence.Redo
    shortcut_interpretation['Ctrl+X']=qg.QKeySequence.Cut
    shortcut_interpretation['Ctrl+C']=qg.QKeySequence.Copy
    shortcut_interpretation['Ctrl+V']=qg.QKeySequence.Paste

    def __init__(self,action_defs, toolbar_definitions,menu_struct,toolbar_struct,shortcuts,top_menu_key):
        self.action_defs = action_defs.copy()
        self.toolbar_definitions = toolbar_definitions.copy()
        self.menu_struct = menu_struct.copy()
        self.toolbar_struct = toolbar_struct.copy()
        self.shortcuts = shortcuts.copy()
        
        self.top_menu_key = top_menu_key

    def build(self,parent=None):
        for key,value in self.shortcuts.items():
            self.action_defs[key]['shortcut'] = value
        
        shortcuts_translation = dict([(value,value) for value in self.shortcuts.values()])
        shortcuts_translation.update(self.shortcut_interpretation)
        
        icons = popupcad.guis.icons.get_icons()
        self.actions = dict([(key,self.build_action(key,parent,self.action_defs,shortcuts_translation,icons)) for key in self.action_defs])
                
        self.other_items = {}
        self.other_items['']='separator'
        
        self.all_items = {}
        self.all_items.update(self.actions)
        self.all_items.update(self.other_items)
        
        self.menu_list = []
        self.main_menu = [self.build_menu_r2(key,self.menu_struct,self.all_items,self.menu_list) for key in self.menu_struct[self.top_menu_key]]
        self.toolbars,self.toolbar_menus = self.build_toolbar(self.toolbar_struct,self.top_menu_key,self.all_items,icons)

    @classmethod
    def build_menu_r2(cls,element,structure,dictionary,menu_list):
        menu = qg.QMenu(element)
        menu_list.append(menu)
        if element in structure:
            for item in structure[element]:
                if item in dictionary:
                    subelement = dictionary[item]
                    if isinstance(subelement,qg.QAction):
                        menu.addAction(subelement)
                    elif subelement=='separator': #if isinstance(item,type([])):
                        menu.addSeparator()
                else:
                    submenu = cls.build_menu_r2(item,structure,dictionary,menu_list)
                    menu.addMenu(submenu)
        return menu
                
    def build_toolbar(self,toolbar_structure,top_element,dictionary,icons):
        toolbars = []
        toolbar_menus = []
        for topitem in toolbar_structure[top_element]:
            toolbar = qg.QToolBar(topitem)
            toolbar.setIconSize(qc.QSize(popupcad.toolbar_icon_size,popupcad.toolbar_icon_size))
            toolbar.setToolButtonStyle(qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            for item in toolbar_structure[topitem]:
                if item in dictionary:
                    subelement = dictionary[item]
                    if isinstance(subelement,qg.QAction):
                        toolbar.addAction(subelement)
                    elif subelement=='separator': #if isinstance(item,type([])):
                        toolbar.addSeparator()
                else:
                    submenu = self.build_menu_r2(item,toolbar_structure,dictionary,toolbar_menus)
                    tb = qg.QToolButton()
                    try:
                        tb.setIcon(icons[self.toolbar_definitions[item]['icon']])
                    except KeyError:
                        pass
                    try:
                        tb.setText(self.toolbar_definitions[item]['text'])
                    except KeyError:
                        pass
                    tb.setMenu(submenu)
                    tb.setPopupMode(tb.ToolButtonPopupMode.InstantPopup)
                    tb.setToolButtonStyle(qc.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                    toolbar.addWidget(tb)
            toolbars.append(toolbar)
        return toolbars,toolbar_menus


    @staticmethod
    def build_action(key,parent,action_defs,shortcuts_translation,icons):
        kwargs = action_defs[key]

        action_kwargs = {}
        try:
            action_kwargs['icon']=icons[kwargs['icon']]
        except KeyError:
            pass

        try:
            action_kwargs['statusTip']=kwargs['statusTip']
        except KeyError:
            pass

        try:
            action_kwargs['shortcut'] = shortcuts_translation[kwargs['shortcut']]
        except KeyError:
            pass
        
        action = qg.QAction(parent,**action_kwargs)
            
        try:
            action.setText(kwargs['text'])
        except KeyError:
            pass
    
        try:
            action.setCheckable(kwargs['is_checkable'])
        except KeyError:
            pass
    
        try:
            action.setChecked(kwargs['is_checked'])
        except KeyError:
            pass

        try:
            parent_trigger_method_name = kwargs['triggered']
            if hasattr(parent_trigger_method_name,'__call__'):
                parent_trigger_method = parent_trigger_method_name
            else:
                parent_trigger_method = getattr(parent,parent_trigger_method_name)
            action.triggered.connect(parent_trigger_method)
        except (KeyError,AttributeError):
            pass
    
        return action
    
    def set_parent(self,parent):
        for item,value in self.actions.items():
            value.setParent(parent)

if __name__=='__main__':
    app = qg.QApplication([sys.argv[0]])
    m.build()
#    sys.exit(app.exec_())