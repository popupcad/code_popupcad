# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import sys

import qt.QtCore as qc
import qt.QtGui as qg
import popupcad
import numpy

import popupcad.constraints.constraints as constraints

from popupcad.geometry.vertex import ShapeVertex, DrawnPoint
from popupcad.graphics2d.interactivevertex import InteractiveVertex, ReferenceInteractiveVertex, DrawingPoint, InteractiveVertexBase
from popupcad.graphics2d.interactiveedge import InteractiveEdge, ReferenceInteractiveEdge
from popupcad.graphics2d.interactive import Interactive
from popupcad.graphics2d.proto import ProtoLine, ProtoPath, ProtoCircle, ProtoPoly, ProtoRect2Point
from popupcad.graphics2d.graphicsscene import GraphicsScene
from popupcad.graphics2d.graphicsview import GraphicsView
from popupcad.filetypes.sketch import Sketch
from popupcad.widgets.listeditor import ListEditor
from popupcad.widgets.widgetcommon import MainGui
from popupcad.filetypes.undoredo import UndoRedo
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.manufacturing.nulloperation import NullOp
from popupcad.graphics2d.text import TextParent

class Sketcher(MainGui,qg.QMainWindow):
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
        self.create_menu_system(popupcad.supportfiledir+'/sketcher_menu.yaml')
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

#        self.set_nominal_size()

        if self.selectops:
            self.optreedock.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_operations'])
        self.constraintdock.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_constraints'])
        self.propdock.closeEvent = lambda event: self.action_uncheck(self.menu_system.actions['view_properties'])

#        self.move_center()
    def regen_id(self):
        self.sketch.regen_id()

    def editItem(self, constraint):
        self.undoredo.savesnapshot()
        constraint.edit()
        self.refreshconstraints()

    def cut_to_clipboard(self):
        self.undoredo.savesnapshot()
        self.scene.cut_to_clipboard()

    def copy_to_clipboard(self):
#        self.undoredo.savesnapshot()
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
                new_constraints.append(constraints.FixedConstraint.new(newgeneric))

            elif isinstance(item, ReferenceInteractiveEdge):
                generic = item.get_generic()
                v1 = ShapeVertex(generic.vertex1.getpos())
                v2 = ShapeVertex(generic.vertex2.getpos())
                new_constraints.append(constraints.FixedConstraint.new(v1, v2))

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
        self.sketch.constraintsystem.cleanup()
        del self.sketch.constraintsystem.generator
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
        del self.sketch.constraintsystem.generator

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

        self.constraint_editor.linklist(self.sketch.constraintsystem.constraints)
        self.sketch.constraintsystem.get_vertices = self.get_sketch_vertices
        self.load_references()
        self.update_window_title()
        

    def showvertices(self):
        if self.menu_system.actions['constraints_show'].isChecked():
            self.scene.cancelcreate()
        self.scene.showvertices(self.menu_system.actions['constraints_show'].isChecked())
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
        sketch = popupcad.filetypes.sketch.Sketch.new()
        self.loadsketch(sketch)
        self.undoredo.restartundoqueue()

    def solidworksimport(self):
        from popupcad.filetypes.solidworksimport import Assembly
        a = Assembly.open()
        if a is not None:
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
    def add_line(self):
        self.addproto(ProtoLine)
    def add_path(self):
        self.addproto(ProtoPath)
    def add_rect(self):
        self.addproto(ProtoRect2Point)
    def add_circle(self):
        self.addproto(ProtoCircle)
    def add_poly(self):
        self.addproto(ProtoPoly)
    def add_text(self):
        self.addproto(TextParent)
        
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
                    operationgeometries = self.design.operations[ii].output[jj].controlpolygons()
                    staticgeometries = [item.outputstatic() for item in operationgeometries]

                    controlpoints = self.design.operations[ii].output[jj].controlpoints()
                    controlpoints = [point.gen_interactive() for point in controlpoints]

                    controllines = self.design.operations[ii].output[jj].controllines()
                    controllines = [line.gen_interactive() for line in controllines]
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

    def extract(self):
        if self.selectops:
            selected_indeces = self.optree.currentIndeces2()
            if len(selected_indeces) > 0:
                ii, jj = selected_indeces[0]
#                self.load_references_inner(ii, jj)

                self.scene.removerefgeoms()

                staticgeometries=[]
                ii -= 1
                if ii >= 0:
                    if self.design is not None:
                        print(ii, jj)
                        try:
                            operationgeometries = self.design.operations[ii].output[jj].controlpolygons()
                            staticgeometries = [item.copy().outputinteractive() for item in operationgeometries]
        
                        except (IndexError, AttributeError):
                            pass

                [self.scene.addItem(item) for item in staticgeometries]
                
    def array(self):
        dialog = qg.QDialog()
        x_num = qg.QSpinBox()
        x_num.setValue(2)
        x_num.setMinimum(1)

        x_val = qg.QDoubleSpinBox()
        x_val.setMinimum(popupcad.gui_negative_infinity)
        x_val.setMaximum(popupcad.gui_positive_infinity)
        x_val.setValue(1)

        y_num = qg.QSpinBox()
        y_num.setValue(1)
        y_num.setMinimum(1)

        y_val = qg.QDoubleSpinBox()
        y_val.setValue(1)
        y_val.setMinimum(popupcad.gui_negative_infinity)
        y_val.setMaximum(popupcad.gui_positive_infinity)

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

    def set_construction_on(self):
        self.set_construction(True)

    def set_construction_off(self):
        self.set_construction(False)

    def update_window_title(self):
        basename = self.sketch.get_basename()
        self.setWindowTitle('Sketcher'+' - '+basename)
    
    def undo(self):
        self.undoredo.undo()
    def redo(self):
        self.undoredo.redo()
    def show_hide_op_tree(self):
        self.showhide2(self.optreedock, self.menu_system.actions['view_operations'])
    def show_hide_constraints(self):
        self.showhide2(self.optreedock, self.menu_system.actions['view_constraints'])
    def show_hide_properties(self):
        self.showhide2(self.optreedock, self.menu_system.actions['view_properties'])
    def rubberband(self):
        self.graphicsview.rubberband()
    def scrollhand(self):
        self.graphicsview.scrollhand()
    def zoomToFit(self):
        self.graphicsview.zoomToFit()
    def screenShot(self):
        self.scene.screenShot()
    def add_constraint_coincident(self):
        self.add_constraint(constraints.CoincidentConstraint)
    def add_constraint_distance(self):
        self.add_constraint(constraints.DistanceConstraint)
    def add_constraint_x_distance(self):
        self.add_constraint(constraints.XDistanceConstraint)
    def add_constraint_y_distance(self):
        self.add_constraint(constraints.YDistanceConstraint)
    def add_constraint_fixed(self):
        self.add_constraint(constraints.FixedConstraint)
    def add_constraint_angle(self):
        self.add_constraint(constraints.AngleConstraint)
    def add_constraint_parallel(self):
        self.add_constraint(constraints.ParallelLinesConstraint)
    def add_constraint_perpendicular(self):
        self.add_constraint(constraints.PerpendicularLinesConstraint)
    def add_constraint_equal(self):
        self.add_constraint(constraints.EqualLengthLinesConstraint)
    def add_constraint_horizontal(self):
        self.add_constraint(constraints.HorizontalConstraint)
    def add_constraint_vertical(self):
        self.add_constraint(constraints.VerticalConstraint)
    def add_constraint_point_line_distance(self):
        self.add_constraint(constraints.PointLineDistanceConstraint)
    def add_constraint_line_midpoint(self):
        self.add_constraint(constraints.LineMidpointConstraint)
        
        
if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    mw = Sketcher(None, Sketch.new())
    mw.show()
    sys.exit(app.exec_())