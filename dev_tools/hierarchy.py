# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

#from pynamics.tree_node import TreeNode
from dev_tools.acyclicdirectedgraph import Node,AcyclicDirectedGraph
import random
#import numpy
#import yaml


def level(connections):
    return [item.level for item in connections]
def overlaps(connections,connection):
    return [connection.overlaps(item) for item in connections]
def max_overlapping_levels(connections,connection):
    return max([item.level for item in connections if connection.overlaps(item)])
def num_levels(connections):
    levels = [c.level for c in connections]
    num_levels = len(set(levels))
    return num_levels
    
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
            return self._level

    def set_level(self,level):
        self._level = level

    level = property(get_level,set_level)

    def __str__(self):
        return '{0} --> {1}'.format(self.parent,self.child)
        
    def __repr__(self):
        return str(self)
    
    def segments(self):
        a = range(self.ii,self.jj)
        b = range(self.ii+1,self.jj+1)
        e = [tuple(item) for item in zip(a,b)]
        return e

    def overlapped_items(self):
        a=list(range(self.ii+1,self.jj))
        return a

    def overlapping_segments(self,other):
        my_segments = set(self.segments())
        other_segments = set(other.segments())
        return my_segments.intersection(other_segments)
    
    def overlaps(self,other):
        return not not self.overlapping_segments(other)
    
def create_sorted_connections(list_in, get_children):
    connections = []
    for ii,operation in enumerate(list_in):
        for child in get_children(operation):
            connections.append(Connection(list_in,operation,child))
    connections.sort(key=lambda item:(item.hops,item.ii))

    for connection in connections:
        connection.set_level(max_overlapping_levels(connections,connection)+1)

    return connections
        

if __name__=='__main__':
    num_operations = 10
#            
#    operations = []
#    for item in range(num_operations):
#        operation = Operation('item '+str(item))
#        operations.append(operation)
#
#    connection_list = []        
#    for ii,operation in enumerate(operations[:-1]):
##        operation.add_branch(operations[ii+1])
#        connection_list.append((operation,operations[ii+1]))
#        
#        
#    num_extra_connections = 10
#    
#    extras = []
#    for ii in range(num_extra_connections):
#        a = random.randint(0,num_operations-2)
#        b = random.randint(a+1,num_operations-1)
#        extras.append((a,b))
##        operations[a].add_branch(operations[b])
#        connection_list.append((operations[a],operations[b]))
#
#    network = AcyclicDirectedGraph(operations,connection_list)

#    ----------------------------------------------------------

    operations = list(range(num_operations))
    connections = {}
    for item in operations:
        connections[item]=[]
    connections[0].append(1)
    connections[0].append(4)
    connections[0].append(5)
    connections[2].append(6)
        

    connections = create_sorted_connections(operations,lambda item:connections[item])

    A = [[' ']*num_levels(connections) for ii in range(num_operations)]
    for c in connections:
        A[c.ii][c.level]='*'
        A[c.jj][c.level]='*'
#        
        for kk in c.overlapped_items():
            A[kk][c.level]='|'
#    #
    for item in A:
        string = ''.join(item)
        print(string)
#        
#        