# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 22:17:43 2015

@author: danaukes
"""

import PySide.QtGui as qg
import PySide.QtCore as qc

class Action(qg.QAction):
    pass

def build(editor):
    file_new = Action('New',editor)
    file_open = Action('Open...',editor)
    file_save = Action('Save',editor)
    file_save_as = Action('Save As...',editor)
    file_upgrade = Action('Upgrade',editor)
    file_export_svg = Action('Export to .svg...',editor)
    file_export_dxf = Action('Export to .dxf...',editor)
    file_export_dae = Action('Export to .dae...',editor)
    file_export_stl = Action('Export to .stl...',editor)
    
    file_actions = []
    file_actions.append(file_new)
    file_actions.append(file_open)
    file_actions.append(file_save)
    file_actions.append(file_save_as)
    file_actions.append(file_upgrade)
    file_actions.append(file_export_svg)
    file_actions.append(file_export_dxf)
    file_actions.append(file_export_dae)
    file_actions.append(file_export_stl)
    
    menu_file = qg.QMenu('File')
    [menu_file.addAction(item) for item in file_actions]
    return menu_file



#self.fileactions = []
#self.fileactions.append({'text': "&New",'kwargs': {'icon': icons['new'],'shortcut': qg.QKeySequence.New,'statusTip': "Create a new file",'triggered': self.newfile}})
#self.fileactions.append({'text': "&Open...",'kwargs': {'icon': icons['open'],'shortcut': qg.QKeySequence.Open,'statusTip': "Open an existing file",'triggered': self.open}})
#self.fileactions.append({'text': "&Save",'kwargs': {'icon': icons['save'],'shortcut': qg.QKeySequence.Save,'statusTip': "Save the document to disk",'triggered': self.save}})
#self.fileactions.append({'text': "Save &As...",'kwargs': {'icon': icons['save'],'shortcut': qg.QKeySequence.SaveAs,'statusTip': "Save the document under a new name",'triggered': self.saveAs}})
#self.fileactions.append({'text': "Upgrade",'kwargs': {'statusTip': "Upgrade the file",'triggered': self.upgrade}})
#self.fileactions.append({'text': 'Export to stl', 'kwargs': {'icon': icons['export'],'statusTip': "Exports to a stl file",'triggered': self.export_stl}})
#self.fileactions.append({'text': '&Export to SVG', 'kwargs': {'icon': icons['export'], 'triggered': self.exportLayerSVG}})
#self.fileactions.append({'text': 'Export to dxf', 'kwargs': {'icon': icons['export'],'statusTip': "Exports to a dxf file",'triggered': self.export_dxf}})
#self.fileactions.append({'text': 'Export to dae', 'kwargs': {'icon': icons['export'],'statusTip': "Exports to a dae file",'triggered': self.export_dae}})
#
#self.fileactions.append({'text': "Save Joint Defs", 'kwargs': {'triggered': self.save_joint_def}})
#self.fileactions.append({'text': "Export Laminate", 'kwargs': {'triggered': self.export_laminate}})
#self.fileactions.append({'text': "Regen ID", 'kwargs': {'triggered': self.regen_id, }})
#self.fileactions.append({'text': "Preferences...", 'kwargs': {'triggered': self.preferences}})
#self.fileactions.append({'text': "Render Icons", 'kwargs': {'triggered': self.gen_icons}})
#self.fileactions.append({'text': "Build Documentation", 'kwargs': {'triggered': self.build_documentation}})
#self.fileactions.append({'text': "License", 'kwargs': {'triggered': self.show_license}})
#self.fileactions.append({'text': "Update...",'kwargs': {'triggered': self.download_installer}})
#
#self.projectactions = []
#self.projectactions.append({'text': '&Rebuild','kwargs': {'icon': icons['refresh'],'shortcut': 'Ctrl+Shift+R','triggered': self.reprocessoperations_outer}})
#
#def dummy(action):
#    action.setCheckable(True)
#    action.setChecked(True)
#    self.act_autoreprocesstoggle = action
#self.projectactions.append({'text': 'Auto Reprocess', 'kwargs': {}, 'prepmethod': dummy})
#
#self.projectactions.append(None)
#self.projectactions.append({'text': 'Layer Order...', 'kwargs': {'triggered': self.editlayers}})
#self.projectactions.append({'text': 'Laminate Properties...', 'kwargs': {'triggered': self.editlaminate}})
#self.projectactions.append({'text': 'Sketches...', 'kwargs': {'triggered': self.sketchlist}})
#self.projectactions.append({'text': 'SubDesigns...', 'kwargs': {'triggered': self.subdesigns}})
#self.projectactions.append({'text': 'Replace...', 'kwargs': {'triggered': self.replace}})
#self.projectactions.append({'text': 'Insert Laminate Op and Replace...', 'kwargs': {'triggered': self.insert_and_replace}})
#
#self.viewactions = []
#
#def dummy(action):
#    action.setCheckable(True)
#    action.setChecked(False)
#    self.act_view_3d = action
#self.viewactions.append({'prepmethod': dummy,'text': '3D View','kwargs': {'icon': icons['printapede'],'triggered': lambda: self.showhide2(self.view_3d_dock,self.act_view_3d)}})
#
#def dummy(action):
#    action.setCheckable(True)
#    action.setChecked(True)
#    self.act_view_ops = action
#self.viewactions.append({'prepmethod': dummy,'text': 'Operations','kwargs': {'icon': icons['operations'],'triggered': lambda: self.showhide2(self.operationdock,self.act_view_ops)}})
#
#def dummy(action):
#    action.setCheckable(True)
#    action.setChecked(True)
#    self.act_view_layers = action
#self.viewactions.append({'prepmethod': dummy,'text': 'Layers','kwargs': {'icon': icons['layers'],'triggered': lambda: self.showhide2(self.layerlistwidgetdock,self.act_view_layers)}})
#
#def dummy(action):
#    action.setCheckable(True)
#    action.setChecked(False)
#    self.act_view_errors = action
#self.viewactions.append({'prepmethod': dummy, 'text': 'Error Log', 'kwargs': {'triggered': lambda: self.showhide2(self.error_log, self.act_view_errors)}})
#
#self.viewactions.append({'text': 'Zoom Fit','kwargs': {'triggered': self.view_2d.zoomToFit,'shortcut': 'Ctrl+F'}})
#self.viewactions.append({'text': 'Screenshot','kwargs': {'triggered': self.scene.screenShot,'shortcut': 'Ctrl+R'}})
#self.viewactions.append({'text': '3D Screenshot', 'kwargs': {'triggered': self.screenshot_3d}})
#
#self.tools1 = []
#self.tools1.append({'text': 'Cleanup','kwargs': {'icon': icons['cleanup'],'triggered': lambda: self.newoperation(popupcad.manufacturing.cleanup2.Cleanup2)}})
#self.tools1.append({'text': 'New Cleanup','kwargs': {'icon': icons['cleanup'],'triggered': lambda: self.newoperation(popupcad.manufacturing.cleanup3.Cleanup3)}})
#self.tools1.append({'text': 'Simplify','kwargs': {'icon': icons['simplify'],'triggered': lambda: self.newoperation(popupcad.manufacturing.simplify2.Simplify2)}})
#self.tools1.append({'text': 'JointOp','kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.joint_operation3.JointOperation3)}})
#self.tools1.append({'text': 'HoleOp','kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.hole_operation.HoleOperation)}})
#self.tools1.append({'text': 'Freeze', 'kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.freeze.Freeze)}})
#self.tools1.append({'text': 'Cross-Section','kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.cross_section.CrossSection)}})
#self.tools1.append({'text': 'SubOp','kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.sub_operation2.SubOperation2)}})
#self.tools1.append({'text': 'Transform','kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.transform.TransformOperation)}})
##        self.tools1.append({'text': 'Code Exec','kwargs': {'triggered': lambda: self.newoperation(popupcad.manufacturing.code_exec_op.CodeExecOperation)}})
#
#self.operationactions = []
#self.operationactions.append({'text': '&SketchOp','kwargs': {'icon': icons['polygons'],'shortcut': 'Ctrl+Shift+S','triggered': lambda: self.newoperation(popupcad.manufacturing.simplesketchoperation.SimpleSketchOp)}})
#self.operationactions.append({'text': '&LaminateOp','kwargs': {'icon': icons['metaop'],'shortcut': 'Ctrl+Shift+M','triggered': lambda: self.newoperation(popupcad.manufacturing.laminateoperation2.LaminateOperation2)}})
#self.operationactions.append({'text': '&Dilate/Erode','kwargs': {'icon': icons['bufferop'],'shortcut': 'Ctrl+Shift+B','triggered': lambda: self.newoperation(popupcad.manufacturing.bufferop3.BufferOperation3)}})
#self.operationactions.append({'text': '&PlaceOp','kwargs': {'icon': icons['placeop'],'shortcut': 'Ctrl+Shift+P','triggered': lambda: self.newoperation(popupcad.manufacturing.placeop8.PlaceOperation8)}})
#self.operationactions.append({'text': 'L&ocateOp','kwargs': {'icon': icons['locate'],'shortcut': 'Ctrl+Shift+O','triggered': lambda: self.newoperation(popupcad.manufacturing.locateoperation3.LocateOperation3)}})
#self.operationactions.append({'text': 'Shift/Flip','kwargs': {'icon': icons['shiftflip'],'triggered': lambda: self.newoperation(popupcad.manufacturing.shiftflip3.ShiftFlip3)}})
#self.operationactions.append({'text': '&LayerOp','kwargs': {'icon': icons['layerop'],'shortcut': 'Ctrl+Shift+L','triggered': lambda: self.newoperation(popupcad.manufacturing.layerop2.LayerOp2)}})
#self.operationactions.append({'text': 'More...', 'submenu': self.tools1, 'kwargs': {}})
#
#self.menu_file = self.addMenu(self.fileactions, name='File')
#self.menu_project = self.addMenu(self.projectactions, name='Project')
#self.menu_view = self.addMenu(self.viewactions, name='View')
#self.toolbar_operations, self.menu_operations = self.addToolbarMenu(self.operationactions, name='Operations')
#
##        menu_file = popupcad.guis.actions.build(self)
##        menu_bar = qg.QMenuBar()
##        menu_bar.addMenu(menu_file)
##        self.setMenuBar(menu_bar)
#
#self.showhide2(self.view_3d_dock, self.act_view_3d)
#self.showhide2(self.operationdock, self.act_view_ops)
#self.showhide2(self.layerlistwidgetdock, self.act_view_layers)
#self.showhide2(self.error_log, self.act_view_errors)