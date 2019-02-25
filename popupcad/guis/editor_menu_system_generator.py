# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

if __name__=='__main__':

    menu_struct = {}
    
    action_setup = {}
    action_setup['file_new']= {'text': "&New",'kwargs': {'icon': 'new','statusTip': "Create a new file"}}
    action_setup['file_open']= {'text': "&Open...",'kwargs': {'icon': 'open','statusTip': "Open an existing file"}}
    action_setup['file_save']= {'text': "&Save",'kwargs': {'icon': 'save','statusTip': "Save the document to disk"}}
    action_setup['file_saveas']= {'text': "Save &As...",'kwargs': {'icon': 'save','statusTip': "Save the document under a new name"}}
    action_setup['file_upgrade']= {'text': "Upgrade",'kwargs': {'statusTip': "Upgrade the file"}}
#    action_setup['file_export_stl']= {'text': 'Export to stl', 'kwargs': {'icon': 'export','statusTip': "Exports to a stl file"}}
    action_setup['file_export_svg']= {'text': '&Export to SVG', 'kwargs': {'icon': 'export'}}
    action_setup['file_export_dxf_outer']= {'text': 'Export to dxf...', 'kwargs': {'icon': 'export','statusTip': "Exports to a dxf file"}}
#    action_setup['file_export_dxf']= {'text': 'Export to dxf', 'kwargs': {'icon': 'export','statusTip': "Exports to a dxf file"}}
#    action_setup['file_export_layers_dxf']= {'text': 'Export layers to dxf', 'kwargs': {'icon': 'export','statusTip': "Exports to a dxf file"}}
    action_setup['file_export_dae']= {'text': 'Export to dae', 'kwargs': {'icon': 'export','statusTip': "Exports to a dae file"}}
    action_setup['file_save_joint_defs']= {'text': "Save Joint Defs"}
    action_setup['file_export_foldable_laminate']= {'text': "Export Foldable Robotics Laminate",'kwargs': {'icon': 'export','statusTip': "Exports to a dxf file"}}
    #action_setup['file_export_laminate']= {'text': "Export Laminate"}
    action_setup['file_regen_id']= {'text': "Regen ID"}
    action_setup['file_render_icons']= {'text': "Render Icons"}
    action_setup['file_build_documentation']= {'text': "Build Documentation"}
    action_setup['file_license']= {'text': "License"}
#    action_setup['file_update']= {'text': "Update..."}
    
    menu_struct['File']=['file_new',
                        'file_open',
                        'file_save',
                        'file_saveas',
                        'file_upgrade',
#                        'file_export_stl',
                        'file_export_svg',
                        'file_export_dxf_outer',
                        'file_export_foldable_laminate',
#                        'file_export_dxf',
#                        'file_export_layers_dxf',
#                        'file_export_dae',
                        'file_save_joint_defs',
    #                    'file_export_laminate',
                        'file_regen_id',
                        'file_render_icons',
                        'file_build_documentation',
                        'file_license',
#                        'file_update',
                        ]
    
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
    action_setup['operations_hollow'] = {'text': 'Hollow'}
    action_setup['operations_fill'] = {'text': 'Fill'}
    
    menu_struct['more_operations']=['operations_cleanup',
                                    'operations_new_cleanup',
                                    'operations_simplify',
                                    'operations_joint_op',
                                    'operations_hole_op',
                                    'operations_freeze',
                                    'operations_cross_section',
                                    'operations_subop',
                                    'operations_code_op',
                                    'operations_hollow',
                                    'operations_fill']
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
    
    triggered = {}
    triggered['file_new'] = 'newfile'
    triggered['file_open'] = 'open'
    triggered['file_save'] = 'save'
    triggered['file_saveas'] = 'saveAs'
    triggered['file_upgrade'] = 'upgrade'
#    triggered['file_export_stl'] = 'export_stl'
    triggered['file_export_svg'] = 'exportLayerSVG'
    triggered['file_export_dxf_outer'] = 'export_dxf_outer'
#    triggered['file_export_dxf'] = 'export_dxf'
#    triggered['file_export_layers_dxf'] = 'export_dxf_layers'
    triggered['file_export_dae'] = 'export_dae'
    triggered['file_save_joint_defs'] = 'save_joint_def'
    triggered['file_export_foldable_laminate'] = 'export_foldable_laminate'
#triggered['file_export_laminate'] = 'export_laminate'
    triggered['file_regen_id'] = 'regen_id'
    triggered['file_render_icons'] = 'gen_icons'
    triggered['file_build_documentation'] = 'build_documentation'
    triggered['file_license'] = 'show_license'
#    triggered['file_update'] = 'download_installer'
    
    triggered['project_rebuild'] = 'reprocessoperations_outer'
    #triggered['project_auto_reprocess'] = ''
    triggered['project_layer_order'] = 'editlayers'
    triggered['project_laminate_props'] = 'editlaminate'
    triggered['project_sketches'] = 'sketchlist'
    triggered['project_subdesigns'] = 'subdesigns'
    triggered['project_replace'] = 'replace'
    triggered['project_insert_and_replace'] = 'insert_and_replace'
    triggered['project_hierarchy'] = 'operation_network'
    
    triggered['view_3d'] = 'show_hide_view_3d'
    triggered['view_operations'] = 'show_hide_operationdock'
    triggered['view_layers'] = 'show_hide_layerlistwidgetdock'
    triggered['view_error_log'] = 'show_hide_error_log'
    triggered['view_zoom_fit'] = 'zoomToFit'
    triggered['view_screenshot'] = 'screenShot'
    triggered['view_3dscreenshot'] = 'screenshot_3d'
    
    triggered['operations_cleanup'] = 'new_cleanup2'
    triggered['operations_new_cleanup'] = 'new_cleanup3'
    triggered['operations_simplify'] = 'new_simplify2'
    triggered['operations_joint_op'] = 'new_jointop3'
    triggered['operations_hole_op'] = 'new_holeop'
    triggered['operations_freeze'] = 'new_freezeop'
    triggered['operations_cross_section'] = 'new_cross_section'
    triggered['operations_subop'] = 'new_subop'
    triggered['operations_code_op'] = 'new_codeop'
    triggered['operations_hollow'] = 'new_hollow'
    triggered['operations_fill'] = 'new_fill'
    
    triggered['operations_transform_internal'] = 'new_transform_internal'
    triggered['operations_transform_external'] = 'new_transform_external'
    triggered['operations_shift_flip'] = 'new_shiftflip'
    triggered['operations_Sketch'] = 'new_sketch_op'
    triggered['operations_Lamiante'] = 'new_laminate_op'
    triggered['operations_Dilate/Erode'] = 'new_buffer_op'
    triggered['operations_Layer'] = 'new_layer_op'
    
    for key,value in action_setup.items():
        if 'kwargs' in value:
            value.update(value['kwargs'])
            del value['kwargs']
    
    for key,value in triggered.items():
        action_setup[key]['triggered'] = value
    
    toolbar_definitions = {}
    toolbar_definitions['more_operations'] = {'text':'More...'}
    toolbar_definitions['transform_operations'] = {'text':'Transform','icon':'placeop'}
    #toolbar_struct = menu_struct.copy()
    toolbar_struct = {}
    toolbar_struct['operations'] = menu_struct['operations']
    toolbar_struct['transform_operations'] = menu_struct['transform_operations']
    toolbar_struct['more_operations'] = menu_struct['more_operations']
    toolbar_struct['top'] = ['operations']
    
    from popupcad.guis.actions import MenuSystem
    m =MenuSystem(action_setup,toolbar_definitions,menu_struct,toolbar_struct,shortcuts,'top')
    
    import yaml
    import popupcad
    
    with open(popupcad.supportfiledir+'/editor_menu.yaml','w') as f:
        yaml.dump(m,f)