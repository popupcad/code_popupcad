# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 12:52:50 2015

This class

@author: skylion
"""
import trollius #NOTE: Trollius requires protobuffer from Google
from trollius import From

import pygazebo
import pygazebo.msg.joint_cmd_pb2
import pygazebo.msg.world_control_pb2
import time 
import popupcad
from lxml import etree
import subprocess
import os

try:
    import itertools.izip as zip
except ImportError:
    pass

def pause_simulation(world_name, pause=True):
    wait_net_service('localhost', 11345)
    
    @trollius.coroutine
    def coroutine():
        manager = yield From(pygazebo.connect())
        print("connected")
        
        publisher = yield From(
            manager.advertise("/gazebo/" + world_name + "/world_control",
                              'gazebo.msgs.WorldControl'))
    
        message = pygazebo.msg.world_control_pb2.WorldControl()
        message.pause = pause
        
        try:
            yield From(publisher.wait_for_listener())                
            yield From(publisher.publish(message))
            yield From(trollius.sleep(1.0))
        except:
            pass
        print("Connection closed")
            
    loop = trollius.get_event_loop()    
    loop.run_until_complete(coroutine())


def apply_joint_forces(world_name, robot_name, joint_names, forces, duration=-1):
    """ Applies joint forces via Trollius over a specified duration.
    """    
    wait_net_service('localhost', 11345)        
    print("Net serviced detected. Proceeding")

    @trollius.coroutine
    def joint_force_loop():
        manager = yield From(pygazebo.connect())
        publisher = yield From(manager.advertise('/gazebo/' + world_name + '/' + robot_name + '/joint_cmd',
                               'gazebo.msgs.JointCmd'))
        print("connected")
        
        t_start = time.time()
        t_end = time.time() + duration # The time that you want the controller to stop
        while time.time() < t_end or duration == -1:
            try:
                #print(str(time.time()) + "waiting for: " + str(t_end))
                for joint_name, force in zip(joint_names, forces):                    
                    yield From(publisher.wait_for_listener())                
                    message = pygazebo.msg.joint_cmd_pb2.JointCmd()
                    message.name = robot_name + '::' + joint_name #format should be: name_of_robot + '::name_of_joint'
                    message.force = force
                    yield From(publisher.publish(message))
                yield From(trollius.sleep(1.0))
            except Exception as e:
                print("SOMETHING HAS GONE WRONG: " + str(e))                
                break
                raise e
        print("Connection closed")
        #print("Duration =" + str(time.time() - t_start))
    tasks = []
    #for joint_name, force in zip(joint_names, forces):
    #    tasks.append(trollius.Task(joint_force_loop(world_name, robot_name, joint_name, force)))
    tasks.append(trollius.Task(joint_force_loop())) 
    
    loop = trollius.get_event_loop()    

    loop.run_until_complete(trollius.wait(tasks))

def apply_joint_pos(world_name, robot_name, joint_names, poses, duration=0):
    """ Applies a joint position asynchronously over multiple joint members, 
        then waits for a specified duration if specified.    
    """    
    wait_net_service('localhost', 11345)
    print("Net serviced detected. Proceeding")
    
    @trollius.coroutine
    def joint_pose_loop(world_name, robot_name, joint_name, pose):
        manager = yield From(pygazebo.connect())
        publisher = yield From(
                manager.advertise('/gazebo/' + world_name + '/' + robot_name + '/joint_cmd',
                                  'gazebo.msgs.JointCmd'))
        print("connected")         
        
        
        message = pygazebo.msg.joint_cmd_pb2.JointCmd()
        message.name = robot_name + '::' + joint_name #format should be: name_of_robot + '::name_of_joint'
        #Message.position is a PID message with several values
        message.position.target = pose
                  
        
        try:
            
            yield From(publisher.wait_for_listener())
            #This is needed to ensure that they are ready to publish.
            yield From(publisher.publish(message))
        except:
            pass
        print("Connection closed")
    
    tasks = []
    for joint_name, pose in zip(joint_names, poses):
        tasks.append(trollius.Task(joint_pose_loop(world_name, robot_name, joint_name, pose)))
        
    loop = trollius.get_event_loop()        
    loop.run_until_complete(trollius.wait(tasks))
    time.sleep(duration)  
#Applies the joint using PyGazebo. All joints are applied concurrently.
#Allows for granular PID control
#TODO Allow users to specify PID variables. 
#Until other variables implemented, this is experimental.
#WARNING: This method will crash Simbody
def apply_joint_pos_seq(world_name, robot_name, joint_names, poses, duration=0):
   """ Applies joint positions sequentially using subprocesses. No Trollius at all, 
       just commandline arguements.
   """
   wait_net_service('localhost', 11345)
   print("Net serviced detected. Proceeding")
   for joint_name, pose in zip(joint_names, poses):
       subprocess.call(["gz", "joint", "-m", robot_name, "-j", joint_name, '--pos-t', str(pose)]) 
       #os.system("gz joint -m " + robot_name + " -j " + joint_name + " --pos-t " + str(pose))
   print("Joint poses applied")
   time.sleep(duration)    

#Time is defined in nanoseconds
def wait_until_sim_time(target_time):
    ''' This function waits until the specified target_time in seconds.'''    
    import pygazebo.msg.world_stats_pb2
    
    @trollius.coroutine
    def sub_loop():
        manager = yield From(pygazebo.connect()) 
        
        sub_loop.is_waiting = True        
                
        
        def callback(data):
            if not sub_loop.is_waiting:
                return
            message = pygazebo.msg.world_stats_pb2.WorldStatistics.FromString(data)        
            sim_time = message.sim_time
            print('hi')            
            import math
            sim_time = sim_time.sec + sim_time.nsec/math.pow(10, 9)
            print(sim_time)
            sub_loop.is_waiting = sim_time < target_time
                            
                
        subscriber = manager.subscribe('/gazebo/world/world_stats',
                         'gazebo.msgs.WorldStatistics',
                         callback)
    
        yield From(subscriber.wait_for_connection())
        while(sub_loop.is_waiting):
            yield From(trollius.sleep(1.0))
        
        #subscriber.remove() #TODO This feature in PyGazebo is bugged.
        #Reimplement or hack around
        #print('Subscriber removed')
        print('Done waiting!')
            
    loop = trollius.get_event_loop()
    loop.run_until_complete(sub_loop())
    
#TODO Reimplement with pyGazebo or ROS    
def follow_model(robot_name, camera_name="gzclient_camera"):
    subprocess.call(["gz", "camera", "-c", camera_name, '-f', robot_name])
    print("Now following: " + robot_name)
    
    
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
    """
    Begins the export process to Gazebo
    """
    design = program.editor.design
    from popupcad.manufacturing.joint_operation2 import JointOperation2
    from popupcad.manufacturing.joint_operation3 import JointOperation3    
    operation = None  
    for tmp_op in design.operations:
        if (isinstance(tmp_op, JointOperation2) 
                and (operation is None 
                or not isinstance(operation, JointOperation3)) 
                or isinstance(tmp_op, JointOperation3)):
            operation = tmp_op

    if operation is None:            
        import PySide.QtGui as qg
        import PySide
        widget = qg.QMessageBox()
        widget.setText("Error: No Valid Joint Operation Detected")
        widget.setWindowModality(PySide.QtCore.Qt.NonModal)
        widget.exec_() 
    else:
        export_inner(operation)
       
    
#Export to Gazebo
def export_inner(operation, useDart=False):
    """ Continues the export process on the specified operation
    """    
    print("Beginnning Export")    
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
    etree.SubElement(model_object, "plugin", name="Model_Vel", 
                     filename="libmodel_vel.so")
    #world_object.append(createFloor())
    include_floor = etree.SubElement(world_object, "include")
    etree.SubElement(include_floor, "uri").text = "model://ground_plane"
    include_sun = etree.SubElement(world_object, "include")
    etree.SubElement(include_sun, "uri").text = "model://sun"
    
    #Sorts them in the correct order    
    #operation.connections.sort(key=lambda tup: tup[0], reverse=True)    
        
    ordered_connection = [reorder_pair(connection[1], operation.get_laminate_generations()) for connection in operation.connections]
    from tree_node import spawnTreeFromList
    tree = spawnTreeFromList(ordered_connection, sort=True)   
    assert(len(tree.decendents) == len(operation.bodies_generic) - 1)
    midpoints = [connect[0] for connect in operation.connections]
    print(midpoints)
    #Ensures that the list of lines is properly sorted    
    #assert(all(midpoints[i] <= midpoints[i+1] for i in xrange(len(midpoints)-1)))
    
    #tree = spawnTreeFromList([[str(ordered_connect[0]), str(ordered_connect[1])] for ordered_connect in ordered_connection])        
    
    counter = 0
    for joint_laminate in joint_laminates:
        model_object.append(createRobotPart(joint_laminate, counter, tree, approxCollisions=(not useDart)))
        counter+=1
    
    joint_names = []               
    for joint_connection in zip(midpoints, ordered_connection):
        from tree_node import TreeNode
        name = "hingejoint"
        name += tree.getNode(joint_connection[1][0]).getID()
        name += '|'
        name += tree.getNode(joint_connection[1][1]).getID()            
        model_object.append(craftJoint(operation, list(joint_connection), name, tree))
        joint_names.append(name)
        
    if useDart is True:
        physics_engine = 'dart'
    else:
        physics_engine = 'simbody'
        world_object.append(craftSimbodyPhysics())
    
    #Saves the object
    file_output = popupcad.exportdir + os.path.sep + project_name + ".world"
    f = open(file_output,"w")
    f.write(etree.tostring(global_root, pretty_print=True))
    f.close()
    
    def stringify(s1): #For local use to generate default Python code
        return "'{}'".format(s1)
    
    #Experimental Python IDE and Control System
    #TODO Sandbox this
    from popupcad.widgets.userinput import UserInputIDE
    mw = UserInputIDE()
    mw.setWindowTitle('Internal Python IDE')
    mw.appendText('#This code will control your robot during the simulation')
    mw.appendText('from popupcad_gazebo.gazebo_controller import apply_joint_forces, apply_joint_pos')
    mw.appendText('world_name=' + stringify(world_name))
    mw.appendText('robot_name=' + stringify(robot_name))
    mw.appendText('joint_names=' + str(joint_names))
    mw.te.setReadOnly(False)   
    mw.exec_()    
    print("Starting gazebo")
    user_input_code = compile(mw.te.toPlainText(), 'user_defined', 'exec')#Todo Sandbox this
     #TODO replace with Subprocess to prevent pollution of STDOUT
    #subprocess.Popen("killall -9 gazebo & killall -9 gzserver  & killall -9 gzclient", shell=True)    
    
    subprocess.Popen(['killall', 'gzserver'])
    gazebo = subprocess.Popen(["gazebo", "-e", physics_engine, file_output, '-u', '--verbose'])
    print("Gazebo is now open")
    
    #Even with wait net service we run into issues.    
    wait_net_service('localhost', 11345)
    print("Gazebo is done waiting")
    
    def exec_(arg): #This is done for Python 2 and 3 compatibility
        exec(arg)
        
    from multiprocessing import Process
    code_process = Process(target=exec_, args=(user_input_code,))
    time.sleep(4)
    follow_model(robot_name)
    pause_simulation(world_name, pause=False)
    code_process.start()    
    import PySide.QtGui as qg
    import PySide
    widget = qg.QMessageBox()
    widget.setText("Press Okay to Stop the Simulation and Close Gazebo")
    widget.setWindowModality(PySide.QtCore.Qt.NonModal)
    widget.exec_() 
    code_process.terminate()
    gazebo.terminate()
    #TODO Make it possible to kill the process later if it needs to

##TODO name the joints better, maybe via user_defined names if possible
def craftJoint(operation, connection, name, tree, upper_limit='3.145159', lower_limit='-3.145159'):
    """
    Generates the SDf tag for a joint based off the connection and laminate generations.
    """    
    joint_pair = connection[1]
    joint_root = etree.Element("joint", {"name":name, "type":"revolute"})
    etree.SubElement(joint_root, "parent").text = tree.getNode(joint_pair[0]).getID()
    etree.SubElement(joint_root, "child").text = tree.getNode(joint_pair[1]).getID()
    joint_center = findMidPoint(connection[0], joint_pair[0])
    joint_loc = str(joint_center[0]) + " " + str(joint_center[1]) + " " + str(joint_center[2]) + " 0 0 0"
    etree.SubElement(joint_root, "pose").text = joint_loc   
    axis = etree.SubElement(joint_root, "axis")
    line = unitizeLine(connection[0])    
    etree.SubElement(axis, "xyz").text = str(line[0]) + " " + str(line[1]) + " " + str(0)
    
    #etree.SubElement(axis, "use_parent_model_frame").text = "true"
    limit = etree.SubElement(axis, "limit")
    
    #Add the properties of the joint
    midpoints = [op[0] for op in operation.connections]
    joint_index = midpoints.index(connection[0])
    joint_props = operation.all_joint_props[joint_index]
    
    
    from popupcad.manufacturing.joint_operation3 import JointOperation3            
    if isinstance(operation, JointOperation3):
        from math import radians
        lower_limit = str(radians(joint_props[3]))
        upper_limit = str(radians(joint_props[4]))
    else:
        lower_limit = '-3.145159'
        upper_limit = '3.14519'
    
    etree.SubElement(limit, "lower").text = lower_limit
    etree.SubElement(limit, "upper").text = upper_limit
            
    #etree.SubElement(limit, "stiffness").text = str(joint_props[0])
    from math import radians    
    dynamics = etree.SubElement(axis, "dynamics")
    etree.SubElement(dynamics, "damping").text = str(joint_props[1])
    etree.SubElement(dynamics, "spring_reference").text = str(radians(joint_props[2]))
    etree.SubElement(dynamics, "spring_stiffness").text = str(joint_props[0])    
    return joint_root

#Obsolete method to create floor, now we just include ground_plane
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
    surface = etree.SubElement(floor_collision, "surface")    
    bounce = etree.SubElement(surface, "bounce")    
    etree.SubElement(bounce, "restitution_coefficient").text = str(0)    
    etree.SubElement(floor_box, "size").text = "100 100"
    #floor_box = etree.SubElement(floor_geo, "box")    
    #etree.SubElement(floor_box, "size").text = "1000 1000 100"
    floor_visual = etree.SubElement(floor_root, "visual", name="floor visual")
    from copy import deepcopy #copys the element    
    floor_visual.append(deepcopy(floor_geo))    
    
    
    
    material = etree.SubElement(floor_visual, "material")
    etree.SubElement(material, "ambient").text = "0 0 0 0"
    etree.SubElement(material, "diffuse").text = "0 0 0 0"
    etree.SubElement(material, "specular").text ="0.1 0.1 0.1 1"
    etree.SubElement(material, "emissive").text = "0 0 0 0"

    return floor

def extractLine(shape, z = 0):    
    """
    Extracts a line from a shape line.
    """
    x = shape.exteriorpoints()[0][0] - shape.exteriorpoints()[1][0]
    y = shape.exteriorpoints()[0][1] - shape.exteriorpoints()[1][1]
    return (x, y, z)
    
def findMidPoint(shape, anchor):
    """
    Finds the midpoint of the line and extrcts the height out of it from the laminate.
    """
    x = shape.exteriorpoints()[0][0] + shape.exteriorpoints()[1][0]
    y = shape.exteriorpoints()[0][1] + shape.exteriorpoints()[1][1]
    z = anchor.getLaminateThickness()    
    x /= (2.0  * popupcad.SI_length_scaling)
    y /= (2.0  * popupcad.SI_length_scaling)
    z /= (2.0  * popupcad.SI_length_scaling)
    return (x, y, z)
    
def unitizeLine(shape):
    """
    Unitizes a line
    """
    (x, y, z) = extractLine(shape)    
    from math import sqrt
    length = sqrt(x * x + y * y)
    x /= length
    y /= length
    return (x, y, z)

#TODO Ensure this actually works
#Ensures the connection are in the right order
def reorder_pair(joint_pair, hierarchy_map):
    first = hierarchy_map[joint_pair[0]]
    second = hierarchy_map[joint_pair[1]]
    if first > second:
        return (joint_pair[1], joint_pair[0])
    else:
        return joint_pair
    
def createRobotPart(joint_laminate, counter, tree, buildMesh=True, approxCollisions=False):
    """
    Creates the SDF for each link in the Robot
    """
    filename = str(joint_laminate.id)
    _, trueMass, center_of_mass, I =  joint_laminate.mass_properties()      
    
    xml_name = tree.getNode(joint_laminate).getID()   
    
    root_of_robot = etree.Element("link", name=xml_name)
    etree.SubElement(root_of_robot, "gravity").text = "true" # For Testing purposes disable gravity
    etree.SubElement(root_of_robot, "self_collide").text = str(not approxCollisions) 
    #To make the collision realistic.   
    
    centroid_pose = str(center_of_mass[0]) + " " + str(center_of_mass[1]) + " " + str(center_of_mass[2]) + " 0 0 0"
    
    surface_tree = etree.Element("surface")
    friction = etree.SubElement(surface_tree, "friction")
    ode_params = etree.SubElement(friction, "ode")
    etree.SubElement(ode_params, "mu").text = "0.05"
    etree.SubElement(ode_params, "mu2").text = "0.05"   
    etree.SubElement(ode_params, "slip1").text = "1"
    etree.SubElement(ode_params, "slip2").text = "1"
    
    if buildMesh: #Decides if you want to use an external mesh file or the polyline feature (experimental)
        joint_laminate.toDAE()      
        visual_of_robot = etree.SubElement(root_of_robot, "visual", name="basic_bot_visual" + str(counter))        
        etree.SubElement(visual_of_robot, "pose").text = "0 0 0 0 0 0"
        
        geometry_of_robot = etree.Element("geometry")
        robo_mesh = etree.SubElement(geometry_of_robot, "mesh")
        etree.SubElement(robo_mesh, "uri").text = "file://" + popupcad.exportdir + os.path.sep  + filename + ".dae"
        #etree.SubElement(robo_mesh, "scale").text = "1 1 1000000"    #For debugging
        visual_of_robot.append(geometry_of_robot)

        
        if approxCollisions:
            collision = approximateCollisions2(joint_laminate, center_of_mass)
            #for collision in collisions:
            root_of_robot.append(collision)
        else:
            from copy import deepcopy #copys the element
            collision = etree.SubElement(root_of_robot, "collision", name="basic_bot_collision" + str(counter))        
            collision.insert(0, deepcopy(geometry_of_robot))
            collision.insert(0, surface_tree)
    else:
        visuals_of_robot = joint_laminate.toSDFTag("visual", "basic_bot_visual" + str(counter))    
        for visual_of_robot in visuals_of_robot:
            #Feel free tocomment these out for optional model prettyness. 
            #Note though it may cause additional lag
            etree.SubElement(visual_of_robot, "cast_shadows").text = "true"
            #etree.SubElement(visual_of_robot, "transparency").text = str(0.5) #prevents it from being transparent.
            root_of_robot.append(visual_of_robot)     
        if approxCollisions:
            collision = approximateCollisions2(joint_laminate, center_of_mass)
            #for collision in collisions:
            root_of_robot.append(collision)
        else:
            collisions = joint_laminate.toSDFTag("collision", "basic_bot_collision" + str(counter))
            for collision in collisions:    
                collision.insert(0, surface_tree)
                root_of_robot.append(collision)    
                
    inertial = etree.SubElement(root_of_robot, "inertial")
    #trueMass = joint_laminate.calculateTrueVolume() * joint_laminate.getDensity() 
    etree.SubElement(inertial, "mass").text = str(trueMass) 
    etree.SubElement(inertial, "pose").text = centroid_pose
    it_matrix = etree.SubElement(inertial, "inertia")    
    etree.SubElement(it_matrix, 'ixx').text = str(I[0,0])
    etree.SubElement(it_matrix, 'ixy').text = str(I[0,1])
    etree.SubElement(it_matrix, 'ixz').text = str(I[0,2])
    etree.SubElement(it_matrix, 'iyy').text = str(I[1,1])
    etree.SubElement(it_matrix, 'iyz').text = str(I[1,2])
    etree.SubElement(it_matrix, 'izz').text = str(I[2,2])
    return root_of_robot


#Experimental and Deprecated
def approximateCollisions(joint_laminate, centroid):    
    collisions = []
    layerdef = joint_laminate.layerdef
    for layer in layerdef.layers:
        shapes = joint_laminate.geoms[layer]#TODO Add it in for other shapes         
        zvalue = layerdef.zvalue[layer]      
        thickness = layer.thickness
        if (len(shapes) == 0) : #In case there are no shapes.
            print("No shapes skipping")            
            continue
        for s in shapes:
            vertices = [vert/popupcad.SI_length_scaling for vert in s.extrudeVertices(thickness, z0=zvalue)]
            for x, y, z in zip(vertices, vertices[1:], vertices[2:]):
                joint_name = str(joint_laminate.id) + ':('+str(x)+','+str(y)+','+str(z)+')'
                collision = etree.Element("collision", name=joint_name)
                etree.SubElement(collision, 'pose').text = str(x) + ' ' + str(y) + ' ' + str(z) + ' 0 0 0'
                geom = etree.SubElement(collision, 'geometry')
                sphere = etree.SubElement(geom, 'sphere')
                etree.SubElement(sphere, 'radius').text = str(0.01) #1cm will be the range of the collisions
                collisions.append(collision)
    return collisions
    
def approximateCollisions2(joint_laminate, centroid):    
    x, y, z = centroid
    x1, y1, x2, y2 = joint_laminate.getBoundingBox()
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    width/=popupcad.SI_length_scaling
    height/=popupcad.SI_length_scaling
    joint_name = "collision:" + str(joint_laminate.id)
    collision = etree.Element("collision", name=joint_name)
    etree.SubElement(collision, 'pose').text = str(x) + ' ' + str(y) + ' ' + str(z) + ' 0 0 0'
    geom = etree.SubElement(collision, 'geometry')
    sphere = etree.SubElement(geom, 'box')
    thickness = joint_laminate.getLaminateThickness()
    thickness/=popupcad.SI_length_scaling    
    etree.SubElement(sphere, 'size').text = str(width) + ' ' + str(height) + ' ' + str(thickness)
    surface = etree.SubElement(collision, "surface")    
    bounce = etree.SubElement(surface, "bounce")    
    etree.SubElement(bounce, "restitution_coefficient").text = str(0)    
    return collision
 
def craftSimbodyPhysics():
    physics_root = etree.Element("physics", {"name":"Simbody", "default":"true", "type":"revolute"})
    simbody_physics = etree.SubElement(physics_root, "simbody")
    contact = etree.SubElement(simbody_physics, "contact")
    etree.SubElement(contact, "plastic_coef_restitution").text = str(0)
    etree.SubElement(contact, "override_impact_capture_velocity").text = str(100000000)
    return physics_root
    
#TODO Move these import mesh function to a proper home.
def import_STL(filename):
    '''
    Imports an STL File. 
    The vectors, normals, and individual vertices are contained as numpy arrays within the object.
    '''
    from stl import mesh
    mesh = mesh.Mesh.from_file(filename)
    return mesh
    
#TODO test collada. Unable to test because our DAE files are badly formatted
#TODO Ensure collada files are better formatted in the future. Materials are not loaded.
def import_Collada(filename):
    '''
    Returns a list of objects represented as a list of triangles. 
    A triangle is list of vertices. 
    A vertex is a list of points.
    '''
    from collada import Collada
    from StringIO import StringIO 
    
    import sys, inspect #This allows it to except bad Collada files by ignore all errors
    clsmembers = inspect.getmembers(sys.modules['collada.common'], inspect.isclass)
    ignore_types = [cls[1] for cls in clsmembers]    

    mesh = Collada(filename, ignore=ignore_types)        
    geoms = mesh.geometries #This is the list of geometries
    geom_tris = []    
    for geom in geoms:
        for primitive in geom.primitives:
            triangles = list(primitive)
            #Appends each triangles set with each triangle being just a list of vertice
            geom_tris.append([tri.vertices for tri in triangles])
    return geom_tris