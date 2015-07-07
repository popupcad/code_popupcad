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

try:
    import itertools.izip as zip
except ImportError:
    pass

def apply_joint_forces(world_name, robot_name, joint_names, forces, duration=-1):
    wait_net_service('localhost',11345)

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
            print(message)            
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
    
    #Experimental code to make this loop non-blocking
    #loop = trollius.get_event_loop()
    #loop_thread_tasks = lambda t_loop: loop_in_thread(t_loop, tasks)
    #import threading
    #t = threading.Thread(target=loop_thread_tasks, args=(loop,))
    #t.start()
    #return t
    loop = trollius.get_event_loop()
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
            time.sleep(2)
        except socket.timeout, err:
            # this exception occurs only if timeout is set
            if timeout:
                return False
      
        except socket.error, err:
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if type(err.args) != tuple or (err[0] != errno.ETIMEDOUT and err[0] != errno.ECONNREFUSED):
                raise err
        else:
            s.close()
            return True