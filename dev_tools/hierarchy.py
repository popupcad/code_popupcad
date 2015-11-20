# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 06:57:37 2015

@author: danaukes
"""

#from pynamics.tree_node import TreeNode
from dev_tools.acyclicdirectedgraph import Node,AcyclicDirectedGraph
import random
import numpy
#import yaml


def level(connections):
    return [item.level for item in connections]
def overlaps(connections,connection):
    return [connection.overlaps(item) for item in connections]
def max_overlapping_levels(connections,connection):
    return max([item.level for item in connections if connection.overlaps(item)])

class Operation(Node):
    def __init__(self,name,*args,**kwargs):
        super(Operation,self).__init__(*args,**kwargs)
        self.name=name
        
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)
        
class Connection(object):
    def __init__(self,list1,parent,child):
        self.list1 = list1
        self.parent = parent
        self.child = child

    @property
    def ii(self):
        return self.list1.index(self.parent)

    @property
    def jj(self):
        return self.list1.index(self.child)
    @property
    def hops(self):
        return self.jj-self.ii

    def get_level(self):
        try:
            return self._level
        except AttributeError:
            self._level = -1

    def set_level(self,level):
        self._level = level

    level = property(get_level,set_level)

    def __str__(self):
        return '{0} --> {1}'.format(self.parent,self.child)
        
    def __repr__(self):
        return str(self)
    
    def segments(self):
        a=numpy.r_[self.ii:self.jj]
        b=a+1
        c=numpy.array([a,b])
        d = c.T.tolist()
        e = [tuple(item) for item in d]
        return e

    def overlapped_items(self):
        a=numpy.r_[self.ii+1:self.jj]
        return a.tolist()

    def overlapping_segments(self,other):
        my_segments = set(self.segments())
        other_segments = set(other.segments())
        return my_segments.intersection(other_segments)
    
    def overlaps(self,other):
        return not not self.overlapping_segments(other)


if __name__=='__main__':
    num_operations = 10
            
    operations = []
    for item in range(num_operations):
        operation = Operation('item '+str(item))
        operations.append(operation)

    connection_list = []        
    for ii,operation in enumerate(operations[:-1]):
#        operation.add_branch(operations[ii+1])
        connection_list.append((operation,operations[ii+1]))
        
        
    num_extra_connections = 10
    
    extras = []
    for ii in range(num_extra_connections):
        a = random.randint(0,num_operations-2)
        b = random.randint(a+1,num_operations-1)
        extras.append((a,b))
#        operations[a].add_branch(operations[b])
        connection_list.append((operations[a],operations[b]))


    network = AcyclicDirectedGraph(operations,connection_list)
    #
    #with open('structure.yaml','w') as f:
    #    yaml.dump(operations,f)
        
#    with open('structure.yaml',) as f:
#        operations = yaml.load(f)
#    num_operations = len(operations)
        
    #A = numpy.zeros((num_operations,num_operations),dtype=int)  
    #IJ =  numpy.array(numpy.meshgrid(numpy.r_[0:num_operations],numpy.r_[0:num_operations])).T
    #
    connections = []
    for ii,operation in enumerate(operations):
        for child in operation.children():
            connections.append(Connection(operations,operation,child))
    #        jj = operations.index(child)
    #        A[ii,jj]=1
    #    print(operation,children)
    ##print(A)
        
    #connections2 = sorted(numpy.array(A.nonzero()).T.tolist(),key=lambda item:(item[1]-item[0],item[0]))
    
    connections.sort(key=lambda item:(item.hops,item.ii))
    level(connections)
    c = connections[-3]
    #print(max_overlapping_levels(connections,c))
    for connection in connections:
        connection.set_level(max_overlapping_levels(connections,connection)+1)
    levels = [c.level for c in connections]
    num_levels = max(levels)+1
    A = numpy.array([[' ']*num_levels]*num_operations)
    for c in connections:
        A[c.ii,c.level]='*'
        A[c.jj,c.level]='*'
        
    #    if not not c.overlapped_items:
        A[c.overlapped_items(),c.level]='|'
    #
    for item in A:
        string = ''.join(item)
        print(string)
        
        