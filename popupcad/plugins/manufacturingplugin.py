# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:05:16 2014

@author: danaukes
"""

import popupcad
from popupcad.supportfiles import Icon
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.plugin import Plugin

class ManufacturingPlugin(Plugin):
    def __init__(self, editor, design):
        supportactions= []
        supportactions.append({'text':'Sheet','kwargs':{'icon':Icon('outersheet'),'triggered':lambda:editor.newoperation(popupcad.manufacturing.OuterSheet2)}})
        supportactions.append({'text':'&Web','kwargs':{'icon':Icon('outerweb'),'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_U,'triggered':lambda:editor.newoperation(popupcad.manufacturing.AutoWeb3)}})
        supportactions.append({'text':'S&upport','kwargs':{'icon':Icon('autosupport'),'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_W,'triggered':lambda:editor.newoperation(popupcad.manufacturing.SupportCandidate3)}})
        supportactions.append({'text':'Custom Support','kwargs':{'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_W,'triggered':lambda:editor.newoperation(popupcad.manufacturing.CustomSupport3)}})
        
        manufacturingactions = []
        manufacturingactions.append({'text':'Keep-outs','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:editor.newoperation(popupcad.manufacturing.KeepOut2)}})
        manufacturingactions.append({'text':'Supports','submenu':supportactions,'kwargs':{'icon':Icon('outerweb')}})
        manufacturingactions.append({'text':'Tool Clearance','kwargs':{'triggered':lambda:editor.newoperation(popupcad.manufacturing.ToolClearance2)}})
        manufacturingactions.append({'text':'Cuts','kwargs':{'icon':Icon('firstpass'),'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_1,'triggered':lambda:editor.newoperation(popupcad.manufacturing.CutOperation2)}})
        manufacturingactions.append({'text':'Removability','kwargs':{'triggered':lambda:editor.newoperation(popupcad.manufacturing.Removability)}})
        manufacturingactions.append({'text':'Identify Bodies','kwargs':{'triggered':lambda:editor.newoperation(popupcad.manufacturing.IdentifyBodies)}})
        manufacturingactions.append({'text':'Identify Rigid Bodies','kwargs':{'triggered':lambda:editor.newoperation(popupcad.manufacturing.IdentifyRigidBodies)}})
        for item in manufacturingactions:
            editor.addMenuItem(editor.menu_manufacturing,item)
            editor.addToolbarItem(editor.toolbar_manufacturing,item)