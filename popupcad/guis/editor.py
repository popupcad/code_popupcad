# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import sys
import os
import PySide.QtCore as qc
import PySide.QtGui as qg
import glob
import imp

import popupcad

from popupcad.filetypes.design import Design
from popupcad.supportfiles import Icon


class Editor(popupcad.widgets.widgetcommon.WidgetCommon, qg.QMainWindow):

    '''
    Editor Class

    The Editor is the main widget for popupCAD.
    '''
    gridchange = qc.Signal()
    operationedited = qc.Signal(object)
    operationadded = qc.Signal(object)

    def loggable(func):
        def log(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as ex:
                import traceback
                import sys
                tb = sys.exc_info()[2]
                exception_string = traceback.format_exception(type(ex), ex, tb)
                [self.error_log.appendText(item) for item in exception_string]

                m = qg.QMessageBox()
                m.setIcon(m.Warning)
                m.setText(ex.args[0])
                try:
                    m.setInformativeText(str(ex.args[1]))
                except IndexError:
                    pass
                try:
                    m.setDetailedText(str(ex.args[2]))
                except IndexError:
                    pass
                m.exec_()
                raise

        return log

    def __init__(self, parent=None, **kwargs):
        """Initialize Editor

        :param parent: Parent Widget(if any)
        :type parent: QWidget
        :returns:  nothing
        :raises: nothing
        """
        super(Editor, self).__init__(parent)
        self.error_log = popupcad.widgets.errorlog.ErrorLog()
        self.safe_init(parent, **kwargs)

    @loggable
    def safe_init(self, parent=None, **kwargs):
        self.scene = popupcad.graphics2d.graphicsscene.GraphicsScene()
        self.view_2d = popupcad.graphics2d.graphicsview.GraphicsView(
            self.scene)
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

        self.importscripts()

        self.operationeditor.currentRowChanged.connect(
            self.showcurrentoutput_inner)
        self.layerlistwidget.itemSelectionChanged.connect(
            self.showcurrentoutput)
        self.setWindowTitle('Editor')
        self.operationeditor.signal_edit.connect(self.editoperation)
        self.newfile()
        self.operationadded.connect(self.newoperationslot)
        self.operationedited.connect(self.editedoperationslot)

        self.createActions()
        self.backuptimer = qc.QTimer()
        self.backuptimer.setInterval(popupcad.backup_timeout)
        self.backuptimer.timeout.connect(self.autosave)
        self.backuptimer.start()

        self.set_nominal_size()
        self.move_center()
        self.operationdock.closeEvent = lambda event: self.action_uncheck(
            self.act_view_ops)
        self.layerlistwidgetdock.closeEvent = lambda event: self.action_uncheck(
            self.act_view_layers)
        self.view_3d_dock.closeEvent = lambda event: self.action_uncheck(
            self.act_view_3d)
        self.error_log.closeEvent = lambda event: self.action_uncheck(
            self.act_view_errors)

    def autosave(self):
        import os
        import glob
        filenames = glob.glob(popupcad.backupdir + '\\*.cad')
        filenames.sort(reverse=True)
        for filename in filenames[popupcad.backup_limit:]:
            os.remove(filename)

        time = popupcad.basic_functions.return_formatted_time()
        filename = os.path.normpath(
            os.path.join(
                popupcad.backupdir,
                'autosave_' +
                time +
                '.cad'))
        self.design.save_yaml(filename, update_filename=False)

    @loggable
    def importscripts(self):
        self.scriptclasses = []
        searchstring = os.path.normpath(
            os.path.join(
                popupcad.scriptdir,
                '*.py'))
        scripts = glob.glob(searchstring)
        for script in scripts:
            module = imp.load_source('module', script)
            self.scriptclasses.append(module.Script(self))

    @loggable
    def createActions(self):
        self.fileactions = []
        self.fileactions.append({'text': "&New",
                                 'kwargs': {'icon': Icon('new'),
                                            'shortcut': qg.QKeySequence.New,
                                            'statusTip': "Create a new file",
                                            'triggered': self.newfile}})
        self.fileactions.append({'text': "&Open...",
                                 'kwargs': {'icon': Icon('open'),
                                            'shortcut': qg.QKeySequence.Open,
                                            'statusTip': "Open an existing file",
                                            'triggered': self.open}})
        self.fileactions.append({'text': "&Save",
                                 'kwargs': {'icon': Icon('save'),
                                            'shortcut': qg.QKeySequence.Save,
                                            'statusTip': "Save the document to disk",
                                            'triggered': self.save}})
        self.fileactions.append({'text': "Save &As...",
                                 'kwargs': {'icon': Icon('saveas'),
                                            'shortcut': qg.QKeySequence.SaveAs,
                                            'statusTip': "Save the document under a new name",
                                            'triggered': self.saveAs}})
        self.fileactions.append({'text': "Upgrade",
                                 'kwargs': {'statusTip': "Upgrade the file",
                                            'triggered': self.upgrade}})
        self.fileactions.append({'text': '&Export to SVG', 'kwargs': {
                                'icon': Icon('export'), 'triggered': self.exportLayerSVG}})
        self.fileactions.append({'text': 'Export to dxf', 'kwargs': {
                                'icon': Icon('export'),
                                'statusTip': "Exports to a dxf file",                                
                                'triggered': self.export_dxf}})
        self.fileactions.append({'text': 'Export to dae', 'kwargs': {
                                'icon': Icon('export'),
                                'statusTip': "Exports to a dxf file",                                
                                'triggered': self.export_dae}})
        self.fileactions.append(
            {'text': "Save Joint Defs", 'kwargs': {'triggered': self.save_joint_def}})
        self.fileactions.append(
            {'text': "Export Laminate", 'kwargs': {'triggered': self.export_laminate}})
        self.fileactions.append(
            {'text': "Regen ID", 'kwargs': {'triggered': self.regen_id, }})
        self.fileactions.append(
            {'text': "Preferences...", 'kwargs': {'triggered': self.preferences}})
        self.fileactions.append(
            {'text': "Render Icons", 'kwargs': {'triggered': self.gen_icons}})
        self.fileactions.append(
            {'text': "Build Documentation", 'kwargs': {'triggered': self.build_documentation}})
        self.fileactions.append(
            {'text': "License", 'kwargs': {'triggered': self.show_license}})
        self.fileactions.append({'text': "Update...",
                                 'kwargs': {'triggered': self.download_installer}})

        self.projectactions = []
        self.projectactions.append({'text': '&Rebuild',
                                    'kwargs': {'icon': Icon('refresh'),
                                               'shortcut': qc.Qt.CTRL + qc.Qt.SHIFT + qc.Qt.Key_R,
                                               'triggered': self.reprocessoperations}})

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(True)
            self.act_autoreprocesstoggle = action
        self.projectactions.append(
            {'text': 'Auto Reprocess', 'kwargs': {}, 'prepmethod': dummy})
        self.projectactions.append(None)
        self.projectactions.append(
            {'text': 'Layer Order...', 'kwargs': {'triggered': self.editlayers}})
        self.projectactions.append(
            {'text': 'Laminate Properties...', 'kwargs': {'triggered': self.editlaminate}})
        self.projectactions.append(
            {'text': 'Sketches...', 'kwargs': {'triggered': self.sketchlist}})
        self.projectactions.append(
            {'text': 'SubDesigns...', 'kwargs': {'triggered': self.subdesigns}})
        self.projectactions.append(
            {'text': 'Replace...', 'kwargs': {'triggered': self.replace}})
        self.projectactions.append({'text': 'Insert Laminate Op and Replace...', 'kwargs': {
                                   'triggered': self.insert_and_replace}})

        self.viewactions = []

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(False)
            self.act_view_3d = action
        self.viewactions.append(
            {
                'prepmethod': dummy,
                'text': '3D View',
                'kwargs': {
                    'icon': Icon('3dview'),
                    'triggered': lambda: self.showhide2(
                        self.view_3d_dock,
                        self.act_view_3d)}})

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(True)
            self.act_view_ops = action
        self.viewactions.append(
            {
                'prepmethod': dummy,
                'text': 'Operations',
                'kwargs': {
                    'icon': Icon('operations'),
                    'triggered': lambda: self.showhide2(
                        self.operationdock,
                        self.act_view_ops)}})

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(True)
            self.act_view_layers = action
        self.viewactions.append(
            {
                'prepmethod': dummy,
                'text': 'Layers',
                'kwargs': {
                    'icon': Icon('layers'),
                    'triggered': lambda: self.showhide2(
                        self.layerlistwidgetdock,
                        self.act_view_layers)}})

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(False)
            self.act_view_errors = action
        self.viewactions.append({'prepmethod': dummy, 'text': 'Error Log', 'kwargs': {
                                'triggered': lambda: self.showhide2(self.error_log, self.act_view_errors)}})

        self.viewactions.append({'text': 'Zoom Fit',
                                 'kwargs': {'triggered': self.view_2d.zoomToFit,
                                            'shortcut': qc.Qt.CTRL + qc.Qt.Key_F}})
        self.viewactions.append({'text': 'Screenshot',
                                 'kwargs': {'triggered': self.scene.screenShot,
                                            'shortcut': qc.Qt.CTRL + qc.Qt.Key_R}})
        self.viewactions.append(
            {'text': '3D Screenshot', 'kwargs': {'triggered': self.screenshot_3d}})

        self.tools1 = []
        self.tools1.append(
            {
                'text': 'Cleanup',
                'kwargs': {
                    'icon': Icon('cleanup'),
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.cleanup2.Cleanup2)}})
        self.tools1.append(
            {
                'text': 'New Cleanup',
                'kwargs': {
                    'icon': Icon('cleanup'),
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.cleanup3.Cleanup3)}})
        self.tools1.append(
            {
                'text': 'Simplify',
                'kwargs': {
                    'icon': Icon('simplify'),
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.simplify2.Simplify2)}})
        self.tools1.append(
            {
                'text': 'Joints',
                'kwargs': {
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.joint_operation2.JointOperation2)}})
        self.tools1.append({'text': 'Freeze', 'kwargs': {
                           'triggered': lambda: self.newoperation(popupcad.manufacturing.freeze.Freeze)}})
        self.tools1.append(
            {
                'text': 'Cross-Section',
                'kwargs': {
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.cross_section.CrossSection)}})
        self.tools1.append(
            {
                'text': 'Sub-Operation',
                'kwargs': {
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.sub_operation.SubOperation)}})

        self.operationactions = []
        self.operationactions.append(
            {
                'text': '&SketchOp',
                'kwargs': {
                    'icon': Icon('polygons'),
                    'shortcut': qc.Qt.CTRL +
                    qc.Qt.SHIFT +
                    qc.Qt.Key_S,
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.simplesketchoperation.SimpleSketchOp)}})
        self.operationactions.append(
            {
                'text': '&LaminateOp',
                'kwargs': {
                    'icon': Icon('metaop'),
                    'shortcut': qc.Qt.CTRL +
                    qc.Qt.SHIFT +
                    qc.Qt.Key_M,
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.laminateoperation2.LaminateOperation2)}})
        self.operationactions.append(
            {
                'text': '&Dilate/Erode',
                'kwargs': {
                    'icon': Icon('bufferop'),
                    'shortcut': qc.Qt.CTRL +
                    qc.Qt.SHIFT +
                    qc.Qt.Key_B,
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.bufferop3.BufferOperation3)}})
        self.operationactions.append(
            {
                'text': '&PlaceOp',
                'kwargs': {
                    'icon': Icon('placeop'),
                    'shortcut': qc.Qt.CTRL +
                    qc.Qt.SHIFT +
                    qc.Qt.Key_P,
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.placeop8.PlaceOperation8)}})
        self.operationactions.append(
            {
                'text': 'L&ocateOp',
                'kwargs': {
                    'icon': Icon('locate'),
                    'shortcut': qc.Qt.CTRL +
                    qc.Qt.SHIFT +
                    qc.Qt.Key_O,
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.locateoperation3.LocateOperation3)}})
        self.operationactions.append(
            {
                'text': 'Shift/Flip',
                'kwargs': {
                    'icon': Icon('shiftflip'),
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.shiftflip3.ShiftFlip3)}})
        self.operationactions.append(
            {
                'text': '&LayerOp',
                'kwargs': {
                    'icon': Icon('layerop'),
                    'shortcut': qc.Qt.CTRL +
                    qc.Qt.SHIFT +
                    qc.Qt.Key_L,
                    'triggered': lambda: self.newoperation(
                        popupcad.manufacturing.layerop2.LayerOp2)}})
        self.operationactions.append(
            {'text': 'More...', 'submenu': self.tools1, 'kwargs': {}})

        self.menu_file = self.addMenu(self.fileactions, name='File')
        self.menu_project = self.addMenu(self.projectactions, name='Project')
        self.menu_view = self.addMenu(self.viewactions, name='View')
        self.toolbar_operations, self.menu_operations = self.addToolbarMenu(
            self.operationactions, name='Operations')

        self.showhide2(self.view_3d_dock, self.act_view_3d)
        self.showhide2(self.operationdock, self.act_view_ops)
        self.showhide2(self.layerlistwidgetdock, self.act_view_layers)
        self.showhide2(self.error_log, self.act_view_errors)

    def get_design(self):
        return self.design

    @loggable
    def newoperation(self, operationclass):
        operationclass.new(
            self,
            self.design,
            self.operationeditor.currentRow(),
            self.operationadded)

    @loggable
    def editoperation(self, operation):
        operation.edit(self, self.design, self.operationedited)

    def regen_id(self):
        self.design.regen_id()

    @loggable
    def newoperationslot(self, operation):
        self.design.operations.append(operation)
        if self.act_autoreprocesstoggle.isChecked():
            self.reprocessoperations([operation])

    @loggable
    def editedoperationslot(self, operation):
        if self.act_autoreprocesstoggle.isChecked():
            self.reprocessoperations([operation])

    @loggable
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

    @loggable
    def newfile(self):
        from popupcad.filetypes.layerdef import LayerDef
        from popupcad.materials.materials import Carbon_0_90_0, Pyralux, Kapton
        design = Design()
        design.define_layers(
            LayerDef(
                Carbon_0_90_0(),
                Pyralux(),
                Kapton(),
                Pyralux(),
                Carbon_0_90_0()))
        self.load_design(design)
        self.view_2d.zoomToFit()

    @loggable
    def open(self, filename=None):
        if filename is None:
            design = Design.open(self)
        else:
            design = Design.load_yaml(filename)
        if not design is None:
            self.load_design(design)
            if self.act_autoreprocesstoggle.isChecked():
                self.reprocessoperations()
            self.view_2d.zoomToFit()

    @loggable
    def save(self):
        return self.design.save(self)

    @loggable
    def saveAs(self, parent=None):
        return self.design.saveAs(self)

    @loggable
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

    @loggable
    def editlayers(self):
        window = popupcad.widgets.materialselection.MaterialSelection(
            self.design.return_layer_definition().layers,
            popupcad.materials.materials.available_materials,
            self)
        result = window.exec_()
        if result == window.Accepted:
            self.design.define_layers(window.layerdef)
        self.updatelayerlist()
        self.layerlistwidget.selectAll()

    @loggable
    def editlaminate(self):
        from dev_tools.propertyeditor import PropertyEditor
        dialog = self.builddialog(
            PropertyEditor(
                self.design.return_layer_definition().layers))
        dialog.exec_()
        self.design.return_layer_definition().refreshzvalues()

    @loggable
    def sketchlist(self):
        from popupcad.widgets.listmanager import AdvancedSketchListManager
        widget = AdvancedSketchListManager(self.design)
        dialog = self.builddialog(widget)
        dialog.setWindowTitle('Sketches')
        dialog.exec_()

    @loggable
    def subdesigns(self):
        from popupcad.widgets.listmanager import AdvancedDesignListManager
        widget = AdvancedDesignListManager(self.design)
        dialog = self.builddialog(widget)
        dialog.setWindowTitle('Sub-Designs')
        dialog.exec_()

    @loggable
    def updatelayerlist(self):
        self.layerlistwidget.linklist(
            self.design.return_layer_definition().layers)

    @loggable
    def showcurrentoutput(self):
        if len(self.design.operations)>0:
            selected_indeces = self.operationeditor.currentIndeces2()
            if len(selected_indeces) > 0:
                ii, jj = selected_indeces[0]
            else:
                ii, jj = -1, 0
                self.operationeditor.selectIndeces([(ii, jj)])
            self.showcurrentoutput_inner(ii, jj)

    @loggable
    def showcurrentoutput_inner(self, ii, jj):
        try:
            self.scene.deleteall()
            self.view_3d.view.clear()
            operationoutput = self.design.operations[ii].output[jj]
            selectedlayers = [item for item in self.design.return_layer_definition(
            ).layers if item in self.layerlistwidget.selectedData()]
            self.show2dgeometry3(operationoutput, selectedlayers)
            self.show3dgeometry3(operationoutput, selectedlayers)
        except IndexError:
            raise

    @loggable
    def show2dgeometry3(self, operationoutput, selectedlayers,):
        display_geometry_2d = operationoutput.display_geometry_2d()
        self.scene.deleteall()
        for layer in selectedlayers[::1]:
            for geom in display_geometry_2d[layer]:
                self.scene.addItem(geom)
                geom.setselectable(True)

    @loggable
    def show3dgeometry3(self, operationoutput, selectedlayers):
        if self.act_view_3d.isChecked():
            tris = operationoutput.tris()
            self.view_3d.view.update_object(
                self.design.return_layer_definition().zvalue,
                tris,
                selectedlayers)
        else:
            self.clear3dgeometry()

    def clear3dgeometry(self):
        tris = dict([(layer, [])
                     for layer in self.design.return_layer_definition().layers])
        self.view_3d.view.update_object(
            self.design.return_layer_definition().zvalue,
            tris,
            [])

    @loggable
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

        generic_laminate = self.design.operations[
            ii].output[jj].generic_laminate()
        for layernum, layer in enumerate(
            self.design.return_layer_definition().layers[
                ::1]):
            basename = self.design.get_basename() + '_' + \
                str(self.design.operations[ii]) + '_layer{0:02d}.svg'.format(layernum + 1)
            scene = popupcad.graphics2d.graphicsscene.GraphicsScene()
            geoms = [
                item.outputstatic(
                    brush_color=(
                        1,
                        1,
                        1,
                        0)) for item in generic_laminate.geoms[layer]]
            [scene.addItem(geom) for geom in geoms]
            scene.renderprocess(basename, *win.acceptdata())

    def closeEvent(self, event):
        if self.checkSafe():
            self.error_log.close()
            event.accept()
        else:
            event.ignore()
        popupcad.local_settings.save_yaml(popupcad.local_settings_filename)

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

    @loggable
    def preferences(self):
        import dev_tools.propertyeditor
        pe = dev_tools.propertyeditor.PropertyEditor(popupcad.local_settings)
        pe.show()

    @loggable
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

    @loggable
    def insert_and_replace(self):
        from popupcad.manufacturing.laminateoperation2 import LaminateOperation2
        operation_ref, output_index = self.operationeditor.currentRefs()[0]
        operation_index = self.design.operation_index(operation_ref)
        newop = LaminateOperation2({'unary': [], 'binary': []}, 'union')
        self.design.operations.insert(operation_index + 1, newop)
        self.design.replace_op_refs(
            (operation_ref, output_index), (newop.id, 0))
        newop.operation_links['unary'].append((operation_ref, output_index))
        self.reprocessoperations()

    @loggable
    def upgrade(self):
        try:
            self.load_design(self.design.upgrade())
        except popupcad.filetypes.design.UpgradeError as ex:
            print(ex)
            raise
        if self.act_autoreprocesstoggle.isChecked():
            self.reprocessoperations()
        self.view_2d.zoomToFit()

    @loggable
    def download_installer(self):
        qg.QDesktopServices.openUrl(popupcad.update_url)

    @loggable
    def save_joint_def(self):
        self.design.save_joint_def()

    @loggable
    def screenshot_3d(self):
        time = popupcad.basic_functions.return_formatted_time()
        filename = os.path.normpath(
            os.path.join(
                popupcad.exportdir,
                '3D_screenshot_' +
                time +
                '.png'))
#        self.view_3d.view.initializeGL()
#        self.view_3d.view.update()
        self.view_3d.view.grabFrameBuffer().save(filename)

    @loggable
    def export_laminate(self):
        ii, jj = self.operationeditor.currentIndeces2()[0]
        output = self.design.operations[ii].output[jj]
        generic = output.csg.to_generic_laminate()
        generic.saveAs()

    @loggable
    def gen_icons(self):
        self.design.raster()

    @loggable
    def build_documentation(self):
        self.design.build_documentation()

    @loggable
    def export_dxf(self):
        import os
        ii, jj = self.operationeditor.currentIndeces2()[0]
        output = self.design.operations[ii].output[jj]
        generic = output.generic_laminate()
        generic.save_dxf(os.path.normpath(os.path.join(popupcad.exportdir,self.design.get_basename() + '_'+str(self.design.operations[ii])+'.dxf')))

    @loggable
    def export_dae(self):
        ii, jj = self.operationeditor.currentIndeces2()[0]
        output = self.design.operations[ii].output[jj]
        output.generic_laminate().toDAE()

    @loggable
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

if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    app.setWindowIcon(Icon('popupcad'))
    mw = Editor()
    mw.show()
    mw.raise_()
    sys.exit(app.exec_())
