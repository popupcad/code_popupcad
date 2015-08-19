# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import sys
import PySide.QtGui as qg
import PySide.QtCore as qc
import popupcad
import numpy

import popupcad.filetypes.constraints as constraints

from popupcad.geometry.vertex import ShapeVertex, DrawnPoint
from popupcad.graphics2d.interactivevertex import InteractiveVertex, ReferenceInteractiveVertex, DrawingPoint, InteractiveVertexBase
from popupcad.graphics2d.interactiveedge import InteractiveEdge, ReferenceInteractiveEdge
from popupcad.graphics2d.interactive import Interactive
from popupcad.graphics2d.proto import ProtoLine, ProtoPath, ProtoCircle, ProtoPoly, ProtoRect2Point
from popupcad.graphics2d.graphicsscene import GraphicsScene
from popupcad.graphics2d.graphicsview import GraphicsView
from popupcad.filetypes.sketch import Sketch
from popupcad.widgets.listeditor import ListEditor
from popupcad.supportfiles import Icon
from popupcad.widgets.widgetcommon import WidgetCommon
from popupcad.filetypes.undoredo import UndoRedo
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.manufacturing.nulloperation import NullOp
from popupcad.graphics2d.text import TextParent

class Sketcher(WidgetCommon, qg.QMainWindow):
    showprop = qc.Signal(object)

    def __init__(self,parent,sketch,design=None,accept_method=None,selectops=False):

        qg.QMainWindow.__init__(self, parent)
        self.design = design
        self.accept_method = accept_method
        self.selectops = selectops

        if self.design is None:
            self.operations = [NullOp()]
        else:
            self.operations = [NullOp()] + self.design.operations[:]

        self.setupLayout()

        if self.selectops:
            self.optree.linklist(self.operations)

        self.undoredo = UndoRedo(self.get_current_sketch, self.loadsketch)
        self.loadsketch(sketch)
        self.undoredo.restartundoqueue()
        self.createActions()
        self.load_references()
        self.connectSignals()

    def connectSignals(self):
        self.setWindowModality(qc.Qt.WindowModality.ApplicationModal)
        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.scene.itemclicked.connect(self.loadpropwindow)
        self.showprop.connect(self.loadpropwindow)
        self.scene.newpolygon.connect(self.undoredo.savesnapshot)
        self.scene.savesnapshot.connect(self.undoredo.savesnapshot)
        self.scene.itemdeleted.connect(self.cleanupconstraints)
        self.scene.refresh_request.connect(self.refreshconstraints)
        self.scene.constraint_update_request.connect(self.update_selective)
        
        self.constraint_editor.signal_edit.connect(self.editItem)
        self.constraint_editor.itemPressed.connect(self.showconstraint_item)
        self.constraint_editor.itemdeleted.connect(self.constraint_deleted)
        if self.selectops:
            self.optree.currentRowChanged.connect(self.load_references_inner)

    def setupLayout(self):
        self.constraint_editor = ListEditor()
        if self.selectops:
            self.optree = DraggableTreeWidget()
        self.propertieswindow = qg.QWidget()

        ok_button = qg.QPushButton('&Ok', self)
        cancel_button = qg.QPushButton('&Cancel', self)
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        sublayout = qg.QHBoxLayout()
        sublayout.addStretch(1)
        sublayout.addWidget(ok_button)
        sublayout.addWidget(cancel_button)
        sublayout.addStretch(1)

        self.scene = GraphicsScene()
        self.graphicsview = GraphicsView(self.scene)

        centrallayout = qg.QVBoxLayout()
        centrallayout.addWidget(self.graphicsview)
        centrallayout.addLayout(sublayout)
        centralwidget = qg.QWidget()
        centralwidget.setLayout(centrallayout)

        if self.selectops:
            self.optreedock = qg.QDockWidget()
            self.optreedock.setWidget(self.optree)
            self.optreedock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
            self.optreedock.setWindowTitle('Operatons')

        self.constraintdock = qg.QDockWidget()
        self.constraintdock.setWidget(self.constraint_editor)
        self.constraintdock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
        self.constraintdock.setWindowTitle('Constraints')
        self.constraintdock.setMinimumHeight(200)

        self.propdock = qg.QDockWidget()
        self.propdock.setWidget(self.propertieswindow)
        self.propdock.setAllowedAreas(qc.Qt.AllDockWidgetAreas)
        self.propdock.setWindowTitle('Properties')
        self.propdock.setMinimumHeight(200)

        if self.selectops:
            self.addDockWidget(qc.Qt.LeftDockWidgetArea, self.optreedock)
        self.addDockWidget(qc.Qt.RightDockWidgetArea, self.constraintdock)
        self.addDockWidget(qc.Qt.RightDockWidgetArea, self.propdock)

        self.setCentralWidget(centralwidget)
        self.setWindowTitle('Sketcher')

        self.set_nominal_size()
        self.move_center()

        if self.selectops:
            self.optreedock.closeEvent = lambda event: self.action_uncheck(
                self.act_view_ops)
        self.constraintdock.closeEvent = lambda event: self.action_uncheck(
            self.act_view_constraints)
        self.propdock.closeEvent = lambda event: self.action_uncheck(
            self.act_view_properties)

    def regen_id(self):
        self.sketch.regen_id()

    def editItem(self, constraint):
        self.undoredo.savesnapshot()
        constraint.edit()
        self.refreshconstraints()

    def createActions(self):
        icons = popupcad.guis.icons.icons
        self.fileactions = []
        self.fileactions.append({'text': "&New",
                                 'kwargs': {'triggered': self.newfile,
                                            'shortcut': qg.QKeySequence.New,
                                            'icon': icons['new']}})
        self.fileactions.append({'text': "&Open...",
                                 'kwargs': {'triggered': self.open,
                                            'shortcut': qg.QKeySequence.Open,
                                            'icon': icons['open']}})
        self.fileactions.append({'text': "Import...",
                                 'kwargs': {'triggered': self.solidworksimport,
                                            'icon': icons['import']}})
        self.fileactions.append({'text': "&Save",
                                 'kwargs': {'triggered': self.save,
                                            'shortcut': qg.QKeySequence.Save,
                                            'icon': icons['save']}})
        self.fileactions.append({'text': "Save &As...",
                                 'kwargs': {'triggered': self.saveAs,
                                            'shortcut': qg.QKeySequence.SaveAs,
                                            'icon': icons['saveas']}})
        self.fileactions.append(
            {'text': "Regen ID", 'kwargs': {'triggered': self.regen_id}})

        self.editactions = []
        self.editactions.append({'text': 'Undo',
                                 'kwargs': {'triggered': self.undoredo.undo,
                                            'shortcut': qg.QKeySequence.Undo,
                                            'icon': icons['undo']}})
        self.editactions.append({'text': 'Redo',
                                 'kwargs': {'triggered': self.undoredo.redo,
                                            'shortcut': qg.QKeySequence.Redo,
                                            'icon': icons['redo']}})
        self.editactions.append(None)
        self.editactions.append({'text': 'Cut',
                                 'kwargs': {'triggered': self.cut_to_clipboard,
                                            'shortcut': qg.QKeySequence.Cut}})
        self.editactions.append({'text': 'Copy',
                                 'kwargs': {'triggered': self.copy_to_clipboard,
                                            'shortcut': qg.QKeySequence.Copy}})
        self.editactions.append({'text': 'Paste',
                                 'kwargs': {'triggered': self.paste_from_clipboard,
                                            'shortcut': qg.QKeySequence.Paste}})
        self.editactions.append(
            {'text': 'Array', 'kwargs': {'triggered': self.array}})

        self.viewactions = []

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(True)
            self.act_view_ops = action
        self.viewactions.append({'prepmethod': dummy, 'text': 'Operations', 'kwargs': {
                                'triggered': lambda: self.showhide2(self.optreedock, self.act_view_ops)}})

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(True)
            self.act_view_constraints = action
        self.viewactions.append(
            {
                'prepmethod': dummy,
                'text': 'Constraints',
                'kwargs': {
                    'triggered': lambda: self.showhide2(
                        self.constraintdock,
                        self.act_view_constraints)}})

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(True)
            self.act_view_properties = action
        self.viewactions.append({'prepmethod': dummy, 'text': 'Properties', 'kwargs': {
                                'triggered': lambda: self.showhide2(self.propdock, self.act_view_properties)}})
        self.viewactions.append({'text': 'select',
                                 'kwargs': {'triggered': self.graphicsview.rubberband,
                                            'shortcut': qc.Qt.CTRL + qc.Qt.SHIFT + qc.Qt.Key_S,
                                            'icon': icons['select']}})
        self.viewactions.append({'text': 'pan',
                                 'kwargs': {'triggered': self.graphicsview.scrollhand,
                                            'shortcut': qc.Qt.CTRL + qc.Qt.SHIFT + qc.Qt.Key_P,
                                            'icon': icons['pan']}})
        self.viewactions.append(None)
        self.viewactions.append({'text': 'Zoom Fit',
                                 'kwargs': {'triggered': self.graphicsview.zoomToFit,
                                            'shortcut': qc.Qt.CTRL + qc.Qt.Key_F}})
        self.viewactions.append({'text': 'Screenshot',
                                 'kwargs': {'triggered': self.scene.screenShot,
                                            'shortcut': qc.Qt.CTRL + qc.Qt.Key_R}})

        self.drawingactions = []
        self.drawingactions.append({'text': 'point',
                                    'kwargs': {'triggered': self.adddrawingpoint,
                                               'icon': icons['points']}})
        self.drawingactions.append({'text': 'line', 'kwargs': {
                                   'triggered': lambda: self.addproto(ProtoLine), 'icon': icons['line']}})
        self.drawingactions.append({'text': 'polyline', 'kwargs': {
                                   'triggered': lambda: self.addproto(ProtoPath), 'icon': icons['polyline']}})
        self.drawingactions.append({'text': 'rect', 'kwargs': {
                                   'triggered': lambda: self.addproto(ProtoRect2Point), 'icon': icons['rectangle']}})
        self.drawingactions.append({'text': 'circle', 'kwargs': {
                                   'triggered': lambda: self.addproto(ProtoCircle), 'icon': icons['circle']}})
        self.drawingactions.append({'text': 'poly', 'kwargs': {
                                   'triggered': lambda: self.addproto(ProtoPoly), 'icon': icons['polygon']}})
        self.drawingactions.append({'text': 'text', 'kwargs': {
                                   'triggered': lambda: self.addproto(TextParent), 'icon': icons['text']}})

        self.tools = []
#        self.drawingactions.append(None)
        self.tools.append({'text': 'convex hull','kwargs': {'triggered': self.convex_hull,'icon': icons['convex_hull']}})
        self.tools.append({'text': 'triangulate','kwargs': {'triggered': self.triangulate,'icon': icons['triangulate']}})
        self.tools.append({'text': 'shared edges','kwargs': {'triggered': self.getjoints,'icon': icons['getjoints2']}})
        self.tools.append({'text': 'flip direction', 'kwargs': {'triggered': self.flipdirection}})
        self.tools.append({'text': 'hollow', 'kwargs': {'triggered': self.hollow}})
        self.tools.append({'text': 'fill', 'kwargs': {'triggered': self.fill}})
        self.tools.append({'text': 'Construction', 'kwargs': {'triggered': lambda: self.set_construction(True)}})
        self.tools.append({'text': 'Not Construction', 'kwargs': {'triggered': lambda: self.set_construction(False)}})

        distanceactions = []
        distanceactions.append(
            {
                'text': 'Coincident',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.coincident),
                    'icon': icons['coincident']}})
        distanceactions.append(
            {
                'text': 'Distance',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.distance),
                    'icon': icons['distance']}})
        distanceactions.append(
            {
                'text': 'DistanceX',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.distancex),
                    'icon': icons['distancex']}})
        distanceactions.append(
            {
                'text': 'DistanceY',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.distancey),
                    'icon': icons['distancey']}})
        distanceactions.append({'text': 'Fixed', 'kwargs': {
                               'triggered': lambda: self.add_constraint(constraints.fixed)}})

        twolineactions = []
        twolineactions.append(
            {
                'text': 'Angle',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.angle),
                    'icon': icons['angle']}})
        twolineactions.append(
            {
                'text': 'Parallel',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.parallel),
                    'icon': icons['parallel']}})
        twolineactions.append(
            {
                'text': 'Perpendicular',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.perpendicular),
                    'icon': icons['perpendicular']}})
        twolineactions.append(
            {
                'text': 'Equal',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.equal),
                    'icon': icons['equal']}})
        twolineactions.append(
            {
                'text': 'Horizontal',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.horizontal),
                    'icon': icons['horizontal']}})
        twolineactions.append(
            {
                'text': 'Vertical',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.vertical),
                    'icon': icons['vertical']}})

        self.constraintactions = []

        def dummy(action):
            action.setCheckable(True)
            action.setChecked(False)
            self.act_view_vertices = action

        self.constraintactions.append(
            {
                'prepmethod': dummy,
                'text': 'Constraints On',
                'kwargs': {
                    'triggered': self.showvertices,
                    'icon': icons['showconstraints']}})
        self.constraintactions.append(None)
        self.constraintactions.append(
            {'text': 'Distance', 'submenu': distanceactions, 'kwargs': {'icon': icons['distance']}})
        self.constraintactions.append(
            {'text': 'Lines', 'submenu': twolineactions, 'kwargs': {'icon': icons['parallel']}})
        self.constraintactions.append(
            {
                'text': 'PointLine',
                'kwargs': {
                    'triggered': lambda: self.add_constraint(
                        constraints.PointLine),
                    'icon': icons['pointline']}})
        self.constraintactions.append({'text': 'Midpoint', 'kwargs': {
                                      'triggered': lambda: self.add_constraint(constraints.LineMidpoint)}})
        self.constraintactions.append({'text': 'Update', 'kwargs': {
                                      'triggered': self.refreshconstraints, 'icon': icons['refresh']}})
        self.constraintactions.append({'text': 'Cleanup', 'kwargs': {
                                      'triggered': self.cleanupconstraints, 'icon': icons['broom']}})

        self.menu_file = self.addMenu(self.fileactions, name='File')
        self.menu_edit = self.addMenu(self.editactions, name='Edit')
        self.toolbar_drawing, self.menu_drawing = self.addToolbarMenu(
            self.drawingactions, name='Drawing')
        self.toolbar_tools, self.menu_tools = self.addToolbarMenu(
            self.tools, name='Drawing')
        self.toolbar_constraints, self.menu_constraints = self.addToolbarMenu(
            self.constraintactions, name='Constraints')
        self.menu_view = self.addMenu(self.viewactions, name='View')

    def cut_to_clipboard(self):
        self.undoredo.savesnapshot()
        self.scene.cut_to_clipboard()

    def copy_to_clipboard(self):
        self.undoredo.savesnapshot()
        self.scene.copy_to_clipboard()

    def paste_from_clipboard(self):
        self.undoredo.savesnapshot()
        self.scene.paste_from_clipboard()

    def add_constraint(self, constraintclass):
        from popupcad.filetypes.genericshapes import GenericLine
        self.undoredo.savesnapshot()
        items = []
        new_constraints = []

        for item in self.scene.selectedItems():
            if isinstance(item, ReferenceInteractiveVertex):
                generic = item.get_generic()
                newgeneric = DrawnPoint(generic.getpos(),construction = True)
                newitem = newgeneric.gen_interactive()
                self.scene.addItem(newitem)
                items.append(newgeneric)
                item.setSelected(False)
                newitem.setSelected(True)
                new_constraints.append(constraints.fixed.new(newgeneric))

            elif isinstance(item, ReferenceInteractiveEdge):
                generic = item.get_generic()
                v1 = ShapeVertex(generic.vertex1.getpos())
                v2 = ShapeVertex(generic.vertex2.getpos())
                new_constraints.append(constraints.fixed.new(v1, v2))

                l = GenericLine([v1, v2], [], construction=True)

                a = l.outputinteractive()
                self.scene.addItem(a)

                item.setSelected(False)
                a.setSelected(True)
                items.append(a.selectableedges[0].get_generic())

            elif isinstance(item, InteractiveVertex):
                items.append(item.get_generic())
            elif isinstance(item, InteractiveEdge):
                items.append(item.get_generic())
            elif isinstance(item, DrawingPoint):
                items.append(item.get_generic())

        new_constraint = constraintclass.new(*items)
        if new_constraint is not None:
            new_constraints.append(new_constraint)
            for constraint in new_constraints:
                self.sketch.constraintsystem.add_constraint(constraint)
            self.refreshconstraints()

    def constraint_deleted(self):
        self.refreshconstraints()

    def refreshconstraints(self):
        self.sketch.constraintsystem.regenerate()
        self.sketch.constraintsystem.update()
        self.scene.updateshape()
        self.constraint_editor.refresh()

    def update_constraints(self,vertices):
        self.sketch.constraintsystem.update()
        self.scene.updateshape()
        self.constraint_editor.refresh()

    def update_selective(self,vertices):
        self.sketch.constraintsystem.update_selective(vertices)
        self.scene.updateshape()
        self.constraint_editor.refresh()

    def get_sketch_vertices(self):
        self.update_sketch_geometries()
        vertices = [vertex for geom in self.sketch.operationgeometry for vertex in geom.vertices()]
        return vertices

    def cleanupconstraints(self):
        self.sketch.constraintsystem.cleanup()
        self.constraint_editor.refresh()
        self.sketch.constraintsystem.regenerate()

    def showconstraint_item(self, obj1):
        self.showprop.emit(obj1.customdata)
        self.scene.clearSelection()
        vertices = [
            item for item in self.scene.items() if isinstance(
                item,
                InteractiveVertexBase)]
        for v in vertices:
            if v.get_generic().id in obj1.customdata.vertex_ids:
                v.setSelected(True)
        pass
        edges = [
            item for item in self.scene.items() if isinstance(
                item,
                InteractiveEdge) or isinstance(
                item,
                ReferenceInteractiveEdge)]
        for edge in edges:
            c = tuple(sorted([item.id for item in edge.generic.vertices()]))
            if c in obj1.customdata.segment_ids:
                edge.setSelected(True)

    def loadsketch(self, sketch):
        self.sketch = sketch.copy()
        self.scene.deleteall()
        self.scene.sketch = self.sketch

        for item in self.sketch.operationgeometry:
            newitem = item.outputinteractive()
            self.scene.addItem(newitem)
            newitem.refreshview()

        self.constraint_editor.linklist(
            self.sketch.constraintsystem.constraints)
        self.sketch.constraintsystem.get_vertices = self.get_sketch_vertices
        self.load_references()
        self.update_window_title()
        

    def showvertices(self):
        if self.act_view_vertices.isChecked():
            self.scene.cancelcreate()
        self.scene.showvertices(self.act_view_vertices.isChecked())
        self.scene.updatevertices()

    def update_sketch_geometries(self):
        self.sketch.cleargeometries()
        geometries = [
            item.generic for item in self.scene.items() if isinstance(
                item,
                Interactive) if item.generic.isValid()]
        geometries.extend(
            [item.generic for item in self.scene.items() if isinstance(item, DrawingPoint)])
        geometries.extend(
            [item.generic for item in self.scene.items() if isinstance(item, TextParent)])
        self.sketch.addoperationgeometries(geometries)

    def get_current_sketch(self):
        self.update_sketch_geometries()
        return self.sketch

    def newfile(self):
        sketch = popupcad.filetypes.sketch.Sketch()
        self.loadsketch(sketch)
        self.undoredo.restartundoqueue()

    def solidworksimport(self):
        from popupcad.filetypes.solidworksimport import Assembly
        a = Assembly.open()
        sketch = a.build_face_sketch()
        self.loadsketch(sketch)
        self.undoredo.restartundoqueue()

    def open(self):
        sketch = popupcad.filetypes.sketch.Sketch.open()
        if not sketch is None:
            self.loadsketch(sketch)
            self.undoredo.restartundoqueue()

    def save(self):
        self.update_sketch_geometries()
        self.sketch.save()
        self.update_window_title()

    def saveAs(self):
        self.update_sketch_geometries()
        self.sketch.saveAs()
        self.update_window_title()

    def adddrawingpoint(self):
        self.graphicsview.turn_off_drag()
        self.scene.addpolygon(DrawingPoint)

    def addproto(self, proto):
        self.graphicsview.turn_off_drag()
        self.scene.addpolygon(proto)

    def convex_hull(self):
        from popupcad.graphics2d.interactivevertexbase import InteractiveVertexBase
        from popupcad.graphics2d.interactiveedge import InteractiveEdge

        selecteditems = self.scene.selectedItems()
        genericvertices = []
        for item in selecteditems:
            if isinstance(item, InteractiveVertexBase):
                genericvertices.append(item.get_generic())
            elif isinstance(item, InteractiveEdge):
                genericvertices.extend(item.get_generic().vertices())
        vertices2 = [vertex.getpos() for vertex in genericvertices]
        vertices2 = numpy.array(vertices2)
        poly = popupcad.algorithms.triangulate.convex_hull(vertices2)
        self.scene.addItem(poly.outputinteractive())

    def triangulate(self):
        from popupcad.graphics2d.interactivevertexbase import InteractiveVertexBase
        from popupcad.graphics2d.interactiveedge import InteractiveEdge

        selecteditems = self.scene.selectedItems()
        genericvertices = []
        for item in selecteditems:
            if isinstance(item, InteractiveVertexBase):
                genericvertices.append(item.get_generic())
            elif isinstance(item, InteractiveEdge):
                genericvertices.extend(item.get_generic().vertices())
        vertices2 = [vertex.getpos() for vertex in genericvertices]
        polys = popupcad.algorithms.triangulate.triangulate(vertices2)
        [self.scene.addItem(poly.outputinteractive()) for poly in polys]

    def getjoints(self):
        items = []
        for item in self.scene.items():
            if isinstance(item, Interactive):
                items.append(item.generic)
                item.removefromscene()

        roundvalue = 3
                
        genericlines = popupcad.algorithms.getjoints.getjoints(items,roundvalue)
        interactive_lines = [segment.outputinteractive() for segment in genericlines]

        [self.scene.addItem(line) for line in interactive_lines]

    def showconstraint(self, row):
        item = self.constraint_editor.item(row)
        self.showconstraint_item(item)

    def accept(self):
        if self.accept_method is not None:
            self.accept_method(*self.acceptdata())
        self.close()

    def reject(self):
        self.close()

    def loadpropwindow(self, obj):
        widget = obj.properties()
        self.propdock.setWidget(widget)

    def acceptdata(self):
        self.update_sketch_geometries()
        return self.sketch,

    def load_references3(self, ii, jj):
        staticgeometries, controlpoints, controllines = [], [], []
        ii -= 1
        if ii >= 0:
            if self.design is not None:
                print(ii, jj)
                try:
                    operationgeometries = self.design.operations[
                        ii].output[jj].controlpolygons()
                    staticgeometries = [item.outputstatic()
                                        for item in operationgeometries]

                    controlpoints = self.design.operations[
                        ii].output[jj].controlpoints()
                    controlpoints = [point.gen_interactive()
                                     for point in controlpoints]

                    controllines = self.design.operations[
                        ii].output[jj].controllines()
                    controllines = [line.gen_interactive()
                                    for line in controllines]
                except (IndexError, AttributeError):
                    pass
        return staticgeometries, controlpoints, controllines

    def load_references_inner(self, ii, jj):
        self.scene.removerefgeoms()
        self.static_items, self.controlpoints, self.controllines = self.load_references3(
            ii, jj)
        self.scene.update_extra_objects(self.controlpoints + self.controllines)
        self.scene.updatevertices()
        [self.scene.addItem(item) for item in self.static_items]

    def load_references(self):
        if self.selectops:
            selected_indeces = self.optree.currentIndeces2()
            if len(selected_indeces) > 0:
                ii, jj = selected_indeces[0]
                self.load_references_inner(ii, jj)

    def flipdirection(self):
        selecteditems = self.scene.selectedItems()
        for item in selecteditems:
            item.generic.flip()
            item.updateshape()

    def hollow(self):
        selecteditems = self.scene.selectedItems()
        newgenerics = []
        for item in selecteditems:
            newgenerics.extend(item.generic.hollow())
            item.harddelete()
        for item in newgenerics:
            self.scene.addItem(item.outputinteractive())

    def fill(self):
        selecteditems = self.scene.selectedItems()
        newgenerics = []
        for item in selecteditems:
            newgenerics.extend(item.generic.fill())
            item.harddelete()
        for item in newgenerics:
            self.scene.addItem(item.outputinteractive())

    def array(self):
        dialog = qg.QDialog()
        x_num = qg.QSpinBox()
        x_num.setValue(2)
        x_num.setMinimum(1)

        x_val = qg.QDoubleSpinBox()
        x_val.setMinimum(-100000)
        x_val.setMaximum(100000)
        x_val.setValue(1)

        y_num = qg.QSpinBox()
        y_num.setValue(1)
        y_num.setMinimum(1)

        y_val = qg.QDoubleSpinBox()
        y_val.setValue(1)
        y_val.setMinimum(-100000)
        y_val.setMaximum(100000)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')
        sublayout1 = qg.QHBoxLayout()
        sublayout1.addWidget(button_ok)
        sublayout1.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('# in x'))
        layout.addWidget(x_num)
        layout.addWidget(qg.QLabel('x spacing'))
        layout.addWidget(x_val)
        layout.addWidget(qg.QLabel('# in y'))
        layout.addWidget(y_num)
        layout.addWidget(qg.QLabel('y spacing'))
        layout.addWidget(y_val)
        layout.addLayout(sublayout1)

        dialog.setLayout(layout)
        button_ok.clicked.connect(dialog.accept)
        button_cancel.clicked.connect(dialog.reject)
        copies = []
        if dialog.exec_():
            for ii in range(x_num.value()):
                for jj in range(y_num.value()):
                    if ii == jj == 0:
                        pass
                    else:
                        for item in self.scene.selectedItems():
                            shift_val = (
                                ii *
                                x_val.value(),
                                jj *
                                y_val.value())
                            new = item.generic.copy(identical = False)
                            new.shift(shift_val)
                            copies.append(new)
        copies = [
            self.scene.addItem(
                item.outputinteractive()) for item in copies]

    def set_construction(self,value):
        for item in self.scene.selectedItems():
            try:
                item.generic.set_construction(value)
            except AttributeError:
                pass

    def update_window_title(self):
        basename = self.sketch.get_basename()
        self.setWindowTitle('Editor'+' - '+basename)

if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    mw = Sketcher(None, Sketch())
    mw.show()
    sys.exit(app.exec_())