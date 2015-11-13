# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 09:00:31 2015

@author: danaukes
"""
import popupcad
import sys

import qt.QtCore as qc
import qt.QtGui as qg

from collections import OrderedDict

class MenuSystem(object):
    shortcut_interpretation={}
    shortcut_interpretation['Ctrl+N']=qg.QKeySequence.New
    shortcut_interpretation['Ctrl+O']=qg.QKeySequence.Open
    shortcut_interpretation['Ctrl+S']=qg.QKeySequence.Save
    shortcut_interpretation['Ctrl+Shift+S']=qg.QKeySequence.SaveAs    
    
    def __init__(self,action_defs, menu_struct,shortcuts,top_menu_key):
        self.action_defs = action_defs
        self.menu_struct = menu_struct
        self.shortcuts = shortcuts.copy()
        for key,value in self.shortcuts.items():
            if value in self.shortcut_interpretation:
                self.shortcuts[key] = self.shortcut_interpretation[value]
        self.top_menu_key = top_menu_key

    def build(self,parent=None):
        icons = popupcad.guis.icons.build()
        self.actions = dict([(key,self.build_action(key,parent,self.action_defs,self.shortcuts,icons)) for key in self.action_defs])
        self.menu_dict = dict([(key,qg.QMenu(key)) for key in menu_struct])
        
        self.all_items = {}
        self.all_items.update(self.actions)
        self.all_items.update(self.menu_dict)
        self.all_items['']='separator'
        
        self.build_menu_r(self.top_menu_key,self.menu_struct,self.all_items)
        
        self.main_menu = self.menu_dict[self.top_menu_key]
        return self.main_menu
        
    @classmethod
    def build_menu_r(cls,element,structure,dictionary):
        menu = dictionary[element]
        for item in structure[element]:
            subelement = dictionary[item]
            if isinstance(subelement,qg.QMenu):
                if item in structure:
                    cls.build_menu_r(item,structure,dictionary)
                menu.addMenu(subelement)
            elif isinstance(subelement,qg.QAction):
                menu.addAction(subelement)
            elif subelement=='separator': #if isinstance(item,type([])):
                menu.addSeparator()

    @staticmethod
    def build_action(key,parent,action_defs,shortcuts,icons):
        kwargs = action_defs[key]

        if 'kwargs' in kwargs:
            action_kwargs = kwargs['kwargs']
            if 'icon' in action_kwargs:
                action_kwargs['icon']=icons[action_kwargs['icon']]
        else:
            action_kwargs = {}

        if key in shortcuts:
            action_kwargs['shortcut']=shortcuts[key]
        
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
    
        return action
    
    def set_parent(self,parent):
        for item,value in self.actions.items():
            value.setParent(parent)

            
menu_struct = {}

action_setup = OrderedDict()
action_setup['file_new']= {'text': "&New",'kwargs': {'icon': 'new','statusTip': "Create a new file"}}
action_setup['file_open']= {'text': "&Open...",'kwargs': {'icon': 'open','statusTip': "Open an existing file"}}
action_setup['file_save']= {'text': "&Save",'kwargs': {'icon': 'save','statusTip': "Save the document to disk"}}
action_setup['file_saveas']= {'text': "Save &As...",'kwargs': {'icon': 'save','statusTip': "Save the document under a new name"}}
action_setup['file_upgrade']= {'text': "Upgrade",'kwargs': {'statusTip': "Upgrade the file"}}
action_setup['file_export_stl']= {'text': 'Export to stl', 'kwargs': {'icon': 'export','statusTip': "Exports to a stl file"}}
action_setup['file_export_svg']= {'text': '&Export to SVG', 'kwargs': {'icon': 'export'}}
action_setup['file_export_dxf']= {'text': 'Export to dxf', 'kwargs': {'icon': 'export','statusTip': "Exports to a dxf file"}}
action_setup['file_export_layers_dxf']= {'text': 'Export layers to dxf', 'kwargs': {'icon': 'export','statusTip': "Exports to a dxf file"}}
action_setup['file_export_dae']= {'text': 'Export to dae', 'kwargs': {'icon': 'export','statusTip': "Exports to a dae file"}}
action_setup['file_save_joint_defs']= {'text': "Save Joint Defs"}
action_setup['file_export_laminate']= {'text': "Export Laminate"}
action_setup['file_regen_id']= {'text': "Regen ID"}
action_setup['file_render_icons']= {'text': "Render Icons"}
action_setup['file_build_documentation']= {'text': "Build Documentation"}
action_setup['file_license']= {'text': "License"}
action_setup['file_update']= {'text': "Update..."}

menu_struct['File']=['file_new',
                    'file_open',
                    'file_save',
                    'file_saveas',
                    'file_upgrade',
                    'file_export_stl',
                    'file_export_svg',
                    'file_export_dxf',
                    'file_export_layers_dxf',
                    'file_export_dae',
                    'file_save_joint_defs',
                    'file_export_laminate',
                    'file_regen_id',
                    'file_render_icons',
                    'file_build_documentation',
                    'file_license',
                    'file_update']

action_setup['project_rebuild'] = {'text': '&Rebuild','kwargs': {'icon': 'refresh'}}
action_setup['project_auto_reprocess'] = {'text': 'Auto Reprocess','is_checkable':True,'is_checked':True}
action_setup['project_layer_order'] = {'text': 'Layer Order...'}
action_setup['project_laminate_props'] = {'text': 'Laminate Properties...'}
action_setup['project_sketches'] = {'text': 'Sketches...'}
action_setup['project_subdesigns'] = {'text': 'SubDesigns...'}
action_setup['project_replace'] = {'text': 'Replace...'}
action_setup['project_insert_and_replace'] = {'text': 'Insert Laminate Op and Replace...'}
action_setup['project_hierarchy'] = {'text': 'Hierarchy'}

menu_struct['Project']=['project_rebuild',
                    'project_auto_reprocess',
                    'project_layer_order',
                    'project_laminate_props',
                    'project_sketches',
                    'project_subdesigns',
                    'project_replace',
                    'project_insert_and_replace',
                    'project_hierarchy']

action_setup['view_3d'] = {'text': '3D View','kwargs': {'icon': 'printapede'},'is_checkable':True,'is_checked':False}
action_setup['view_operations'] = {'text': 'Operations','kwargs': {'icon': 'operations'},'is_checkable':True,'is_checked':True}
action_setup['view_layers'] = {'text': 'Layers','kwargs': {'icon': 'layers'},'is_checkable':True,'is_checked':True}
action_setup['view_error_log'] = {'text': 'Error Log','is_checkable':True,'is_checked':False}
action_setup['view_zoom_fit'] = {'text': 'Zoom Fit'}
action_setup['view_screenshot'] = {'text': 'Screenshot'}
action_setup['view_3dscreenshot'] = {'text': '3D Screenshot'}

menu_struct['View']=['view_3d',
                    'view_operations',
                    'view_layers',
                    'view_error_log',
                    'view_zoom_fit',
                    'view_screenshot',
                    'view_3dscreenshot']
                    
action_setup['operations_cleanup'] = {'text': 'Cleanup','kwargs': {'icon': 'cleanup'}}
action_setup['operations_new_cleanup'] = {'text': 'New Cleanup','kwargs': {'icon': 'cleanup'}}
action_setup['operations_simplify'] = {'text': 'Simplify','kwargs': {'icon': 'simplify'}}
action_setup['operations_joint_op'] = {'text': 'JointOp'}
action_setup['operations_hole_op'] = {'text': 'HoleOp',}
action_setup['operations_freeze'] = {'text': 'Freeze'}
action_setup['operations_cross_section'] = {'text': 'Cross-Section'}
action_setup['operations_subop'] = {'text': 'SubOp'}
action_setup['operations_code_op'] = {'text': 'Code Exec'}

menu_struct['more_operations']=['operations_cleanup',
                                'operations_new_cleanup',
                                'operations_simplify',
                                'operations_joint_op',
                                'operations_hole_op',
                                'operations_freeze',
                                'operations_cross_section',
                                'operations_subop',
                                'operations_code_op']
#
action_setup['operations_transform_internal'] = {'text': 'Internal Transform','kwargs': {'icon': 'placeop'}}
action_setup['operations_transform_external'] = {'text': 'External Transform','kwargs': {'icon': 'placeop'}}
action_setup['operations_shift_flip'] = {'text': 'Shift/Flip','kwargs': {'icon': 'shiftflip'}}

menu_struct['transform_operations']=['operations_transform_internal',
                                    'operations_transform_external',
                                    'operations_shift_flip']

action_setup['operations_Sketch'] = {'text': '&SketchOp','kwargs': {'icon': 'polygons'}}
action_setup['operations_Lamiante'] = {'text': '&LaminateOp','kwargs': {'icon': 'metaop'}}
action_setup['operations_Dilate/Erode'] = {'text': '&Dilate/Erode','kwargs': {'icon': 'bufferop'}}
action_setup['operations_Layer'] = {'text': '&LayerOp','kwargs': {'icon': 'layerop'}}

menu_struct['operations']=['operations_Sketch','operations_Lamiante','operations_Dilate/Erode','transform_operations','operations_Layer','more_operations']

menu_struct['top']=['File','Project','View','operations']

shortcuts = {}
shortcuts['operations_Sketch']='Ctrl+Shift+S'
shortcuts['operations_Lamiante']='Ctrl+Shift+M'
shortcuts['operations_Dilate/Erode']='Ctrl+Shift+B'
shortcuts['operations_Layer']='Ctrl+Shift+L'
shortcuts['file_new'] = 'Ctrl+N'
shortcuts['file_open'] = 'Ctrl+O'
shortcuts['file_save'] = 'Ctrl+S'
shortcuts['file_saveas'] = 'Ctrl+Shift+S'
shortcuts['project_rebuild'] = 'Ctrl+Shift+R'
shortcuts['view_zoom_fit']='Ctrl+F'
shortcuts['operations_transform_external']='Ctrl+Shift+P'
shortcuts['view_screenshot']='Ctrl+R'

a=set(shortcuts.keys())-set(action_setup.keys())
if len(a)>0:
    raise(Exception('missing definition of'+str(a)))

m =MenuSystem(action_setup,menu_struct,shortcuts,'top')

import yaml
with open('editor_menu.yaml','w') as f:
    yaml.dump(m,f)
    

if __name__=='__main__':
    app = qg.QApplication([sys.argv[0]])
    m.build()
    sys.exit(app.exec_())