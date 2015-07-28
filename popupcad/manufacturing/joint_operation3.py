from __future__ import print_function #Fixes crossplatform print issues
# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.widgets.dragndroptree import DraggableTreeWidget

import PySide.QtGui as qg
import PySide.QtCore as qc

import popupcad
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.operation2 import Operation2, LayerBasedOperation
from popupcad.filetypes.laminate import Laminate
from popupcad.widgets.table_editor_popup import Table,SingleItemListElement_old, MultiItemListElement, FloatElement, Row,Delegate,TableControl
from popupcad.widgets.listmanager import SketchListManager

try:
    import itertools.izip as zip
except ImportError:
    pass

class JointRow(Row):

    def __init__(self, get_sketches, get_layers):
        elements = []
        elements.append(SingleItemListElement_old('joint sketch', get_sketches))
        elements.append(SingleItemListElement_old('joint layer', get_layers))
        elements.append(MultiItemListElement('sublaminate layers', get_layers))
        elements.append(FloatElement('hinge width'))
        elements.append(FloatElement('stiffness'))
        elements.append(FloatElement('damping'))
        elements.append(FloatElement('preload'))
        elements.append(FloatElement('limit negative',ini=-180))
        elements.append(FloatElement('limit positive',ini=180))
        self.elements = elements


class JointDef(object):

    def __init__(self,sketch,joint_layer,sublaminate_layers,width,stiffness,damping,preload_angle,limit_negative,limit_positive):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width
        self.stiffness = stiffness
        self.damping = damping
        self.preload_angle = preload_angle
        self.limit_negative = limit_negative
        self.limit_positive = limit_positive

    def copy(self):
        new = type(self)(
            self.sketch,
            self.joint_layer,
            self.sublaminate_layers,
            self.width,
            self.stiffness,
            self.damping,
            self.preload_angle,
            self.limit_negative,
            self.limit_positive)
        return new


class MainWidget(qg.QDialog):

    def __init__(self, design, sketches, layers, operations, jointop=None,sketch = None):
        super(MainWidget, self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations

        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.fixed = DraggableTreeWidget()
        self.fixed.linklist(self.operations)

        self.table = Table(JointRow(self.get_sketches, self.get_layers),Delegate)
        table_control= TableControl(self.table, self)


        self.sketchwidget = SketchListManager(self.design,name='Contact Points Sketch')
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value == sketch:
                item.setSelected(True)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
                
        sublayout1 = qg.QHBoxLayout()
        sublayout1_1 = qg.QVBoxLayout()
        sublayout1_2 = qg.QVBoxLayout()
        sublayout1_3 = qg.QVBoxLayout()

        sublayout1_1.addWidget(qg.QLabel('Device'))
        sublayout1_1.addWidget(self.operation_list)
        sublayout1_2.addWidget(qg.QLabel('Fixed Region'))
        sublayout1_2.addWidget(self.fixed)
        sublayout1_3.addWidget(self.sketchwidget)

        sublayout1.addLayout(sublayout1_1)
        sublayout1.addLayout(sublayout1_2)
        sublayout1.addLayout(sublayout1_3)

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addStretch()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)
        sublayout2.addStretch()

        layout = qg.QVBoxLayout()
        layout.addLayout(sublayout1)
        layout.addWidget(table_control)
        layout.addLayout(sublayout2)
        
        self.setLayout(layout)

        if jointop is not None:
            try:
                op_ref, output_ii = jointop.operation_links['parent'][0]
                op_ii = design.operation_index(op_ref)
                self.operation_list.selectIndeces([(op_ii, output_ii)])
            except(IndexError, KeyError):
                pass

            try:
                fixed_ref, fixed_output_ii = jointop.operation_links[
                    'fixed'][0]
                fixed_ii = design.operation_index(fixed_ref)
                self.fixed.selectIndeces([(fixed_ii, fixed_output_ii)])
            except(IndexError, KeyError):
                pass

            for item in jointop.joint_defs:
                sketch = self.design.sketches[item.sketch]
                joint_layer = self.design.return_layer_definition().getlayer(
                    item.joint_layer)
                sublaminate_layers = [self.design.return_layer_definition().getlayer(
                    item2) for item2 in item.sublaminate_layers]
                self.table.row_add(
                    sketch,
                    joint_layer,
                    sublaminate_layers,
                    item.width,
                    item.stiffness,
                    item.damping,
                    item.preload_angle,
                    item.limit_negative,
                    item.limit_positive)            
        else:
            self.table.row_add_empty()

        self.table.resizeColumnsToContents()
        self.table.reset_min_width()
        self.table.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def contact_sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None


    def get_sketches(self):
        return self.sketches

    def get_layers(self):
        return self.layers

    def acceptdata(self):
        jointdefs = []
        for ii in range(self.table.rowCount()):
            sketch = self.table.item(ii, 0).data(qc.Qt.ItemDataRole.UserRole)
            joint_layer = self.table.item(
                ii, 1).data(
                qc.Qt.ItemDataRole.UserRole)
            sublaminate_layers = self.table.item(
                ii, 2).data(
                qc.Qt.ItemDataRole.UserRole)
            width = (self.table.item(ii, 3).data(qc.Qt.ItemDataRole.UserRole))
            stiffness = (
                self.table.item(
                    ii, 4).data(
                    qc.Qt.ItemDataRole.UserRole))
            damping = (
                self.table.item(
                    ii,
                    5).data(
                    qc.Qt.ItemDataRole.UserRole))
            preload_angle = (self.table.item(ii, 6).data(qc.Qt.ItemDataRole.UserRole))
            limit_negative = (self.table.item(ii, 7).data(qc.Qt.ItemDataRole.UserRole))
            limit_positive = (self.table.item(ii, 8).data(qc.Qt.ItemDataRole.UserRole))
            jointdefs.append(JointDef(sketch.id,
                                      joint_layer.id,
                                      [item.id for item in sublaminate_layers],
                                      width,
                                      stiffness,
                                      damping,
                                      preload_angle,limit_negative,limit_positive))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        operation_links['fixed'] = self.fixed.currentRefs()
        sketch_links = {}
        sketch_links['contact_points'] = [self.contact_sketch().id]
        return operation_links,sketch_links,jointdefs

class JointOperation3(Operation2, LayerBasedOperation):
    name = 'JointOp'
    resolution = 2

    def copy(self):
        new = type(self)(
            self.operation_links, [
                item.copy() for item in self.joint_defs])
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self, *args):
        super(JointOperation3, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, operation_links,sketch_links,joint_defs):
        super(JointOperation3,self).editdata(operation_links,sketch_links,{})
        self.joint_defs = joint_defs

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = MainWidget(
            design,
            design.sketches.values(),
            design.return_layer_definition().layers,
            design.operations)
        return dialog

    def buildeditdialog(self, design):
        sketch = design.sketches[self.sketch_links['contact_points'][0]]
        dialog = MainWidget(
            design,
            design.sketches.values(),
            design.return_layer_definition().layers,
            design.prioroperations(self),
            self,sketch)
        return dialog

    def sketchrefs(self):
        items = super(JointOperation3,self).sketchrefs()
        items.extend([item.sketch for item in self.joint_defs])
        return items

    def gen_geoms(self, joint_def, layerdef, design):
        hinge_gap = joint_def.width *popupcad.csg_processing_scaling
        split_buffer = .1 * hinge_gap

        stiffness = joint_def.stiffness
        damping = joint_def.damping
        preload_angle = joint_def.preload_angle

        sublaminate_layers = [
            layerdef.getlayer(item) for item in joint_def.sublaminate_layers]
        hingelayer = layerdef.getlayer(joint_def.joint_layer)

        operationgeom = design.sketches[joint_def.sketch].output_csg()
        sketch_result = Laminate(design.return_layer_definition())
        sketch_result.replacelayergeoms(hingelayer, operationgeom)
        hingelines = sketch_result.to_generic_laminate().geoms[hingelayer]
        hingelines = [item for item in hingelines if item.is_valid_bool()]

        buffered_split = sketch_result.buffer(
            split_buffer,
            resolution=self.resolution)

        allgeoms4 = []
        for geom in hingelines:
            geom = geom.outputshapely()
            laminate = Laminate(layerdef)
            for layer in sublaminate_layers:
                laminate.replacelayergeoms(layer, [geom])
            allgeoms4.append(
                laminate.buffer(
                    hinge_gap,
                    resolution=self.resolution))

        joint_props = [(stiffness, damping, preload_angle)
                       for item in hingelines]
        return allgeoms4, buffered_split, hingelines, joint_props

    def generate(self, design):
        safe_buffer1 = .5 *popupcad.csg_processing_scaling
        safe_buffer2 = .5 *popupcad.csg_processing_scaling
        safe_buffer3 = .5 *popupcad.csg_processing_scaling

        parent_id, parent_output_index = self.operation_links['parent'][0]
        parent_index = design.operation_index(parent_id)
        parent = design.operations[parent_index].output[
            parent_output_index].csg

        fixed_id, fixed_output_index = self.operation_links['fixed'][0]
        fixed_index = design.operation_index(fixed_id)
        fixed = design.operations[fixed_index].output[fixed_output_index].csg

        layerdef = design.return_layer_definition()

        allgeoms = []
        allhingelines = []
        buffered_splits = []
        all_joint_props = []
        for joint_def in self.joint_defs:
            allgeoms4, buffered_split, hingelines, joint_props = self.gen_geoms(
                joint_def, layerdef, design)
            allgeoms.extend(allgeoms4)
            allhingelines.extend(hingelines)
            buffered_splits.append(buffered_split)
            all_joint_props.extend(joint_props)

        safe_sections = []
        for ii in range(len(allgeoms)):
            unsafe = Laminate.unaryoperation(
                allgeoms[
                    :ii] +
                allgeoms[
                    ii +
                    1:],
                'union')
            unsafe_buffer = unsafe.buffer(
                safe_buffer1,
                resolution=self.resolution)
            safe_sections.append(allgeoms[ii].difference(unsafe_buffer))

        safe = Laminate.unaryoperation(safe_sections, 'union')
        buffered_splits2 = Laminate.unaryoperation(buffered_splits, 'union')
        safe_buffer = safe.buffer(safe_buffer2, resolution=self.resolution)
        unsafe = Laminate.unaryoperation(
            allgeoms,
            'union').difference(safe_buffer)
        unsafe2 = unsafe.buffer(safe_buffer3, resolution=self.resolution)

        split1 = parent.difference(unsafe2)
        split2 = split1.difference(buffered_splits2)
        bodies = popupcad.algorithms.body_detection.find(
            split2.to_generic_laminate())

        bodies_generic = [item.to_generic_laminate() for item in bodies]

        connections = {}
        connections2 = {}

        for line, geom in zip(allhingelines, safe_sections):
            connections[line] = []
            connections2[line] = []
            for body, body_generic in zip(bodies, bodies_generic):
                if not geom.intersection(body).isEmpty():
                    connections[line].append(body_generic)
                    connections2[line].append(body)
        for line, geoms in connections2.items():
            connections2[line] = Laminate.unaryoperation(geoms, 'union')

        self.fixed_bodies = []
        fixed_csg = []
        for body, body_generic in zip(bodies, bodies_generic):
            if not fixed.intersection(body).isEmpty():
                self.fixed_bodies.append(body_generic)
                fixed_csg.append(body)

        self.bodies_generic = bodies_generic
        self.connections = [(key, connections[key]) for key in allhingelines if len(connections[key]) == 2]
        self.all_joint_props = all_joint_props

        self.output = []
        self.output.append(OperationOutput(safe,'Safe',self))        
        self.output.append(OperationOutput(unsafe,'Unafe',self))        
        self.output.append(OperationOutput(split1,'Split1',self))        
        self.output.append(OperationOutput(split2,'Split2',self))        
        self.output.extend([OperationOutput(item,'Fixed {0:d}'.format(ii),self) for ii,item in enumerate(fixed_csg)])        
        self.output.extend([OperationOutput(item,'Body {0:d}'.format(ii),self) for ii,item in enumerate(bodies)])        
        self.output.extend([OperationOutput(item,'Connection {0:d}'.format(ii),self) for ii,item in enumerate(connections2.values())])        
        self.output.insert(0, self.output[3])

    def switch_layer_defs(self, layerdef_old, layerdef_new):
        new = self.copy()
        for joint_def in new.joint_defs:
            joint_def.joint_layer = new.convert_layer_links(
                [joint_def.joint_layer], layerdef_old, layerdef_new)[0]
            joint_def.sublaminate_layers = new.convert_layer_links(
                [joint_def.sublaminate_layers], layerdef_old, layerdef_new)[0]
        return new


    #Returns a key of laminates to generations and assigns the value
    #The original fixed body is generation 0 and all others are children to it.
    def get_laminate_generations(self):
        current_node = self.fixed_bodies[0] #The root of the tree
        joint_pairs = [my_tuple[1] for my_tuple in self.connections]
        hierarchy_map = {}
        generation = 0 #The geneation of the current node
        hierarchy_map[current_node] = generation
        generation += 1
        child_queue = [current_node]
        visited_set = []
        while len(child_queue) > 0:
            current_node = child_queue.pop(0)            
            visited_set.append(current_node)                            
            children_tuples = [joint_pair for joint_pair in joint_pairs if current_node in joint_pair]
            children = [[joint for joint in joint_pair if joint != current_node][0] for joint_pair in children_tuples]
            children = [child for child in children if child not in visited_set]
            for child in children:
                hierarchy_map[child] = generation
            generation += 1
            #Queues up the next batch of children
            child_queue.extend([child for child in children if child not in visited_set])
        return hierarchy_map    
    
    #Generates the XML Tree for the joint
    
        #come back and implement rather stuff
    
