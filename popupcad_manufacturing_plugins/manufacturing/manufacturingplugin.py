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
#from .toolclearance2 import ToolClearance2
from .cutop2 import CutOperation2
from .identifybodies import IdentifyBodies
from .identifyrigidbodies import IdentifyRigidBodies
from .removability import Removability
from .scrapoperation import ScrapOperation

class ManufacturingPlugin(Plugin):
    def __init__(self, editor, design):

        scrap = []
        scrap.append({'text':'Sheet','kwargs':{'icon':Icon('outersheet'),'triggered':lambda:editor.newoperation(OuterSheet2)}})
        scrap.append({'text':'&Web','kwargs':{'icon':Icon('outerweb'),'triggered':lambda:editor.newoperation(AutoWeb3)}})
        scrap.append({'text':'Scrap(Beta)','kwargs':{'triggered':lambda:editor.newoperation(ScrapOperation)}})

        supportactions= []
        supportactions.append({'text':'S&upport','kwargs':{'icon':Icon('autosupport'),'triggered':lambda:editor.newoperation(SupportCandidate3)}})
        supportactions.append({'text':'Custom Support','kwargs':{'triggered':lambda:editor.newoperation(CustomSupport3)}})
        
        other = []
        other.append({'text':'Keep-outs','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:editor.newoperation(KeepOut2)}})
        other.append({'text':'Cuts','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:editor.newoperation(CutOperation2)}})
        other.append({'text':'Identify Rigid Bodies','kwargs':{'triggered':lambda:editor.newoperation(IdentifyRigidBodies)}})

        manufacturingactions = []
        manufacturingactions.append({'text':'Scrap','submenu':scrap})
        manufacturingactions.append({'text':'Supports','submenu':supportactions,'kwargs':{'icon':Icon('outerweb')}})
#        manufacturingactions.append({'text':'Tool Clearance','kwargs':{'triggered':lambda:editor.newoperation(ToolClearance2)}})
        manufacturingactions.append({'text':'Removability','kwargs':{'triggered':lambda:editor.newoperation(Removability)}})
        manufacturingactions.append({'text':'Identify Bodies','kwargs':{'triggered':lambda:editor.newoperation(IdentifyBodies)}})
        manufacturingactions.append({'text':'Misc','submenu':other})


        editor.toolbar_manufacturing,editor.menu_manufacturing = editor.addToolbarMenu(manufacturingactions,name='Manufacturing')
#        self.menu_manufacturing = self.buildMenu(self.manufacturingactions,name='Manufacturing')

#        for item in manufacturingactions:
#            editor.addMenuItem(editor.menu_manufacturing,item.copy())
#            editor.addToolbarItem(editor.toolbar_manufacturing,item.copy())