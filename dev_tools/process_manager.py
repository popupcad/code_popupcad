# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from multiprocessing import Process
from multiprocessing import Queue
import time
import random
import yaml
import os
        
#def run_wrapper(a,b):
#    def wrap1(f):
#        print(a,b)
#        def wrapped_func(*args,**kwargs):
#            d = f(*args,**kwargs)
#            return d
#        return wrapped_func
#    return wrap1
#
#@run_wrapper('hey','babe')
#def e(a,b,c):
#    print('inner',a,b,c)
#    return c
    
class DummyClass(object):
    def run(self):        
        time.sleep(random.gauss(3,1))
        self.dummy = 'asdfsadfafds'

class ProcessDataWrapper(object):
    ii = 0
    def __init__(self,inner_process):
        self.index = ProcessDataWrapper.ii
        self.inner_process = inner_process
        ProcessDataWrapper.ii+=1
    def run_outer(self):
        self.time_started = time.time()
        self.inner_process.run()
        self.time_finished = time.time()
        self.time_elapsed = self.time_finished - self.time_started
    def save(self,folder):
        if not os.path.exists(folder):
            os.mkdir(folder)
        with open(os.path.normpath(os.path.join(folder,str(self.index)+'.dat')),'w') as f:
            yaml.dump(self,f)
        
class ProcessData(object):
    ii = 0
    def __init__(self):
        self.index = ProcessData.ii
        ProcessData.ii+=1
    def run_outer(self):
        self.time_started = time.time()
        self.run()
        self.time_finished = time.time()
        self.time_elapsed = self.time_finished - self.time_started
    def save(self,folder):
        with open(os.path.normpath(os.path.join(folder,str(self.index)+'.dat')),'w') as f:
            yaml.dump(self,f)
        
class DummyClass2(ProcessData):
    def run(self):        
        time.sleep(random.gauss(3,1))
        self.dummy = 'asdfsadfafds'
    
class ProcessContainer(Process):
    def __init__(self,inner_process):
        Process.__init__(self)
#        self.process_data = ProcessDataWrapper(inner_process)
        self.process_data = inner_process
    def run(self):
        self.process_data.run_outer()
        self.queue.put(self.process_data)
    def set_queue(self,queue):
        self.queue = queue
        
class ProcessManager(object):
    sleep_time = .5
    def __init__(self,processes,max_processes=4,debug=True,block_till_finished = True,collect_all_data = True,save_data = False,save_dest = '.',refresh_display = None):
        self.all_processes = [ProcessContainer(p) for p in processes]
        self.processes = self.all_processes.copy()
        self.max_processes = max_processes
        self.debug = debug
        self.collect_all_data = collect_all_data
        if self.collect_all_data:
            self.data= []
        self.save_data = save_data
        self.save_dest = save_dest
        self.block_till_finished = block_till_finished
        self.running = []
        self.done = []
        self.num_processes = len(self.processes)
        self.queue=Queue()
        self.checkalivedead()
        if refresh_display!=None:
            self.refresh_display = refresh_display
        
    def run(self):
        self.time_launched = time.time()
        self.print_debug('launching processes')        
        while not not self.processes:
            if self.num_running < self.max_processes:
                num_can_start = self.max_processes - self.num_running 
                num_remaining = len(self.processes)
                num_to_start = min(num_can_start,num_remaining)
                new_processes = []
                for ii in range(num_to_start):
                    p = self.processes.pop(0)
                    new_processes.append(p)
                    p.set_queue(self.queue)
                    p.start()
                    self.running.append(p)
#                for p in new_processes:
#                    p.join()
                string = '{0:0.0f} slots, {1:0.0f} remaining, {2:0.0f} started'.format(num_can_start,num_remaining,num_to_start)
                self.print_debug(string)
            self.checkalivedead()
            self.pull_queue()
            time.sleep(self.sleep_time)
#        for processss in self.all_processes:
#            proce.join()

        if self.block_till_finished:
            self.print_debug('waiting to clear')
            while not not self.running:
                self.checkalivedead()
                self.pull_queue()
                time.sleep(self.sleep_time)

    def checkalivedead(self):
        running = []
        new_done = False
        for process in self.running:
            if process.is_alive():
                running.append(process)
            else:
                self.done.append(process)
                new_done = True
                
        self.running = running
        self.num_running = len(self.running)
        self.num_done= len(self.done)
        if self.debug:
            if new_done:
                time_current = time.time()
                time_elapsed = time_current - self.time_launched
                time_remaining = (time_current-self.time_launched)/self.num_done*self.num_processes
                self.print_debug('{0:.2f} minutes elapsed/{1:.2f} minutes total, {2:d}/{3} finished'.format(time_elapsed/60,time_remaining/60,self.num_done,self.num_processes))

    def pull_queue(self):
        newitems = []
        while not self.queue.empty():
            item = self.queue.get()
            if self.collect_all_data:
                self.data.append(item)
            if self.save_data:
                item.save(self.save_dest)
            newitems.append(item)
            try:
                self.refresh_display(newitems)
            except AttributeError:
                pass
            
    def print_debug(self,*args,**kwargs):
        if self.debug:
            print(args,kwargs)


if __name__ == '__main__':
    t0 = time.time()
    processes = [DummyClass2() for index in range(20)]
    pm = ProcessManager(processes,max_processes=10,debug=True,block_till_finished = True,collect_all_data = False,save_data = True,save_dest = './data')
    pm.run()
    
    t1 = time.time()
    print('elapsed time: ',t1-t0)
