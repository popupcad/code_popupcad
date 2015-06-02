"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import numpy

class Node(object):
    '''
    class containing all the functionality for the node of an acyclic directed graph    
    '''
    def __init__(self):
        self.id = id(self)
        self.network = None
    def setnetwork(self,network):
        self.network = network
    def parents(self):
        return self.network.itemparents(self.network.A,self)
    def children(self):
        return self.network.itemchildren(self.network.A,self)
    def allparents(self):
        return self.network.itemparents(self.network.B,self)
    def allchildren(self):
        return self.network.itemchildren(self.network.B,self)
            
class Data(object):
    '''Generic Data structure which is held by a custom node'''
    def __init__(self,name):
        super(Data,self).__init__()
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name

class AcyclicDirectedGraph(object):
    '''Graph which holds the methods for an acyclic directed graph'''
    def __init__(self,nodes=None,connections=None):
        self.nodes = []
        self.connections = []
        self.A = numpy.array([[]])
        if nodes!=None:
            self.addnodes(nodes)
            if connections!=None:
                self.addconnections(connections)

    def sequencevalid(self,sequence):
        '''checks whether the nodes of a given sequence are correctly ordered (below their children or above their parents)'''
        allparents = self.allparents()
        allchildren = self.allchildren()
        for ii,node in enumerate(sequence):
            above = set(sequence[:ii])
            below = set(sequence[ii+1:])

            children = set(allchildren[node])
            parents = set(allparents[node])

            if len(above.intersection(children))>0:
                return False
            if len(below.intersection(parents))>0:
                return False
        return True

    def subsequencecomplete(self,sequence):
        '''checks whether a given sequence's nodes have all their parents in the subsequence as well'''
        allparents = self.allparents()
        allchildren = self.allchildren()
        for ii,node in enumerate(sequence):
            above = set(sequence[:ii])
            below = set(sequence[ii+1:])

            children = set(allchildren[node])
            parents = set(allparents[node])
            pass

            if len(parents.difference(above))>0:
                return False
            if len(above.intersection(children))>0:
                return False
            if len(below.intersection(parents))>0:
                return False
        return True

    def cleannodes(self):
        '''remove duplicate nodes and rebuild internal connection matrix'''
#        self.nodes = sorted(list(set(self.nodes)))
        self.nodes = list(set(self.nodes))
        self.buildAB()
        
    def cleanconnections(self):
        '''remove duplicate connections and rebuild internal connection matrix'''
        self.connections = list(set(self.connections))
        self.buildAB()

    def addnodes(self,nodes):
        '''add a list of nodes to the network'''
        for node in nodes:
            if isinstance(node,Node):
                node.setnetwork(self)
        self.nodes.extend(nodes)
        self.cleannodes()

    def addconnections(self,connections):
        '''add a list of connections to the network and recalculate internal stuff'''
        for parent,child in connections:
            if parent in self.nodes and child in self.nodes:
                if parent in self.allchildren_item(child):
                    raise(Exception('the parent is a child'))
                else:
                    self.connections.append((parent,child))
        self.cleanconnections()

    def buildAB(self):
        '''build internal representation of directed connections'''
        A,self.forwardindex,self.reverseindex = self.findA(self.nodes,self.connections)
        self.A = A
        self.B = self.findB(A)

    @staticmethod
    def findA(nodes,connections):
        '''return a single-step connection matrix'''        
        m  = len(nodes)
        A = numpy.zeros((m,m),dtype = bool)
        
        forwardindex = dict([(node,ii) for ii,node in enumerate(nodes)])
        reverseindex = dict([(ii,node) for ii,node in enumerate(nodes)])
        
        for connection in connections:
            A[forwardindex[connection[0]],forwardindex[connection[1]]] = 1
            
        return A, forwardindex, reverseindex
        
    @staticmethod    
    def findB(A):
        '''find all connections between nodes...brute force method.'''
        B = A.copy()
        lastB = numpy.zeros(A.shape)
        while not (B == lastB).all():
            lastB = B
            B = B.dot(A)+B
        return lastB
    def parents(self):
        '''return the direct parents of nodes'''
        parents = {}
        for child in self.nodes:
            parents[child] = self.itemparents(self.A,child)
        return parents
    def children(self):
        '''return the direct children of nodes'''
        parents = {}
        for child in self.nodes:
            parents[child] = self.itemchildren(self.A,child)
        return parents
    def allparents(self):
        '''return all parents of nodes'''
        parents = {}
        for child in self.nodes:
            parents[child] = self.itemparents(self.B,child)
        return parents
    def allchildren(self):
        '''return all children of nodes'''
        parents = {}
        for child in self.nodes:
            parents[child] = self.itemchildren(self.B,child)
        return parents
    def parents_item(self,child):
        '''return the direct parents of nodes'''
        return self.itemparents(self.A,child)
    def children_item(self,child):
        '''return the direct children of nodes'''
        return self.itemchildren(self.A,child)
    def allparents_item(self,child):
        '''return all parents of nodes'''
        return self.itemparents(self.B,child)
    def allchildren_item(self,child):
        '''return all children of nodes'''
        return self.itemchildren(self.B,child)
        
    def itemparents(self,C,child):
        '''return the parents of a particular node.  The input connection matrix C determines what type of relationship'''
#        array = numpy.array(C)
        ii = self.forwardindex[child]
        itemparents = C[:,ii].nonzero()[0].tolist()            
        itemparents = [self.reverseindex[item] for item in itemparents ]
        return itemparents
        
    def itemchildren(self,C,child):
        '''return the children of a particular node.  The input connection matrix C determines what type of relationship'''
#        array = numpy.array(C)
        ii = self.forwardindex[child]
        itemparents = C[ii,:].nonzero()[0].tolist()            
        itemparents = [self.reverseindex[item] for item in itemparents ]
        return itemparents
            
if __name__=='__main__':
    pass