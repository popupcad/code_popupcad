# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
from . import generatealignmentlayup
from . import tilepart

#import external modules
import numpy
import shapely

def build_menu_system(program):
    def new_alignment_layup():
        program.editor.newoperation(generatealignmentlayup.AlignmentLayup)
    def new_tile_part():
        program.editor.newoperation(tilepart.TilePart)

    action_definitions = {}
    action_definitions['alignment_layup']={'text': 'Alignment layup','icon': 'identifybodies'}
    action_definitions['tile_part']={'text': 'Tile parts','icon': 'identifybodies'}

    toolbar_definitions={}
    toolbar_definitions['Microrobotics']={'text': 'Microrobotics','icon': 'dotdotdot'}

    menu_structure = {}
    menu_structure['top'] = ['Microrobotics']
    menu_structure['Microrobotics'] = ['alignment_layup', 'tile_part']

    toolbar_structure = menu_structure.copy()
    shortcuts = {}

    triggered = {}
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
