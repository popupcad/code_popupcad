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
    def ancestors(self):
        return self.network.itemparents(self.network.B,self)
    def decendents(self):
        return self.network.itemchildren(self.network.B,self)
            
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

    def sequence_complete_valid(self,sequence):
        '''checks whether a given sequence's nodes have all their parents in the subsequence as well'''
        for ii,node in enumerate(sequence):
            above = set(sequence[:ii])
            below = set(sequence[ii+1:])

            ancestors = set(node.ancestors())
            decendents = set(node.decendents())

            if len(ancestors.difference(above))>0:
                return False
            if len(decendents.difference(below))>0:
                return False
            if len(above.intersection(decendents))>0:
                return False
            if len(below.intersection(ancestors))>0:
                return False
        return True

    def process(self):
        self.forwardindex,self.reverseindex = self.build_indeces(self.nodes)
        self.A,self.B = self.buildAB(self.nodes,self.connections,self.forwardindex)

    def addnodes(self,nodes):
        '''add a list of nodes to the network'''
        for node in nodes:
            if isinstance(node,Node):
                node.setnetwork(self)
        self.nodes.extend(nodes)
        self.nodes = list(set(self.nodes))
        self.process()

    def addconnections(self,connections):
        '''add a list of connections to the network and recalculate internal stuff'''
        for parent,child in connections:
            if parent in self.nodes and child in self.nodes:
                if parent in child.decendents():
                    raise(Exception('the parent is a child'))
                else:
                    self.connections.append((parent,child))
        self.connections = list(set(self.connections))
        self.process()

    @staticmethod    
    def build_indeces(nodes):
        forwardindex = dict([(node,ii) for ii,node in enumerate(nodes)])
        reverseindex = dict([(ii,node) for ii,node in enumerate(nodes)])
        return forwardindex,reverseindex

    @staticmethod    
    def buildAB(nodes,connections,forwardindex):
        '''build internal representation of directed connections'''
        m  = len(nodes)
        A = numpy.zeros((m,m),dtype = bool)
        for connection in connections:
            A[forwardindex[connection[0]],forwardindex[connection[1]]] = 1
        B = A.copy()
        lastB = numpy.zeros(A.shape)
        while not (B == lastB).all():
            lastB = B
            B = B.dot(A)+B
        return A,B

    def itemparents(self,C,child):
        '''return the parents of a particular node.  The input connection matrix C determines what type of relationship'''
        return self.itemchildren(C.T,child)
        
    def itemchildren(self,C,parent):
        '''return the children of a particular node.  The input connection matrix C determines what type of relationship'''
#        array = numpy.array(C)
        ii = self.forwardindex[parent]
        itemparents = C[ii,:].nonzero()[0].tolist()            
        itemparents = [self.reverseindex[item] for item in itemparents ]
        return itemparents
            
if __name__=='__main__':
    pass