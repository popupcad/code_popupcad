# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import sys
import os

import qt.QtCore as qc
import qt.QtGui as qg
import glob
import imp
from popupcad.widgets.export_widget import DxfExportWidget
import popupcad
import yaml
from popupcad.filetypes.design import Design

class NoOutput(Exception):
    def __init__(self):
        Exception.__init__(self,'Operation has not been processed due to a previous exception')

class Editor(popupcad.widgets.widgetcommon.MainGui, qg.QMainWindow):

    '''
    Editor Class

    The Editor is the main widget for popupCAD.
    '''
    gridchange = qc.Signal()
    operationedited = qc.Signal(object)
    operationadded = qc.Signal(object)

    def __init__(self, parent=None, **kwargs):
        """Initialize Editor

        :param parent: Parent Widget(if any)
        :type parent: QWidget
        :returns:  nothing
        :raises: nothing
        """
        super(Editor, self).__init__(parent)
        self.error_log = popupcad.widgets.textwindow.TextWindow()
        self.safe_init(parent, **kwargs)

    
    def safe_init(self, parent=None, **kwargs):
        self.view_2d = popupcad.graphics2d.graphicsview.GraphicsView()
        self.scene = popupcad.graphics2d.graphicsscene.GraphicsScene(self.view_2d)
        self.view_2d.setScene(self.scene)
        self.view_2d.finish_init()
        self.scene.connect_mouse_modes(self.view_2d)

        self.view_2d.scrollhand()
        self.setCentralWidget(self.view_2d)

        self.setTabPosition(qc.Qt.AllDockWidgetAreas, qg.QTabWidget.South)

        self.operationeditor = popupcad.widgets.dragndroptree.DirectedDraggableTreeWidget()
        self.operationeditor.enable()

        self.layerlistwidget = popupcad.widgets.listeditor.ListSelector()

        self.operationdock = qg.QDockWidget()
        self.operationdock.setWidget(self.operationeditor)
        self.operationdock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
        self.operationdock.setWindowTitle('Operations')
        self.addDockWidget(qc.Qt.LeftDockWidgetArea, self.operationdock)

        self.layerlistwidgetdock = qg.QDockWidget()
        self.layerlistwidgetdock.setWidget(self.layerlistwidget)
        self.layerlistwidgetdock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
        self.layerlistwidgetdock.setWindowTitle('Layers')
        self.addDockWidget(qc.Qt.LeftDockWidgetArea, self.layerlistwidgetdock)

        self.view_3d = popupcad.graphics3d.gl_viewer.GLObjectViewer(self)
        self.view_3d_dock = qg.QDockWidget()
        self.view_3d_dock.setWidget(self.view_3d)
        self.view_3d_dock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
        self.view_3d_dock.setWindowTitle('3D Visualization')
        self.addDockWidget(qc.Qt.RightDockWidgetArea, self.view_3d_dock)

        self.operationeditor.currentRowChanged.connect(
            self.showcurrentoutput_inner)
        self.layerlistwidget.itemSelectionChanged.connect(
            self.showcurrentoutput)
        self.setWindowTitle('Editor')
        self.operationeditor.signal_edit.connect(self.editoperation)
        self.newfile()
        self.operationadded.connect(self.newoperationslot)
        self.operationedited.connect(self.editedoperationslot)

        self.create_menu_system(popupcad.supportfiledir+'/editor_menu.yaml')
        
        self.show_hide_view_3d()
        self.show_hide_operationdock()
        self.show_hide_layerlistwidgetdock()
        self.show_hide_error_log()
        
        self.backuptimer = qc.QTimer()
        self.backuptimer.setInterval(popupcad.backup_timeout)
        self.backuptimer.timeout.connect(self.autosave)
        self.backuptimer.start()
        
        self.view_3d_dock.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_3d'])
        self.operationdock.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_operations'])
        self.layerlistwidgetdock.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_layers'])
        self.error_log.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_error_log'])

    def autosave(self):
        self.design.backup(popupcad.backupdir,'_autosave_')
        
    def show_hide_view_3d(self):
        if self.menu_system.actions['view_3d'].isChecked():
            self.view_3d_dock.show()
        else:
            self.view_3d_dock.hide()

    def show_hide_operationdock(self):
        if self.menu_system.actions['view_operations'].isChecked():
            self.operationdock.show()
        else:
            self.operationdock.hide()

    def show_hide_layerlistwidgetdock(self):
        if self.menu_system.actions['view_layers'].isChecked():
            self.layerlistwidgetdock.show()
        else:
            self.layerlistwidgetdock.hide()

    def show_hide_error_log(self):
        if self.menu_system.actions['view_error_log'].isChecked():
            self.error_log.show()
        else:
            self.error_log.hide()
        
    def new_cleanup2(self):
        self.newoperation(popupcad.manufacturing.cleanup2.Cleanup2)
    def new_cleanup3(self):
        self.newoperation(popupcad.manufacturing.cleanup3.Cleanup3)
    def new_simplify2(self):
        self.newoperation(popupcad.manufacturing.simplify2.Simplify2)
    def new_jointop3(self):
        self.newoperation(popupcad.manufacturing.joint_operation3.JointOperation3)
    def new_holeop(self):
        self.newoperation(popupcad.manufacturing.hole_operation.HoleOperation)
    def new_freezeop(self):
        self.newoperation(popupcad.manufacturing.freeze.Freeze)
    def new_cross_section(self):
        self.newoperation(popupcad.manufacturing.cross_section.CrossSection)
    def new_subop(self):
        self.newoperation(popupcad.manufacturing.sub_operation2.SubOperation2)
    def new_codeop(self):
        self.newoperation(popupcad.manufacturing.code_exec_op.CodeExecOperation)
    def new_transform_internal(self):
        self.newoperation(popupcad.manufacturing.transform_internal.TransformInternal)
    def new_transform_external(self):
        self.newoperation(popupcad.manufacturing.transform_external.TransformExternal)
    def new_shiftflip(self):
        self.newoperation(popupcad.manufacturing.shiftflip3.ShiftFlip3)
    def new_sketch_op(self):
        self.newoperation(popupcad.manufacturing.simplesketchoperation.SimpleSketchOp)
    def new_laminate_op(self):
        self.newoperation(popupcad.manufacturing.laminateoperation2.LaminateOperation2)
    def new_buffer_op(self):
        self.newoperation(popupcad.manufacturing.bufferop3.BufferOperation3)
    def new_layer_op(self):
        self.newoperation(popupcad.manufacturing.layerop2.LayerOp2)
    def new_hollow(self):
        self.newoperation(popupcad.manufacturing.hollow.Hollow)
    def new_fill(self):
        self.newoperation(popupcad.manufacturing.fill.Fill)

    def zoomToFit(self):
        self.view_2d.zoomToFit()

    def screenShot(self):
        self.scene.screenShot()

    def operation_network(self):
        import popupcad.widgets.operationnetwork
        widget = popupcad.widgets.operationnetwork.action_method(self)
        hierarchy_dock = qg.QDockWidget()
        hierarchy_dock.setWidget(widget)
        hierarchy_dock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
        hierarchy_dock.setWindowTitle('Hierarchy')
        self.addDockWidget(qc.Qt.RightDockWidgetArea, hierarchy_dock)

    @property
    def design(self):
        return self._design

    @design.setter
    def design(self,design):
        self._design = design
    
    @design.deleter
    def design(self):
        del self._design
    
    def get_design(self):
        return self.design
    
    def newoperation(self, operationclass):
        operationclass.new(self,self.design,self.operationeditor.currentRow(),self.operationadded)
    
    def editoperation(self, operation):
        operation.edit(self, self.design, self.operationedited)

    def regen_id(self):
        self.design.regen_id()
    
    def newoperationslot(self, operation):
        self.design.append_operation(operation)
        if self.menu_system.actions['project_auto_reprocess'].isChecked():
            self.reprocessoperations([operation])
    
    def editedoperationslot(self, operation):
        if self.menu_system.actions['project_auto_reprocess'].isChecked():
            self.reprocessoperations([operation])
    
    def reprocessoperations_outer(self):
        self.reprocessoperations(None)
        
    def reprocessoperations(self, operations=None):
        try:
            self.design.reprocessoperations(operations)
            self.operationeditor.refresh()
            self.showcurrentoutput()
            self.view_2d.zoomToFit()
        except:
            raise
        finally:
            self.operationeditor.refresh()

    def newfile(self):
        from popupcad.filetypes.layerdef import LayerDef
        import popupcad.filetypes.material2 as materials
#        from popupcad.materials.materials import Carbon_0_90_0, Pyralux, Kapton
        design = Design.new()
        design.define_layers(LayerDef(*materials.default_sublaminate))
        self.load_design(design)
        self.view_2d.zoomToFit()
    
    def open_filename(self,filename):
        design = Design.load_yaml(filename)
        if not design is None:
            self.load_design(design)
            if self.menu_system.actions['project_auto_reprocess'].isChecked():
                self.reprocessoperations()
            self.view_2d.zoomToFit()
        
    def open(self):
        design = Design.open(self)
        if not design is None:
            self.load_design(design)
            if self.menu_system.actions['project_auto_reprocess'].isChecked():
                self.reprocessoperations()
            self.view_2d.zoomToFit()

    def save(self):
        value = self.design.save(self)
        self.update_window_title()
        return value
    
    def saveAs(self):
        value = self.design.saveAs(self)
        self.update_window_title()
        return value
    
    def load_design(self, design):
        self.design = design
        self.operationeditor.blockSignals(True)
        self.layerlistwidget.blockSignals(True)
        self.scene.deleteall()
        self.clear3dgeometry()

        self.operationeditor.set_tree_generator(self.design.build_tree)
        self.operationeditor.set_get_design(self.get_design)
        self.operationeditor.linklist(self.design.operations)

        self.updatelayerlist()
        self.layerlistwidget.selectAll()
        self.operationeditor.blockSignals(False)
        self.layerlistwidget.blockSignals(False)
        self.update_window_title()
    
    def editlayers(self):
        available_materials = popupcad.filetypes.material2.default_materials+popupcad.user_materials
        window = popupcad.widgets.materialselection.MaterialSelection(
            self.design.return_layer_definition().layers,
            available_materials,
            self)
        result = window.exec_()
        if result == window.Accepted:
            self.design.define_layers(window.layerdef)
        self.updatelayerlist()
        self.layerlistwidget.selectAll()
    
    def editlaminate(self):
        from idealab_tools.propertyeditor import PropertyEditor
        dialog = self.builddialog(PropertyEditor(self.design.return_layer_definition().layers))
        dialog.exec_()
        del self.design.return_layer_definition().z_values
    
    def sketchlist(self):
        from popupcad.widgets.listmanager import AdvancedSketchListManager
        widget = AdvancedSketchListManager(self.design)
        dialog = self.builddialog(widget)
        dialog.setWindowTitle('Sketches')
        dialog.exec_()

    def subdesigns(self):
        from popupcad.widgets.listmanager import AdvancedDesignListManager
        widget = AdvancedDesignListManager(self.design)
        dialog = self.builddialog(widget)
        dialog.setWindowTitle('Sub-Designs')
        dialog.exec_()

    def updatelayerlist(self):
        self.layerlistwidget.linklist(
            self.design.return_layer_definition().layers)

    def showcurrentoutput(self):
        if len(self.design.operations)>0:
            selected_indeces = self.operationeditor.currentIndeces2()
            if len(selected_indeces) > 0:
                ii, jj = selected_indeces[0]
            else:
                ii, jj = -1, 0
                self.operationeditor.selectIndeces([(ii, jj)])
            self.showcurrentoutput_inner(ii, jj)

    def showcurrentoutput_inner(self, ii, jj):
        self.scene.deleteall()
        self.view_3d.view.clear()
        try:
            operationoutput = self.design.operations[ii].output[jj]
        except IndexError:
            raise
        except AttributeError:
            raise NoOutput()
        selectedlayers = [item for item in self.design.return_layer_definition().layers if item in self.layerlistwidget.selectedData()]
        self.show2dgeometry3(operationoutput, selectedlayers)
        self.show3dgeometry3(operationoutput, selectedlayers)
    
    def show2dgeometry3(self, operationoutput, selectedlayers,):
        display_geometry_2d = operationoutput.display_geometry_2d()
        self.scene.deleteall()
        for layer in selectedlayers[::1]:
            for geom in display_geometry_2d[layer]:
                self.scene.addItem(geom)
                geom.setselectable(True)
    
    def show3dgeometry3(self, operationoutput, selectedlayers):
        if self.menu_system.actions['view_3d'].isChecked():
            layerdef = self.design.return_layer_definition()
            triangles = operationoutput.triangles_by_layer
            self.view_3d.view.update_object(layerdef,triangles,selectedlayers)
        else:
            self.clear3dgeometry()

    def clear3dgeometry(self):
        tris = dict([(layer, []) for layer in self.design.return_layer_definition().layers])
        layerdef = self.design.return_layer_definition()
        self.view_3d.view.update_object(layerdef,tris,[])
    
    def exportLayerSVG(self):
        from popupcad.graphics2d.svg_support import OutputSelection

        win = OutputSelection()
        accepted = win.exec_()
        if not accepted:
            return

        selected_indeces = self.operationeditor.currentIndeces2()
        if len(selected_indeces) > 0:
            ii, jj = selected_indeces[0]
        else:
            ii, jj = -1, 0
            self.operationeditor.selectIndeces([(ii, jj)])

        generic_laminate = self.design.operations[ii].output[jj].generic_laminate()

        for layernum, layer in enumerate(self.design.return_layer_definition().layers[::1]):
            basename = self.design.get_basename() + '_' + str(self.design.operations[ii]) + '_layer{0:02d}.svg'.format(layernum + 1)
            scene = popupcad.graphics2d.graphicsscene.GraphicsScene()
            geoms = [item.outputstatic(brush_color=(1,1,1,0)) for item in generic_laminate.geoms[layer]]
            [scene.addItem(geom) for geom in geoms]
            scene.renderprocess(basename, *win.acceptdata())

    def closeEvent(self, event):
        if self.checkSafe():
            self.error_log.close()
            event.accept()
        else:
            event.ignore()

    def checkSafe(self):
        temp = qg.QMessageBox.warning(
            self,
            "Modified Document",
            'This file has been modified.\nDo you want to save your'
            'changes?',
            qg.QMessageBox.Save | qg.QMessageBox.Discard | qg.QMessageBox.Cancel)
        if temp == qg.QMessageBox.Save:
            return self.save()
        elif temp == qg.QMessageBox.Cancel:
            return False
        return True
    
    def replace(self):
        d = qg.QDialog()
        operationlist = popupcad.widgets.dragndroptree.DraggableTreeWidget()
        operationlist.linklist(self.design.operations)
        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)
        layout3 = qg.QVBoxLayout()
        layout3.addWidget(operationlist)
        layout3.addLayout(layout2)
        d.setLayout(layout3)
        button1.clicked.connect(d.accept)
        button2.clicked.connect(d.reject)
        result = d.exec_()
        if result:
            self.design.replace_op_refs(
                self.operationeditor.currentRefs()[0],
                operationlist.currentRefs()[0])
        self.reprocessoperations()
    
    def insert_and_replace(self):
        from popupcad.manufacturing.laminateoperation2 import LaminateOperation2
        operation_ref, output_index = self.operationeditor.currentRefs()[0]
        operation_index = self.design.operation_index(operation_ref)
        newop = LaminateOperation2({'unary': [], 'binary': []}, 'union')
        self.design.insert_operation(operation_index + 1, newop)
        self.design.replace_op_refs(
            (operation_ref, output_index), (newop.id, 0))
        newop.operation_links['unary'].append((operation_ref, output_index))
        self.reprocessoperations()

    def upgrade(self):
        try:
            self.load_design(self.design.upgrade())
        except popupcad.filetypes.design.UpgradeError as ex:
            print(ex)
            raise
        if self.menu_system.actions['project_auto_reprocess'].isChecked():
            self.reprocessoperations()
        self.view_2d.zoomToFit()
    
#    def download_installer(self):
#        qg.QDesktopServices.openUrl(popupcad.update_url)
    
    def save_joint_def(self):
        self.design.save_joint_def()
    
    def screenshot_3d(self):
        time = popupcad.basic_functions.return_formatted_time()
        filename = os.path.normpath(os.path.join(popupcad.exportdir,'3D_screenshot_' + time + '.png'))
        self.view_3d.view.grabFrameBuffer().save(filename)
    
    def gen_icons(self):
        self.design.raster()
    
    def build_documentation(self):
        self.design.build_documentation()

    def export_dxf_outer(self):
        try:
            dirname = self.design.dirname        
        except AttributeError:
            dirname = popupcad.exportdir
        dialog = DxfExportWidget(dirname)
        result = dialog.exec_()
        if result:
            accept_data = dialog.accept_data()
            ii, jj = self.operationeditor.currentIndeces2()[0]
            output = self.design.operations[ii].output[jj]
            generic = output.generic_laminate()
            basename = self.design.get_basename() + '_'+str(self.design.operations[ii])
            generic.save_dxf(basename,separate_files=accept_data['separate_layers'],directory = accept_data['directory'])

    def export_foldable_laminate(self):
        try:
            dirname = self.design.dirname        
        except AttributeError:
            dirname = popupcad.exportdir
        dialog = DxfExportWidget(dirname)
        result = dialog.exec_()
        if result:
            accept_data = dialog.accept_data()
            ii, jj = self.operationeditor.currentIndeces2()[0]
            output = self.design.operations[ii].output[jj]
            generic = output.generic_laminate()
            foldable = generic.to_foldable_robotics()
#            foldable.plot(new=True)
            basename = self.design.get_basename() + '_'+str(self.design.operations[ii])
            dict1 = foldable.export_dict()
#            print(dict1)
            filename = os.path.join(accept_data['directory'],basename+'.yaml')
            with open(filename,'w') as f:
                yaml.dump(dict1,f)

    def show_license(self):
        import sys

        if hasattr(sys,'frozen'):
            path = popupcad.localpath
        else:
            path = os.path.normpath(os.path.join(popupcad.localpath,'../'))

        path = os.path.normpath(os.path.join(path,'LICENSE'))
        with open(path) as f:
            license_text = f.readlines()

        w = qg.QDialog()
        le = qg.QTextEdit()
        le.setText(''.join(license_text))
        le.setReadOnly(True)
        le.show()
        layout = qg.QVBoxLayout()
        layout.addWidget(le)        
        w.setLayout(layout)
        f = lambda: qc.QSize(600,400)
        w.sizeHint = f
        w.exec_()
    
    def update_window_title(self):
        basename = self.design.get_basename()
        self.setWindowTitle('Editor'+' - '+basename)


if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    mw = Editor()
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())
