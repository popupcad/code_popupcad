# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.supportfiles import Icon
from popupcad.filetypes.plugin import Plugin
from . import autoweb4
from . import outersheet3
from . import supportcandidate4
from . import customsupport3
from . import keepout3
from . import cutop2
from . import identifybodies2
from . import identifyrigidbodies2
from . import removability2
from . import scrapoperation

class ManufacturingPlugin(Plugin):
    def __init__(self, editor, design):

        scrap = []
        scrap.append({'text':'Sheet','kwargs':{'icon':Icon('outersheet'),'triggered':lambda:editor.newoperation(outersheet3.OuterSheet3)}})
        scrap.append({'text':'&Web','kwargs':{'icon':Icon('outerweb'),'triggered':lambda:editor.newoperation(autoweb4.AutoWeb4)}})
        scrap.append({'text':'Scrap(Beta)','kwargs':{'icon':Icon('scrap'),'triggered':lambda:editor.newoperation(scrapoperation.ScrapOperation)}})

        supportactions= []
        supportactions.append({'text':'S&upport','kwargs':{'icon':Icon('autosupport'),'triggered':lambda:editor.newoperation(supportcandidate4.SupportCandidate4)}})
        supportactions.append({'text':'Custom Support','kwargs':{'icon':Icon('customsupport'),'triggered':lambda:editor.newoperation(customsupport3.CustomSupport3)}})
        
        other = []
        other.append({'text':'Keep-outs','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:editor.newoperation(keepout3.KeepOut3)}})
        other.append({'text':'Cuts','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:editor.newoperation(cutop2.CutOperation2)}})
        other.append({'text':'Identify Rigid Bodies','kwargs':{'triggered':lambda:editor.newoperation(identifyrigidbodies2.IdentifyRigidBodies2)}})

        manufacturingactions = []
        manufacturingactions.append({'text':'Scrap','submenu':scrap,'kwargs':{'icon':Icon('scrap')}})
        manufacturingactions.append({'text':'Supports','submenu':supportactions,'kwargs':{'icon':Icon('outerweb')}})
#        manufacturingactions.append({'text':'Tool Clearance','kwargs':{'triggered':lambda:editor.newoperation(ToolClearance2)}})
        manufacturingactions.append({'text':'Removability','kwargs':{'icon':Icon('removability'),'triggered':lambda:editor.newoperation(removability2.Removability2)}})
        manufacturingactions.append({'text':'Identify Bodies','kwargs':{'icon':Icon('identifybodies'),'triggered':lambda:editor.newoperation(identifybodies2.IdentifyBodies2)}})
        manufacturingactions.append({'text':'Misc','submenu':other,'kwargs':{'icon':Icon('dotdotdot')}})


        editor.toolbar_manufacturing,editor.menu_manufacturing = editor.addToolbarMenu(manufacturingactions,name='Manufacturing')
