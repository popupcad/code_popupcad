# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 12:52:50 2015

@author: skylion
"""

import trollius #NOTE: Trollius requires protobuffer from Google
from trollius import From

import pygazebo
import pygazebo.msg.joint_cmd_pb2
import time 
import popupcad
from lxml import etree
import os

try:
    import itertools.izip as zip
except ImportError:
    pass

def apply_joint_forces(world_name, robot_name, joint_names, forces, duration=-1):
    wait_net_service('localhost',11345)    
    print("Net serviced detected. Proceeding")

    @trollius.coroutine
    def joint_force_loop(world_name, robot_name, joint_name, force, duration=-1):
        manager = yield From(pygazebo.connect())
        print("connected")
        
        
        publisher = yield From(
            manager.advertise('/gazebo/' + world_name + '/' + robot_name + '/joint_cmd',
                              'gazebo.msgs.JointCmd'))
    
        message = pygazebo.msg.joint_cmd_pb2.JointCmd()
        message.name = robot_name + '::' + joint_name #format should be: name_of_robot + '::name_of_joint'
        message.force = force
        
        t_end = time.time() + duration # The time that you want the controller to stop
        while time.time() < t_end or duration == -1:
            try:
                yield From(publisher.publish(message))
                yield From(trollius.sleep(1.0))
            except:
                pass
                break
        print("Connection closed")
        
    def loop_in_thread(loop, tasks):
        trollius.set_event_loop(loop)
        loop.run_until_complete(trollius.wait(tasks))
        
    tasks = []
    for joint_name, force in zip(joint_names, forces):
        tasks.append(trollius.Task(joint_force_loop(world_name, robot_name, joint_name, force, duration)))
    
    
    loop = trollius.get_event_loop()    
    import PySide.QtGui as qg
    import PySide
    widget = qg.QMessageBox()
    widget.setText("Close Gazebo to continue...")
    widget.setWindowModality(PySide.QtCore.Qt.NonModal)    
    widget.show()
    
    
    #Experimental code to make this loop non-blocking
    #loop = trollius.get_event_loop()
    #loop_thread_tasks = lambda t_loop: loop_in_thread(t_loop, tasks)
    #import threading
    #t = threading.Thread(target=loop_thread_tasks, args=(loop,))
    #t.start()
    #return t
    loop.run_until_complete(trollius.wait(tasks))
    

def apply_joint_pos(world_name, robot_name, joint_names, poses, duration=-1):
    wait_net_service('localhost', 11345)
    print("Net serviced detected. Proceeding")

    @trollius.coroutine
    def joint_pos_loop(world_name, robot_name, joint_name, pos):
        manager = yield From(pygazebo.connect())
        print("connected")
        
        
        publisher = yield From(
            manager.advertise('/gazebo/' + world_name + '/' + robot_name + '/joint_cmd',
                              'gazebo.msgs.JointCmd'))
    
        message = pygazebo.msg.joint_cmd_pb2.JointCmd()
        message.name = robot_name + '::' + joint_name #format should be: name_of_robot + '::name_of_joint'
        message.position = pos
        
        try:
            yield From(publisher.publish(message))
            yield From(trollius.sleep(1.0))
        except:
            pass
        print("Connection closed")
        
    def loop_in_thread(loop, tasks):
        trollius.set_event_loop(loop)
        loop.run_until_complete(trollius.wait(tasks))
        
    tasks = []
    for joint_name, pos in zip(joint_names, poses):
        tasks.append(trollius.Task(joint_pos_loop(world_name, robot_name, joint_name, pos)))
    
    
    loop = trollius.get_event_loop()    
    import PySide.QtGui as qg
    import PySide
    widget = qg.QMessageBox()
    widget.setText("Close Gazebo to continue...")
    widget.setWindowModality(PySide.QtCore.Qt.NonModal)    
    widget.exec_()
    
    
    #Experimental code to make this loop non-blocking
    #loop = trollius.get_event_loop()
    #loop_thread_tasks = lambda t_loop: loop_in_thread(t_loop, tasks)
    #import threading
    #t = threading.Thread(target=loop_thread_tasks, args=(loop,))
    #t.start()
    #return t
    loop.run_until_complete(trollius.wait(tasks))
    
    
def wait_net_service(server, port, timeout=None):
    """ Wait for network service to appear 
        @param timeout: in seconds, if None or 0 wait forever
        @return: True of False, if timeout is None may return only True or
                 throw unhandled network exception
    """
    import socket
    import errno

    s = socket.socket()
    if timeout:
        from time import time as now
        # time module is needed to calc timeout shared between two exceptions
        end = now() + timeout

    while True:   
        try:
            if timeout:
                next_timeout = end - now()
                if next_timeout < 0:
                    return False
                else:
            	    s.settimeout(next_timeout)
            s.connect((server, port))
        except socket.timeout as err:
            # this exception occurs only if timeout is set
            if timeout:
                return False
      
        except socket.error as err:
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if type(err.args) != tuple or (err[0] != errno.ETIMEDOUT and err[0] != errno.ECONNREFUSED):
                raise err
        else:
            s.close()
            return True

def export(program):
    design = program.editor.design
    from popupcad.manufacturing.joint_operation2 import JointOperation2
    for tmp_op in design.operations:
        if isinstance(tmp_op, JointOperation2):
            operation = tmp_op
    export_inner(operation)
       
    
#Export to Gazebo
def export_inner(operation):
    joint_laminates = operation.bodies_generic
   
   
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
    
    #world_object.append(createFloor())
    include_floor = etree.SubElement(world_object, "include")
    etree.SubElement(include_floor, "uri").text = "model://ground_plane"
    include_sun = etree.SubElement(world_object, "include")
    etree.SubElement(include_sun, "uri").text = "model://sun"
    
    counter = 0
    for joint_laminate in joint_laminates:
        model_object.append(createRobotPart(joint_laminate, counter))
        counter+=1
    
    counter = 0
    for joint_connection in operation.connections:
        model_object.append(craftJoint(operation, joint_connection, counter))
        counter+=1
    
    #Fixed joint method
    #joint_root = etree.SubElement(model_object, "joint", {'name':'atlas', 'type':'revolute'})
    #etree.SubElement(joint_root, 'parent').text = 'world'
    #etree.SubElement(joint_root, 'child').text = str(operation.connections[0][1][0].id)
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
    

    
    joint_names = []        
    for num in range(0, len(operation.all_joint_props)):
        joint_names.append("hingejoint" + str(num))
   
    #joint_forces = [joint_def[2] for joint_def in operation.all_joint_props]
    #apply_joint_forces(world_name, robot_name, joint_names, joint_forces)
    #apply_joint_pos(world_name, robot_name, joint_names, joint_forces)
    
    #Experimental Python IDE and Control System
    #TODO Sandbox this
    #TODO Save and load python scripts
    from popupcad_gazebo.userinput import UserInputIDE
    mw = UserInputIDE()
    mw.setWindowTitle('Internal Python IDE')
    mw.appendText('#This code will control your robot during the simulation')
    mw.appendText('from popupcad_gazebo.gazebo_controller import apply_joint_forces, apply_joint_pos')
    mw.appendText('world_name=' + stringify(world_name))
    mw.appendText('robot_name=' + stringify(robot_name))
    mw.appendText('joint_names=' + str(joint_names))
    mw.te.setReadOnly(False)   
    mw.exec_()    
    user_input_code = mw.te.toPlainText()#Todo Sandbox this
    exec(user_input_code)
    print("the window should have oppened")
    
    #TODO replace with Subprocess to prevent pollution of STDOUT
    os.system("gazebo -e dart " + file_output + " &")
    

def stringify(s1):
    return "'{}'".format(s1)
    
def craftJoint(operation, connection, counter):
    joint_pair = reorder_pair(connection[1], operation.get_laminate_generations())    
    
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
    joint_props = operation.all_joint_props[operation.connections.index(connection)]
    #etree.SubElement(limit, "stiffness").text = str(joint_props[0])
    dynamics = etree.SubElement(axis, "dynamics")
    etree.SubElement(dynamics, "damping").text = str(joint_props[1])
    etree.SubElement(dynamics, "spring_reference").text = str(joint_props[2])
    etree.SubElement(dynamics, "spring_stiffness").text = str(joint_props[0])    
    return joint_root


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
    try:
        first = hierarchy_map[joint_pair[0]]
        second = hierarchy_map[joint_pair[1]]
    except:
        return joint_pair
    if first > second:
        return (joint_pair[1], joint_pair[0])
    else:
        return joint_pair
    
        

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
        joint_laminate.toDAE()      
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
    trueMass = joint_laminate.calculateTrueVolume() * joint_laminate.getDensity() 
    import math    
    trueMass /= math.pow(popupcad.SI_length_scaling, 3) #Volume is cubed
    etree.SubElement(inertial, "mass").text = str(trueMass) #TODO make layer specfic 
    etree.SubElement(inertial, "pose").text = centroid_pose
    
    return root_of_robot            
