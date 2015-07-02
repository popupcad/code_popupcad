# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 12:52:50 2015

@author: skylion
"""

import trollius #NOTE: Trollius requires protobuffer from Google
from trollius import From

import pygazebo
import pygazebo.msg.joint_cmd_pb2

def apply_joint_force(world_name, robot_name, joint_name, force, duration=-1):

    @trollius.coroutine 
    def joint_force_loop():
        manager = yield From(pygazebo.connect())
        
        publisher = yield From(
            manager.advertise('/gazebo/' + world_name + '/' + robot_name + '/joint_cmd',
                              'gazebo.msgs.JointCmd'))
    
        message = pygazebo.msg.joint_cmd_pb2.JointCmd()
        message.name = robot_name + '::' + joint_name #format should be: name_of_robot + '::name_of_joint'
        message.force = force
    
       
        import time
    
        t_end = time.time() + duration # The time that you want the controller to stop
        while time.time() < t_end or duration == -1:
            yield From(publisher.publish(message))
            yield From(trollius.sleep(1.0))
    

    loop = trollius.get_event_loop()
    loop.run_until_complete(joint_force_loop())
