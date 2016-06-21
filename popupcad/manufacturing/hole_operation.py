from __future__ import print_function #Fixes crossplatform print issues
# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
from popupcad.widgets.dragndroptree import DraggableTreeWidget


import qt.QtCore as qc
import qt.QtGui as qg

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
        self.elements = elements


class JointDef(object):

    def __init__(self,sketch,joint_layer,sublaminate_layers,width):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width

    def copy(self):
        new = type(self)(
            self.sketch,
            self.joint_layer,
            self.sublaminate_layers,
            self.width)
        return new


class MainWidget(qg.QDialog):

    def __init__(self, design, sketches, layers, operations, jointop=None,buffer = .01):
        super(MainWidget, self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations

        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.table = Table(JointRow(self.get_sketches, self.get_layers),Delegate)
        table_control= TableControl(self.table, self)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
                
                
        self.buffer_val = qg.QLineEdit()                
                
        sublayout2 = qg.QHBoxLayout()
        sublayout2.addStretch()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)
        sublayout2.addStretch()

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.operation_list)
        layout.addWidget(table_control)
        layout.addWidget(qg.QLabel('Buffer'))
        layout.addWidget(self.buffer_val)
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
                    item.width)            
        else:
            self.table.row_add_empty()
        self.buffer_val.setText(str(buffer))

        self.table.resizeColumnsToContents()
        self.table.reset_min_width()
        self.table.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)

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
            sketch = self.table.item(ii, 0).data(qc.Qt.UserRole)
            joint_layer = self.table.item(
                ii, 1).data(
                qc.Qt.UserRole)
            sublaminate_layers = self.table.item(
                ii, 2).data(
                qc.Qt.UserRole)
            width = (self.table.item(ii, 3).data(qc.Qt.UserRole))
            jointdefs.append(JointDef(sketch.id,joint_layer.id,[item.id for item in sublaminate_layers],width))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        sketch_links = {}
        return operation_links,sketch_links,jointdefs,float(self.buffer_val.text())

class HoleOperation(Operation2, LayerBasedOperation):
    name = 'HoleOp'
    resolution = 2

    def copy(self):
        new = type(self)(self.operation_links, self.sketch_links,[item.copy() for item in self.joint_defs],self.buffer_val)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self, *args):
        super(HoleOperation, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, operation_links,sketch_links,joint_defs,buffer_val):
        super(HoleOperation,self).editdata(operation_links,sketch_links,{})
        self.joint_defs = joint_defs
        self.buffer_val = buffer_val

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = MainWidget(
            design,
            design.sketches.values(),
            design.return_layer_definition().layers,
            design.operations)
        return dialog

    def buildeditdialog(self, design):
        dialog = MainWidget(
            design,
            design.sketches.values(),
            design.return_layer_definition().layers,
            design.prioroperations(self),
            self,self.buffer_val)
        return dialog

    def sketchrefs(self):
        items = super(HoleOperation,self).sketchrefs()
        items.extend([item.sketch for item in self.joint_defs])
        return items

    def gen_geoms(self, joint_def, layerdef, design,split_buffer):
        print('Generating geometry')        
        hinge_gap = joint_def.width *popupcad.csg_processing_scaling
#        split_buffer = .1 * hinge_gap

        sublaminate_layers = [
            layerdef.getlayer(item) for item in joint_def.sublaminate_layers]
        hingelayer = layerdef.getlayer(joint_def.joint_layer)

        operationgeom = design.sketches[joint_def.sketch].output_csg()
        sketch_result = Laminate(design.return_layer_definition())
        sketch_result.replacelayergeoms(hingelayer, operationgeom)
        hingelines = sketch_result.to_generic_laminate().geoms[hingelayer]
        hingelines = [item for item in hingelines if item.is_valid_bool()]

        buffered_split = sketch_result.buffer(split_buffer,resolution=self.resolution)

        allgeoms4 = []
        for geom in hingelines:
            geom = geom.to_shapely()
            laminate = Laminate(layerdef)
            for layer in sublaminate_layers:
                laminate.replacelayergeoms(layer, [geom])
            allgeoms4.append(
                laminate.buffer(hinge_gap,resolution=self.resolution))

        return allgeoms4, buffered_split, hingelines

    def operate(self, design):
        safe_buffer1 = self.buffer_val * popupcad.csg_processing_scaling
        safe_buffer2 = self.buffer_val * popupcad.csg_processing_scaling
        safe_buffer3 = self.buffer_val * popupcad.csg_processing_scaling

        parent_id, parent_output_index = self.operation_links['parent'][0]
        parent_index = design.operation_index(parent_id)
        parent = design.operations[parent_index].output[
            parent_output_index].csg

        layerdef = design.return_layer_definition()

        allgeoms = []
        allhingelines = []
        buffered_splits = []
        for joint_def in self.joint_defs:
            allgeoms4, buffered_split, hingelines = self.gen_geoms(joint_def, layerdef, design,self.buffer_val)
            allgeoms.extend(allgeoms4)
            allhingelines.extend(hingelines)
            buffered_splits.append(buffered_split)
        
        safe_sections = []
        for ii in range(len(allgeoms)):
            unsafe = Laminate.unaryoperation(allgeoms[:ii] +allgeoms[ii +1:],
                'union')
            unsafe_buffer = unsafe.buffer(safe_buffer1,resolution=self.resolution)
            safe_sections.append(allgeoms[ii].difference(unsafe_buffer))

        safe = Laminate.unaryoperation(safe_sections, 'union')
        safe_buffer = safe.buffer(safe_buffer2, resolution=self.resolution)
        unsafe = Laminate.unaryoperation(allgeoms,'union').difference(safe_buffer)
        unsafe2 = unsafe.buffer(safe_buffer3, resolution=self.resolution)
        split1 = parent.difference(unsafe2)
        return split1
#        self.output = []
#        self.output.append(OperationOutput(safe,'Safe',self))        
#        self.output.append(OperationOutput(unsafe,'Unsafe',self))        
#        self.output.append(OperationOutput(split1,'Split1',self))        

    def switch_layer_defs(self, layerdef_old, layerdef_new):
        new = self.copy()
        for joint_def in new.joint_defs:
            joint_def.joint_layer = new.convert_layer_links(
                [joint_def.joint_layer], layerdef_old, layerdef_new)[0]
            joint_def.sublaminate_layers = new.convert_layer_links(
                [joint_def.sublaminate_layers], layerdef_old, layerdef_new)[0]
        return new