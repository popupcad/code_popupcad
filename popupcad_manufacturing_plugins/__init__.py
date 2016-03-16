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

def build_menu_system(program):
    def new_sheet():
        program.editor.newoperation(manufacturing.outersheet3.OuterSheet3)
    def new_web():
        program.editor.newoperation(manufacturing.autoweb4.AutoWeb4)
    def new_scrap():
        program.editor.newoperation(manufacturing.scrapoperation2.ScrapOperation2)
    def new_support():
        program.editor.newoperation(manufacturing.supportcandidate4.SupportCandidate4)
    def new_custom_support():
        program.editor.newoperation(manufacturing.customsupport4.CustomSupport4)
    def new_keepout():
        program.editor.newoperation(manufacturing.keepout3.KeepOut3)
    def new_removability():
        program.editor.newoperation(manufacturing.removability2.Removability2)
    def new_identify_bodies():
        program.editor.newoperation(manufacturing.identifybodies2.IdentifyBodies2)
    def new_identify_rigid_bodies():
        program.editor.newoperation(manufacturing.identifyrigidbodies2.IdentifyRigidBodies2)
    def new_alignment_layup():
        program.editor.newoperation(manufacturing.generatealignmentlayup.AlignmentLayup)
    def new_tile_part():
        program.editor.newoperation(manufacturing.tilepart.TilePart)

    action_definitions = {}

    action_definitions['sheet']={'text': 'Sheet','icon': 'outersheet'}
    action_definitions['web']={'text': '&Web','icon': 'outerweb' }
    action_definitions['scrap']={'text': 'Scrap','icon': 'scrap'}

    action_definitions['support_action']={'text': 'S&upport','icon': 'autosupport'}
    action_definitions['custom_support']={'text': 'Custom Support','icon': 'customsupport'}

    action_definitions['keepout']={'text': 'Keep-out','icon': 'firstpass'}
    action_definitions['identify_rigid_bodies']={'text': 'Identify Rigid Bodies'}

    action_definitions['removability']={'text': 'Removability','icon': 'removability'}
    action_definitions['identify_bodies']={'text': 'Identify Bodies','icon': 'identifybodies'}

    action_definitions['alignment_layup']={'text': 'Alignment layup','icon': 'identifybodies'}
    action_definitions['tile_part']={'text': 'Tile parts','icon': 'identifybodies'}

    toolbar_definitions={}
    toolbar_definitions['Scrap']={'text': 'Scrap', 'icon': 'scrap'}
    toolbar_definitions['Support']={'text': 'Support','icon': 'outerweb'}
    toolbar_definitions['Misc']={'text': 'Misc...','icon': 'dotdotdot'}
    toolbar_definitions['Microrobotics']={'text': 'Microrobotics','icon': 'dotdotdot'}

    menu_structure = {}
    menu_structure['manufacturing'] = ['Scrap','Support','identify_bodies','Misc','Microrobotics']
    menu_structure['top'] = ['manufacturing']
    menu_structure['Scrap'] = ['sheet','web','scrap']
    menu_structure['Support'] = ['support_action','custom_support']
    menu_structure['Misc'] = ['keepout','identify_rigid_bodies','removability']
    menu_structure['Microrobotics'] = ['alignment_layup', 'tile_part']

    toolbar_structure = menu_structure.copy()
    shortcuts = {}

    triggered = {}
    triggered['sheet'] = new_sheet
    triggered['web'] = new_web
    triggered['scrap'] = new_scrap
    triggered['support_action'] = new_support
    triggered['custom_support'] = new_custom_support
    triggered['keepout'] = new_keepout
    triggered['identify_rigid_bodies'] = new_identify_rigid_bodies
    triggered['removability'] = new_removability
    triggered['identify_bodies'] = new_identify_bodies
    triggered['alignment_layup'] = new_alignment_layup
    triggered['tile_part'] = new_tile_part

    for key,value in triggered.items():
        action_definitions[key]['triggered'] = value    

    from popupcad.guis.actions import MenuSystem
    menu_system = MenuSystem(action_definitions,toolbar_definitions,menu_structure,toolbar_structure,shortcuts,'top')
    return menu_system
    
def initialize(program):
    menu_system = build_menu_system(program)
    program.editor.load_menu_system(menu_system)
