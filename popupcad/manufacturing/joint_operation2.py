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
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.operation2 import Operation2, LayerBasedOperation
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.widgets.table_editor import Table, SingleItemListElement, MultiItemListElement, FloatElement, Row
from lxml import etree
import os

try:
    import itertools.izip as zip
except ImportError:
    pass

class JointRow(Row):

    def __init__(self, get_sketches, get_layers):
        elements = []
        elements.append(SingleItemListElement('joint sketch', get_sketches))
        elements.append(SingleItemListElement('joint layer', get_layers))
        elements.append(MultiItemListElement('sublaminate layers', get_layers))
        elements.append(FloatElement('hinge width'))
        elements.append(FloatElement('stiffness'))
        elements.append(FloatElement('damping'))
        elements.append(FloatElement('preload'))
        self.elements = elements


class JointDef(object):

    def __init__(
            self,
            sketch,
            joint_layer,
            sublaminate_layers,
            width,
            stiffness,
            damping,
            preload_angle):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width
        self.stiffness = stiffness
        self.damping = damping
        self.preload_angle = preload_angle

    def copy(self):
        new = type(self)(
            self.sketch,
            self.joint_layer,
            self.sublaminate_layers,
            self.width,
            self.stiffness,
            self.damping,
            self.preload_angle)
        return new


class MainWidget(qg.QDialog):

    def __init__(self, design, sketches, layers, operations, jointop=None):
        super(MainWidget, self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations

        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.fixed = DraggableTreeWidget()
        self.fixed.linklist(self.operations)

        self.table = Table(JointRow(self.get_sketches, self.get_layers))

        button_add = qg.QPushButton('Add')
        button_remove = qg.QPushButton('Remove')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.clicked.connect(self.table.row_add_empty)
        button_remove.clicked.connect(self.table.row_remove)
        button_up.clicked.connect(self.table.row_shift_up)
        button_down.clicked.connect(self.table.row_shift_down)

        sublayout1 = qg.QHBoxLayout()
        sublayout1.addWidget(button_add)
        sublayout1.addWidget(button_remove)
        sublayout1.addStretch()
        sublayout1.addWidget(button_up)
        sublayout1.addWidget(button_down)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
                

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
                    item.preload_angle)            
        else:
            self.table.row_add_empty()

        self.setLayout(layout)



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
            preload_angle = (
                self.table.item(
                    ii, 6).data(
                    qc.Qt.ItemDataRole.UserRole))
            jointdefs.append(JointDef(sketch.id,
                                      joint_layer.id,
                                      [item.id for item in sublaminate_layers],
                                      width,
                                      stiffness,
                                      damping,
                                      preload_angle))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        operation_links['fixed'] = self.fixed.currentRefs()
        return operation_links, jointdefs


class JointOperation2(Operation2, LayerBasedOperation):
    name = 'Joint Definition'
    resolution = 2

    name = 'Joint Operation'

    def copy(self):
        new = type(self)(
            self.operation_links, [
                item.copy() for item in self.joint_defs])
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self, *args):
        super(JointOperation2, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, operation_links, joint_defs):
        self.operation_links = operation_links
        self.joint_defs = joint_defs
        self.clear_output()

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
            self)
        return dialog

    def sketchrefs(self):
        return [item.sketch for item in self.joint_defs]

    def subdesignrefs(self):
        return []

    def gen_geoms(self, joint_def, layerdef, design):
        hinge_gap = joint_def.width * popupcad.internal_argument_scaling
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
        safe_buffer1 = .5 * popupcad.internal_argument_scaling
        safe_buffer2 = .5 * popupcad.internal_argument_scaling
        safe_buffer3 = .5 * popupcad.internal_argument_scaling

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
        for body, body_generic in zip(bodies, bodies_generic):
            if not fixed.intersection(body).isEmpty():
                self.fixed_bodies.append(body_generic)

        self.bodies_generic = bodies_generic
        self.connections = [(key, connections[key]) for key in allhingelines]
        self.all_joint_props = all_joint_props

        laminates = [safe, unsafe2, split1, split2] + bodies + list(connections2.values())
        self.output = []
        for ii, item in enumerate(laminates):
            self.output.append(
                OperationOutput(
                    item,
                    'Body {0:d}'.format(ii),
                    self))
        self.output.insert(0, self.output[0])

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
    def craftJoint(self, connection, counter):
        joint_pair = reorder_pair(connection[1], self.get_laminate_generations())    
        
        joint_root = etree.Element("joint", {"name":"hingejoint" + str(counter), "type":"revolute"})
        etree.SubElement(joint_root, "parent").text = str(joint_pair[0].id)
        etree.SubElement(joint_root, "child").text = str(joint_pair[1].id)
        joint_center = findMidPoint(connection[0], joint_pair[0])
        joint_loc = str(joint_center[0]) + " " + str(joint_center[1]) + " " + str(joint_center[2]) + " 0 0 0"
        etree.SubElement(joint_root, "pose").text = joint_loc   
        axis = etree.SubElement(joint_root, "axis")
        line = unitizeLine(connection[0])    
        etree.SubElement(axis, "xyz").text = str(line[0]) + " " + str(line[1]) + " " + str(0)
        
        #etree.SubElement(axis, "use_parent_model_frame").text = "true"
        limit = etree.SubElement(axis, "limit")
        etree.SubElement(limit, "lower").text = '-3.145159'
        etree.SubElement(limit, "upper").text = '3.14519'
        
        #Add the properties of the joint
        joint_props = self.all_joint_props[self.connections.index(connection)]
        etree.SubElement(limit, "stiffness").text = str(joint_props[0])
        dynamics = etree.SubElement(axis, "dynamics")
        etree.SubElement(dynamics, "damping").text = str(joint_props[1])
        
        return joint_root
        #come back and implement rather stuff
    
    #Export to Gazebo
    def export(self):
        joint_laminates = self.bodies_generic
        for laminate in joint_laminates:
            laminate.toDAE()
       
       
        project_name = "exported" #We can figure out a better way later.
        world_name = 'world'
        robot_name = 'default_body'        
        
        global_root = etree.Element("sdf", version="1.5")
        
        world_object = etree.Element("world", name=world_name)
        global_root.append(world_object);
        
        model_object = etree.Element("model", name=robot_name)
        world_object.append(model_object)
        
        etree.SubElement(model_object, "static").text = "false"
        etree.SubElement(model_object, "pose").text = "0 0 0 0 0 0"
        
        world_object.append(createFloor())
        
        counter = 0
        for joint_laminate in joint_laminates:
            model_object.append(createRobotPart(joint_laminate, counter))
            counter+=1
        
        counter = 0
        for joint_connection in self.connections:
            model_object.append(self.craftJoint(joint_connection, counter))
            counter+=1
        
        #Fixed joint method
        #joint_root = etree.SubElement(model_object, "joint", {'name':'atlas', 'type':'revolute'})
        #etree.SubElement(joint_root, 'parent').text = 'world'
        #etree.SubElement(joint_root, 'child').text = str(self.connections[0][1][0].id)
        #axis = etree.SubElement(joint_root, "axis")
        #etree.SubElement(axis, "xyz").text = "0 1 0"
        #limit = etree.SubElement(axis, "limit")
        #etree.SubElement(limit, "upper").text = '0'
        #etree.SubElement(limit, "lower").text = '0'
        
        #Manually specify the physics engine
        #physics = etree.SubElement(world_object, 'physics', {'name':'default', 'default':'true', 'type':'dart'})
        #etree.SubElement(physics, 'max_step_size').text = str(0.0001)
        #etree.SubElement(physics, "real_time_factor").text = "0.1"
        
        #Saves the object
        file_output = popupcad.exportdir + os.path.sep + project_name + ".world"
        f = open(file_output,"w")
        f.write(etree.tostring(global_root, pretty_print=True))
        f.close()
        
        #TODO replace with Subprocess to prevent pollution of STDOUT
        os.system("gazebo -e dart " + file_output + " &")
        
        
        from gazebo_controller import apply_joint_forces

        joint_names = []        
        for num in range(0, len(self.all_joint_props)):
            joint_names.append("hingejoint" + str(num))
        
        joint_forces = [joint_def[2] for joint_def in self.all_joint_props]
        apply_joint_forces(world_name, robot_name, joint_names, joint_forces)
        

def createRobotPart(joint_laminate, counter, buildMesh=True):
    filename = str(joint_laminate.id)
    center_of_mass = joint_laminate.calculateCentroid()
    
    root_of_robot = etree.Element("link", name=filename)
    etree.SubElement(root_of_robot, "gravity").text = "true" # For Testing purposes disable gravity
    etree.SubElement(root_of_robot, "self_collide").text = "true" #To make the collision realistic.   
    
    centroid_pose = str(center_of_mass[0]) + " " + str(center_of_mass[1]) + " " + str(center_of_mass[2]) + " 0 0 0"
    #etree.SubElement(root_of_robot, "pose").text = centroid_pose    
    
    surface_tree = etree.Element("surface")
    friction = etree.SubElement(surface_tree, "friction")
    ode_params = etree.SubElement(friction, "ode")
    etree.SubElement(ode_params, "mu").text = "0.05"
    etree.SubElement(ode_params, "mu2").text = "0.05"   
    etree.SubElement(ode_params, "slip1").text = "1"
    etree.SubElement(ode_params, "slip2").text = "1"

    
    if buildMesh:
        visual_of_robot = etree.SubElement(root_of_robot, "visual", name="basic_bot_visual" + str(counter))        
        etree.SubElement(visual_of_robot, "pose").text = "0 0 0 0 0 0"
            
        geometry_of_robot = etree.Element("geometry")
        robo_mesh = etree.SubElement(geometry_of_robot, "mesh")
        etree.SubElement(robo_mesh, "uri").text = "file://" + popupcad.exportdir + os.path.sep  + filename + ".dae"
        #etree.SubElement(robo_mesh, "scale").text = "1 1 1000000"    #For debugging
        visual_of_robot.append(geometry_of_robot)

        from copy import deepcopy #copys the element
        collision = etree.SubElement(root_of_robot, "collision", name="basic_bot_collision" + str(counter))
        collision.insert(0, deepcopy(geometry_of_robot))
        collision.insert(0, surface_tree)
    else:
        visuals_of_robot = joint_laminate.toSDFTag("visual", "basic_bot_visual" + str(counter))    
        for visual_of_robot in visuals_of_robot:
            etree.SubElement(visual_of_robot, "cast_shadows").text = "true"
            #etree.SubElement(visual_of_robot, "transparency").text = str(0.5) #prevents it from being transparent.
            root_of_robot.append(visual_of_robot)     
        collisions = joint_laminate.toSDFTag("collision", "basic_bot_collision" + str(counter))
        for collision in collisions:    
            collision.insert(0, surface_tree)
            root_of_robot.append(collision)    
        
    inertial = etree.SubElement(root_of_robot, "inertial")
    trueMass = joint_laminate.calculateTrueVolume() * 1.4 / popupcad.SI_length_scaling
    etree.SubElement(inertial, "mass").text = str(trueMass) #TODO make layer specfic 
    etree.SubElement(inertial, "pose").text = centroid_pose
    
    return root_of_robot            

def createFloor():
    floor = etree.Element("model", name='floor')
    
    #etree.SubElement(floor, "pose").text = "0 0 -100 0 0 0"
    etree.SubElement(floor, "static").text = "true"
        
    floor_root = etree.SubElement(floor, "link", name='floor_link')


    surface_tree = etree.Element("surface")
    friction = etree.SubElement(surface_tree, "friction")
    ode_params = etree.SubElement(friction, "ode")
    etree.SubElement(ode_params, "mu").text = "0.05"
    etree.SubElement(ode_params, "mu2").text = "0.05"   
    etree.SubElement(ode_params, "slip1").text = "1"
    etree.SubElement(ode_params, "slip2").text = "1"
    
    floor_collision = etree.Element("collision", name='floor_collision')
    floor_collision.insert(0, surface_tree)    
    floor_root.append(floor_collision)
    #etree.SubElement(floor_collision, "pose").text = "0 0 0 0 0 0"
    floor_geo = etree.SubElement(floor_collision, "geometry")
    floor_box = etree.SubElement(floor_geo, "plane")
    etree.SubElement(floor_box, "size").text = "10 10"
    #floor_box = etree.SubElement(floor_geo, "box")    
    #etree.SubElement(floor_box, "size").text = "1000 1000 100"
    floor_visual = etree.SubElement(floor_root, "visual", name="floor visual")
    from copy import deepcopy #copys the element    
    floor_visual.append(deepcopy(floor_geo))    
    
    #material = etree.SubElement(floor_visual, "material")
    #etree.SubElement(material, "ambient").text = "1 0 0 1"
    #etree.SubElement(material, "diffuse").text = "1 0 0 1"
    #etree.SubElement(material, "specular").text ="0.1 0.1 0.1 1"
    #etree.SubElement(material, "emissive").text = "0 0 0 0"

    return floor


def extractLine(shape):    
    x = shape.exteriorpoints()[0][0] - shape.exteriorpoints()[1][0]
    y = shape.exteriorpoints()[0][1] - shape.exteriorpoints()[1][1]
    z = 0
    return (x, y, z)
    
def findMidPoint(shape, anchor):
    x = shape.exteriorpoints()[0][0] + shape.exteriorpoints()[1][0]
    y = shape.exteriorpoints()[0][1] + shape.exteriorpoints()[1][1]
    z = anchor.getLaminateThickness()    
    x /= (2.0 * popupcad.internal_argument_scaling * popupcad.SI_length_scaling)
    y /= (2.0 * popupcad.internal_argument_scaling * popupcad.SI_length_scaling)
    z /= (2.0 * popupcad.internal_argument_scaling * popupcad.SI_length_scaling)
    return (x, y, z)
    
def unitizeLine(shape):
    print(shape.exteriorpoints())
    (x, y, z) = extractLine(shape)    
    from math import sqrt
    length = sqrt(x * x + y * y)
    x /= length
    y /= length
    return (x, y, z)

#Ensures the connection are in the right order
def reorder_pair(joint_pair, hierarchy_map):
    first = hierarchy_map[joint_pair[0]]
    second = hierarchy_map[joint_pair[1]]
    if first > second:
        return (joint_pair[1], joint_pair[0])
    else:
        return joint_pair
    

