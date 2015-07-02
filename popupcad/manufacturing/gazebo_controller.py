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

def apply_joint_force(world_name, robot_name, joint_name, force, duration=-1):

    
    @trollius.coroutine 
    def joint_force_loop():
        manager = yield From(pygazebo.connect())
        print("connected")
        
        
        publisher = yield From(
            manager.advertise('/gazebo/' + world_name + '/' + robot_name + '/joint_cmd',
                              'gazebo.msgs.JointCmd'))
    
        message = pygazebo.msg.joint_cmd_pb2.JointCmd()
        message.name = robot_name + '::' + joint_name #format should be: name_of_robot + '::name_of_joint'
        message.force = force
    
    
        #t_end = time.time() + duration # The time that you want the controller to stop
        while True: #time.time() < t_end or duration == -1:
            try:
                yield From(publisher.publish(message))
                yield From(trollius.sleep(1.0))
            except:
                pass
             #Nothing   
        print("Connection closed")
       
    wait_net_service('localhost',11345)
    
    
    loop = trollius.get_event_loop()
    loop.run_until_complete(joint_force_loop())
    raise     
    
    
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
            time.sleep(1)
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

