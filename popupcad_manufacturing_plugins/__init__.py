# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from . import manufacturing

#import external modules

import numpy
import shapely

def initialize(program):

    def new_sheet():
        program.editor.newoperation(manufacturing.outersheet3.OuterSheet3)
    def new_web():
        lambda: program.editor.newoperation(manufacturing.autoweb4.AutoWeb4)
    def new_scrap():
        lambda: program.editor.newoperation(manufacturing.scrapoperation2.ScrapOperation2)
    def new_support():
        lambda: program.editor.newoperation(manufacturing.supportcandidate4.SupportCandidate4)
    def new_custom_support():
        lambda: program.editor.newoperation(manufacturing.customsupport4.CustomSupport4)
    def new_keepout():
        lambda: program.editor.newoperation(manufacturing.keepout3.KeepOut3)
    def new_removability():
        lambda: program.editor.newoperation(manufacturing.removability2.Removability2)
    def new_identify_bodies():
        lambda: program.editor.newoperation(manufacturing.identifybodies2.IdentifyBodies2)
    def new_identify_rigid_bodies():
        lambda: program.editor.newoperation(manufacturing.identifyrigidbodies2.IdentifyRigidBodies2)

    action_definitions = {}
    
    action_definitions['sheet']={'text': 'Sheet','icon': 'outersheet'}
    action_definitions['web']={'text': '&Web','icon': 'outerweb' }
    action_definitions['scrap']={'text': 'Scrap','icon': 'scrap'}

    action_definitions['support']={'text': 'S&upport','icon': 'autosupport'}
    action_definitions['custom_support']={'text': 'Custom Support','icon': 'customsupport'}

    action_definitions['keepout']={'text': 'Keep-out','icon': 'firstpass'}
    action_definitions['identify_rigid_bodies']={'text': 'Identify Rigid Bodies'}

    action_definitions['removability']={'text': 'Removability','icon': 'removability'}
    action_definitions['identify_bodies']={'text': 'Identify Bodies','icon': 'identifybodies'}

    toolbar_definitions={}
    toolbar_definitions['Scrap']={'text': 'Scrap', 'icon': 'scrap'}
    toolbar_definitions['Supports']={'text': 'Supports','icon': 'outerweb'}
    toolbar_definitions['Misc']={'text': 'Misc...','icon': 'dotdotdot'}

    menu_structure = {}
    menu_structure['manufacturing'] = ['Scrap','Supports','identify_bodies','Misc']
    menu_structure['top'] = ['manufacturing']
    menu_structure['Scrap'] = ['sheet','web','scrap']
    menu_structure['Supports'] = ['support','custom_support']
    menu_structure['Misc'] = ['keepout','identify_rigid_bodies','removability']
    
    toolbar_structure = menu_structure.copy()
    shortcuts = {}
    
    triggered = {}
    triggered['sheet'] = new_sheet
    triggered['web'] = new_web
    triggered['scrap'] = new_scrap
    triggered['support'] = new_support
    triggered['custom_support'] = new_custom_support
    triggered['keepout'] = new_keepout
    triggered['identify_rigid_bodies'] = new_identify_rigid_bodies
    triggered['removability'] = new_removability
    triggered['identify_bodies'] = new_identify_bodies

    for key,value in triggered.items():
        action_definitions[key]['triggered'] = value

    from popupcad.guis.actions import MenuSystem
    menu_system = MenuSystem(action_definitions,toolbar_definitions,menu_structure,toolbar_structure,shortcuts,'top')
    program.editor.load_menu_system(menu_system)
#    import yaml
#    with open('manufacturing_menu.yaml','w') as f:
#        yaml.dump(menu_system,f)

    #    program.editor.toolbar_manufacturing, program.editor.menu_manufacturing = program.editor.addToolbarMenu(manufacturingactions, name='Manufacturing')
