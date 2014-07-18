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
from .autoweb3 import AutoWeb3
from .outersheet2 import OuterSheet2
from .supportcandidate3 import SupportCandidate3
from .customsupport3 import CustomSupport3
from .keepout2 import KeepOut2
from .toolclearance2 import ToolClearance2
from .cutop2 import CutOperation2
from .identifybodies import IdentifyBodies
from .identifyrigidbodies import IdentifyRigidBodies
from .removability import Removability

class ManufacturingPlugin(Plugin):
    def __init__(self, editor, design):
        supportactions= []
        supportactions.append({'text':'Sheet','kwargs':{'icon':Icon('outersheet'),'triggered':lambda:editor.newoperation(OuterSheet2)}})
        supportactions.append({'text':'&Web','kwargs':{'icon':Icon('outerweb'),'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_U,'triggered':lambda:editor.newoperation(AutoWeb3)}})
        supportactions.append({'text':'S&upport','kwargs':{'icon':Icon('autosupport'),'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_W,'triggered':lambda:editor.newoperation(SupportCandidate3)}})
        supportactions.append({'text':'Custom Support','kwargs':{'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_W,'triggered':lambda:editor.newoperation(CustomSupport3)}})
        
        manufacturingactions = []
        manufacturingactions.append({'text':'Keep-outs','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:editor.newoperation(KeepOut2)}})
        manufacturingactions.append({'text':'Supports','submenu':supportactions,'kwargs':{'icon':Icon('outerweb')}})
        manufacturingactions.append({'text':'Tool Clearance','kwargs':{'triggered':lambda:editor.newoperation(ToolClearance2)}})
        manufacturingactions.append({'text':'Cuts','kwargs':{'icon':Icon('firstpass'),'shortcut': qc.Qt.CTRL+qc.Qt.SHIFT+qc.Qt.Key_1,'triggered':lambda:editor.newoperation(CutOperation2)}})
        manufacturingactions.append({'text':'Removability','kwargs':{'triggered':lambda:editor.newoperation(Removability)}})
        manufacturingactions.append({'text':'Identify Bodies','kwargs':{'triggered':lambda:editor.newoperation(IdentifyBodies)}})
        manufacturingactions.append({'text':'Identify Rigid Bodies','kwargs':{'triggered':lambda:editor.newoperation(IdentifyRigidBodies)}})

        for item in manufacturingactions:
            editor.addMenuItem(editor.menu_manufacturing,item.copy())
            editor.addToolbarItem(editor.toolbar_manufacturing,item.copy())