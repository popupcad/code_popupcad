# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 06:36:35 2015

@author: danaukes
"""
action_definitions = {}
action_definitions['file_new']={'text': "&New",'triggered': 'newfile','shortcut': 'Ctrl+N','icon': 'new'}
action_definitions['file_open']={'text': "&Open...",'triggered': 'open','shortcut': 'Ctrl+O','icon': 'open'}
action_definitions['file_import']={'text': "Import...",'triggered': 'solidworksimport','icon': 'import'}
action_definitions['file_save']={'text': "&Save",'triggered': 'save','shortcut': 'Ctrl+S','icon': 'save'}
action_definitions['file_saveas']={'text': "Save &As...",'triggered': 'saveAs','shortcut': 'Ctrl+Shift+S','icon': 'save'}
action_definitions['file_regenid']={'text': "Regen ID", 'triggered': 'regen_id'}
action_definitions['edit_undo']={'text': 'Undo','triggered': 'undo','shortcut': 'Ctrl+Z','icon': 'undo'}
action_definitions['edit_redo']={'text': 'Redo','triggered': 'redo','shortcut': 'Ctrl+Y','icon': 'redo'}
action_definitions['edit_cut']={'text': 'Cut','triggered': 'cut_to_clipboard','shortcut': 'Ctrl+X'}
action_definitions['edit_copy']={'text': 'Copy','triggered': 'copy_to_clipboard','shortcut': 'Ctrl+C' }
action_definitions['edit_paste']={'text': 'Paste','triggered': 'paste_from_clipboard','shortcut': 'Ctrl+V'}
action_definitions['edit_array']={'text': 'Array', 'triggered': 'array'}
action_definitions['view_operations']={'text': 'Operations', 'triggered': 'show_hide_op_tree','is_checkable':True,'is_checked':True}
action_definitions['view_constraints']={'text': 'Constraints','triggered': 'show_hide_constraints','is_checkable':True,'is_checked':True}
action_definitions['view_properties']={'text': 'Properties', 'triggered': 'show_hide_properties','is_checkable':True,'is_checked':True}
action_definitions['view_rubberband']={'text': 'select','triggered': 'rubberband','shortcut': 'Ctrl+Shift+S','icon': 'pointer'}
action_definitions['view_scrollhand']={'text': 'pan','triggered': 'scrollhand','shortcut': 'Ctrl+Shift+P','icon': 'hand'}
action_definitions['view_zoom_to_fit']={'text': 'Zoom Fit','triggered': 'zoomToFit','shortcut': 'Ctrl+F'}
action_definitions['view_screenshot']={'text': 'Screenshot','triggered': 'screenShot','shortcut': 'Ctrl+R'}
action_definitions['drawing_add_point']={'text': 'point','triggered': 'adddrawingpoint','icon': 'points'}
action_definitions['drawing_add_line']={'text': 'line', 'triggered': 'add_line', 'icon': 'line'}
action_definitions['drawing_add_path']={'text': 'polyline', 'triggered': 'add_path', 'icon': 'polyline'}
action_definitions['drawing_add_rect']={'text': 'rect', 'triggered': 'add_rect', 'icon': 'rectangle'}
action_definitions['drawing_add_circle']={'text': 'circle', 'triggered': 'add_circle', 'icon': 'circle'}
action_definitions['drawing_add_poly']={'text': 'poly', 'triggered': 'add_poly', 'icon': 'polygon'}
action_definitions['drawing_add_text']={'text': 'text', 'triggered': 'add_text', 'icon': 'text'}
action_definitions['tools_convex_hull']={'text': 'convex hull','triggered': 'convex_hull','icon': 'convex_hull'}
action_definitions['tools_triangulate']={'text': 'triangulate','triggered': 'triangulate','icon': 'triangulate'}
action_definitions['tools_get_joints']={'text': 'shared edges','triggered': 'getjoints','icon': 'getjoints2'}
action_definitions['tools_flip_dir']={'text': 'flip direction', 'triggered': 'flipdirection'}
action_definitions['tools_hollow']={'text': 'hollow', 'triggered': 'hollow'}
action_definitions['tools_fill']={'text': 'fill', 'triggered': 'fill'}
action_definitions['tools_set_construction_on']={'text': 'Construction', 'triggered': 'set_construction_on'}
action_definitions['tools_set_construction_off']={'text': 'Not Construction', 'triggered': 'set_construction_off'}
action_definitions['constraints_coincident']={'text': 'Coincident','triggered': 'add_constraint_coincident','icon': 'coincident'}
action_definitions['constraints_distance']={'text': 'Distance','triggered': 'add_constraint_distance','icon': 'distance'}
action_definitions['constraints_distance_x']={'text': 'DistanceX','triggered': 'add_constraint_x_distance','icon': 'distancex'}
action_definitions['constraints_distance_y']={'text': 'DistanceY','triggered': 'add_constraint_y_distance','icon': 'distancey'}
action_definitions['constraints_fixed']={'text': 'Fixed', 'triggered': 'add_constraint_fixed'}
action_definitions['constraints_angle']={'text': 'Angle','triggered': 'add_constraint_angle','icon': 'angle'}
action_definitions['constraints_parallel']={'text': 'Parallel','triggered': 'add_constraint_parallel','icon': 'parallel'}
action_definitions['constraints_perpendicular']={'text': 'Perpendicular','triggered': 'add_constraint_perpendicular','icon': 'perpendicular'}
action_definitions['constraints_equal']={'text': 'Equal','triggered': 'add_constraint_equal','icon': 'equal'}
action_definitions['constraints_horizontal']={'text': 'Horizontal','triggered': 'add_constraint_horizontal','icon': 'horizontal'}
action_definitions['constraints_vertical']={'text': 'Vertical','triggered': 'add_constraint_vertical','icon': 'vertical'}
action_definitions['constraints_point_line_distance']={'text': 'PointLine','triggered': 'add_constraint_point_line_distance','icon': 'pointline'}
action_definitions['constraints_line_midpoint']={'text': 'Midpoint', 'triggered': 'add_constraint_line_midpoint'}
action_definitions['constraints_refresh']={'text': 'Update', 'triggered': 'refreshconstraints', 'icon': 'refresh'}
action_definitions['constraints_cleanup']={'text': 'Cleanup', 'triggered': 'cleanupconstraints', 'icon': 'broom'}
action_definitions['constraints_show']={'text': 'Constraints On','triggered': 'showvertices','icon': 'showconstraints','is_checkable':True,'is_checked':False}

menu_struct = {}
menu_struct['top']=['file','edit','view','drawing','tools','constraints']
menu_struct['file']=['file_new','file_open','file_import','file_save','file_saveas','file_regenid']
menu_struct['edit']=['edit_undo','edit_redo','edit_cut','edit_copy','edit_paste','edit_array']
menu_struct['view']=['view_operations','view_constraints','view_properties','view_rubberband','view_scrollhand','view_zoom_to_fit','view_screenshot']
menu_struct['drawing']=['drawing_add_point','drawing_add_line','drawing_add_path','drawing_add_rect','drawing_add_rect','drawing_add_circle','drawing_add_poly','drawing_add_text']
menu_struct['tools']=['tools_convex_hull','tools_triangulate','tools_get_joints','tools_flip_dir','tools_hollow','tools_fill','tools_set_construction_on','tools_set_construction_off']
menu_struct['constraints']=['constraints_show','distance_constraints','line_constraints','misc_constraints','constraints_refresh','constraints_cleanup']
menu_struct['distance_constraints']=['constraints_coincident','constraints_distance','constraints_distance_y','constraints_fixed']
menu_struct['line_constraints']=['constraints_angle','constraints_parallel','constraints_perpendicular','constraints_equal','constraints_horizontal','constraints_vertical']
menu_struct['misc_constraints']=['point_constraints','constraints_point_line_distance','constraints_line_midpoint']

toolbar_defs = {}
toolbar_defs['distance_constraints'] = {'text':'Distance','icon':'distance'}
toolbar_defs['line_constraints'] = {'text':'Line','icon':'parallel'}
toolbar_defs['misc_constraints'] = {'text':'Misc','icon':'dotdotdot'}

toolbar_struct = {}
toolbar_struct['top']=['drawing','tools','constraints']
toolbar_struct['drawing']=['drawing_add_point','drawing_add_line','drawing_add_path','drawing_add_rect','drawing_add_rect','drawing_add_circle','drawing_add_poly','drawing_add_text']
toolbar_struct['tools']=['tools_convex_hull','tools_triangulate','tools_get_joints','tools_flip_dir','tools_hollow','tools_fill','tools_set_construction_on','tools_set_construction_off']
toolbar_struct['constraints']=['constraints_show','distance_constraints','line_constraints','misc_constraints','constraints_refresh','constraints_cleanup']
toolbar_struct['distance_constraints']=['constraints_coincident','constraints_distance','constraints_distance_y','constraints_fixed']
toolbar_struct['line_constraints']=['constraints_angle','constraints_parallel','constraints_perpendicular','constraints_equal','constraints_horizontal','constraints_vertical']
toolbar_struct['misc_constraints']=['constraints_point_line_distance','constraints_line_midpoint']

shortcuts = {}
for key,value in action_definitions.items():
    if 'shortcut' in value:
        shortcuts[key]=value['shortcut']
        
from popupcad.guis.actions import MenuSystem
m =MenuSystem(action_definitions,toolbar_defs,menu_struct,toolbar_struct,shortcuts,'top')

import yaml
import popupcad

with open(popupcad.supportfiledir+'/sketcher_menu.yaml','w') as f:
    yaml.dump(m,f)