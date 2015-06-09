# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.widgets.dragndroptree import DraggableTreeWidget

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.operation2 import Operation2,LayerBasedOperation
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.widgets.table_editor import Table,SingleItemListElement,MultiItemListElement,FloatElement,Row

class JointRow(Row):
    def __init__(self,get_sketches,get_layers):
        elements = []
        elements.append(SingleItemListElement('joint sketch',get_sketches))
        elements.append(SingleItemListElement('joint layer',get_layers))
        elements.append(MultiItemListElement('sublaminate layers',get_layers))
        elements.append(FloatElement('hinge width'))
        elements.append(FloatElement('stiffness'))
        elements.append(FloatElement('damping'))
        elements.append(FloatElement('preload'))
        self.elements = elements
        
class JointDef(object):
    def __init__(self,sketch,joint_layer,sublaminate_layers,width,stiffness,damping,preload_angle):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width
        self.stiffness = stiffness
        self.damping = damping
        self.preload_angle = preload_angle
    def copy(self):
        new = type(self)(self.sketch,self.joint_layer,self.sublaminate_layers,self.width,self.stiffness,self.damping,self.preload_angle)
        return new

class MainWidget(qg.QDialog):
    def __init__(self,design,sketches,layers,operations,jointop=None):
        super(MainWidget,self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations
        
        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.fixed = DraggableTreeWidget()
        self.fixed.linklist(self.operations)
        
        self.table= Table(JointRow(self.get_sketches,self.get_layers))

        button_add = qg.QPushButton('Add')
        button_remove = qg.QPushButton('Remove')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.pressed.connect(self.table.row_add_empty)
        button_remove.pressed.connect(self.table.row_remove)
        button_up.pressed.connect(self.table.row_shift_up)
        button_down.pressed.connect(self.table.row_shift_down)

        sublayout1 = qg.QHBoxLayout()
        sublayout1.addWidget(button_add)
        sublayout1.addWidget(button_remove)
        sublayout1.addStretch()
        sublayout1.addWidget(button_up)
        sublayout1.addWidget(button_down)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.pressed.connect(self.accept)        
        button_cancel.pressed.connect(self.reject)        

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.operation_list)
        layout.addWidget(qg.QLabel('Fixed Region'))
        layout.addWidget(self.fixed)
        layout.addWidget(self.table)
        layout.addLayout(sublayout1)
        layout.addLayout(sublayout2)
        self.setLayout(layout)

        if jointop!=None:
            try:
                op_ref,output_ii = jointop.operation_links['parent'][0]
                op_ii = design.operation_index(op_ref)
                self.operation_list.selectIndeces([(op_ii,output_ii)])
            except(IndexError,KeyError):
                pass

            try:
                fixed_ref,fixed_output_ii = jointop.operation_links['fixed'][0]
                fixed_ii = design.operation_index(fixed_ref)
                self.fixed.selectIndeces([(fixed_ii,fixed_output_ii)])
            except(IndexError,KeyError):
                pass

            for item in jointop.joint_defs:
                sketch = self.design.sketches[item.sketch]
                joint_layer = self.design.return_layer_definition().getlayer(item.joint_layer)
                sublaminate_layers = [self.design.return_layer_definition().getlayer(item2) for item2 in item.sublaminate_layers]
                self.table.row_add(sketch,joint_layer,sublaminate_layers,item.width,item.stiffness,item.damping,item.preload_angle)
        else:
            self.table.row_add_empty()

    def get_sketches(self):
        return self.sketches
    
    def get_layers(self):
        return self.layers
            
    def acceptdata(self):
        jointdefs = []
        for ii in range(self.table.rowCount()):
            sketch = self.table.item(ii,0).data(qc.Qt.ItemDataRole.UserRole)
            joint_layer = self.table.item(ii,1).data(qc.Qt.ItemDataRole.UserRole)
            sublaminate_layers = self.table.item(ii,2).data(qc.Qt.ItemDataRole.UserRole)
            width = (self.table.item(ii,3).data(qc.Qt.ItemDataRole.UserRole))
            stiffness = (self.table.item(ii,4).data(qc.Qt.ItemDataRole.UserRole))
            damping = (self.table.item(ii,5).data(qc.Qt.ItemDataRole.UserRole))
            preload_angle = (self.table.item(ii,6).data(qc.Qt.ItemDataRole.UserRole))
            jointdefs.append(JointDef(sketch.id,joint_layer.id,[item.id for item in sublaminate_layers],width,stiffness,damping,preload_angle))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        operation_links['fixed'] = self.fixed.currentRefs()
        return operation_links,jointdefs

class JointOperation2(Operation2,LayerBasedOperation):
    name = 'Joint Definition'
    resolution = 2
    
    name = 'Joint Operation'
    def copy(self):
        new = type(self)(self.operation_links,[item.copy() for item in self.joint_defs])
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(JointOperation2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,operation_links,joint_defs):  
        self.operation_links = operation_links
        self.joint_defs = joint_defs
        self.clear_output()

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.prioroperations(self),self)
        return dialog

    def sketchrefs(self):
        return [item.sketch for item in self.joint_defs]
    
    def subdesignrefs(self):
        return []
    
    
    def gen_geoms(self,joint_def,layerdef,design):
        hinge_gap = joint_def.width*popupcad.internal_argument_scaling
        split_buffer = .1*hinge_gap

        stiffness = joint_def.stiffness
        damping = joint_def.damping
        preload_angle = joint_def.preload_angle

        sublaminate_layers = [layerdef.getlayer(item) for item in joint_def.sublaminate_layers]
        hingelayer = layerdef.getlayer(joint_def.joint_layer)        

        operationgeom = design.sketches[joint_def.sketch].output_csg()
        sketch_result = Laminate(design.return_layer_definition())
        sketch_result.replacelayergeoms(hingelayer,operationgeom)
        hingelines = sketch_result.to_generic_laminate().geoms[hingelayer]

        buffered_split= sketch_result.buffer(split_buffer,resolution = self.resolution)

        allgeoms4 = []
        for geom in hingelines:
            geom = geom.outputshapely()
            laminate = Laminate(layerdef)
            for layer in sublaminate_layers:
                laminate.replacelayergeoms(layer,[geom])
            allgeoms4.append(laminate.buffer(hinge_gap,resolution = self.resolution))
            
        joint_props = [(stiffness,damping,preload_angle) for item in hingelines]
        return allgeoms4, buffered_split,hingelines,joint_props
        
    def generate(self,design):
        safe_buffer1 = .5*popupcad.internal_argument_scaling
        safe_buffer2 = .5*popupcad.internal_argument_scaling
        safe_buffer3 = .5*popupcad.internal_argument_scaling
        
        parent_id,parent_output_index = self.operation_links['parent'][0]
        parent_index = design.operation_index(parent_id)
        parent = design.operations[parent_index].output[parent_output_index].csg

        fixed_id,fixed_output_index = self.operation_links['fixed'][0]
        fixed_index = design.operation_index(fixed_id)
        fixed = design.operations[fixed_index].output[fixed_output_index].csg

        
        layerdef = design.return_layer_definition()

        allgeoms = []
        allhingelines = []
        buffered_splits = []
        all_joint_props = []
        for joint_def in self.joint_defs:
            allgeoms4,buffered_split,hingelines,joint_props= self.gen_geoms(joint_def,layerdef,design)
            allgeoms.extend(allgeoms4)
            allhingelines.extend(hingelines)
            buffered_splits.append(buffered_split)
            all_joint_props.extend(joint_props)
            
        safe_sections = []
        for ii in range(len(allgeoms)):
            unsafe = Laminate.unaryoperation(allgeoms[:ii]+allgeoms[ii+1:],'union')
            unsafe_buffer = unsafe.buffer(safe_buffer1,resolution = self.resolution)
            safe_sections.append(allgeoms[ii].difference(unsafe_buffer))
            
        safe = Laminate.unaryoperation(safe_sections,'union')
        buffered_splits2 = Laminate.unaryoperation(buffered_splits,'union')
        safe_buffer = safe.buffer(safe_buffer2,resolution = self.resolution)
        unsafe = Laminate.unaryoperation(allgeoms,'union').difference(safe_buffer)
        unsafe2 = unsafe.buffer(safe_buffer3,resolution = self.resolution)
        
        split1 = parent.difference(unsafe2)
        split2 = split1.difference(buffered_splits2)
        bodies= popupcad.algorithms.body_detection.find(split2.to_generic_laminate())

        bodies_generic = [item.to_generic_laminate() for item in bodies]
        
        connections = {}
        connections2 = {}
        
        for line,geom in zip(allhingelines,safe_sections):
            connections[line]=[]
            connections2[line]=[]
            for body,body_generic in zip(bodies,bodies_generic):
                if not geom.intersection(body).isEmpty():
                    connections[line].append(body_generic)
                    connections2[line].append(body)
        for line,geoms in connections2.items():
            connections2[line]=Laminate.unaryoperation(geoms,'union')

        self.fixed_bodies = []
        for body,body_generic in zip(bodies,bodies_generic):
            if not fixed.intersection(body).isEmpty():
                self.fixed_bodies.append(body_generic)
                    
        self.bodies_generic = bodies_generic                    
        self.connections = [(key,connections[key]) for key in allhingelines]
        self.all_joint_props = all_joint_props
        
        laminates = [safe,unsafe2,split1,split2]+bodies+list(connections2.values())
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])

    def switch_layer_defs(self,layerdef_old,layerdef_new):
        new = self.copy()
        for joint_def in new.joint_defs:
            joint_def.joint_layer = new.convert_layer_links([joint_def.joint_layer],layerdef_old,layerdef_new)[0]
            joint_def.sublaminate_layers = new.convert_layer_links([joint_def.sublaminate_layers],layerdef_old,layerdef_new)[0]
        return new
