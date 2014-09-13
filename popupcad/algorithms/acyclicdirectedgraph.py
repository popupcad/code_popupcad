# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""



import numpy
import yaml

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
    def minmaxindex(self,sequence):
        return self.network.minmaxindex(self,sequence)
    def sortedallchildrensequence(self):
        return self.network.sortedallchildrensequence(self)
            
class CustomNode(Node):
    '''Child of Node class that can hold data'''
    def __init__(self,data):
        super(CustomNode,self).__init__()
        self.data = data
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return str(self.data)

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
        self.A = [[]]
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

    def minmaxindex(self,node,sequence):
        '''returns the minimum and maximum position in a sequence any given node can reside in to keep a sequence correctly ordered'''
        allparents = self.allparents()
        allchildren = self.allchildren()
        
        parentindeces = [sequence.index(parent) for parent in allparents[node] if parent in sequence]
        childindeces = [sequence.index(child) for child in allchildren[node] if child in sequence]

        i_max = 0
        i_min = len(sequence)-1
        if len(parentindeces)>0:
            i_max = max(parentindeces)+1
        if len(childindeces)>0:
            i_min = min(childindeces)-1
        return i_max,i_min
                
    def addnode(self,node):
        '''add a node to the network'''
        if isinstance(node,Node):
            node.setnetwork(self)
        n=node
        self.nodes.append(n)
        self.cleannodes()
        
        self.buildAB()
        
    def cleannodes(self):
        '''remove duplicate nodes and rebuild internal connection matrix'''
        self.nodes = sorted(list(set(self.nodes)))
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
            self.nodes.append(node)
        self.cleannodes()

    def addconnection(self,parent,child):
        '''add a connection to the network and recalculate internal stuff'''
        self.addsingleconnection(parent,child)
        self.cleanconnections()

    def addsingleconnection(self,parent,child):
        '''just add the connection to the network, don't recalculate anything'''
        if parent in self.nodes and child in self.nodes:
            if parent in self.allchildren()[child]:
                raise(Exception('the parent is a child'))
            else:
                self.connections.append((parent,child))
        
    def addconnections(self,connections):
        '''add a list of connections to the network and recalculate internal stuff'''
        for parent,child in connections:
            self.addsingleconnection(parent,child)
        self.cleanconnections()

    def buildAB(self):
        '''build internal representation of directed connections'''
        A,self.forwardindex,self.reverseindex = self.findA(self.nodes,self.connections)
        self.A = A.tolist()
        self.B = self.findB(A).tolist()

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

    def itemparents(self,C,child):
        '''return the parents of a particular node.  The input connection matrix C determines what type of relationship'''
        array = numpy.array(C)
        ii = self.forwardindex[child]
        itemparents = array[:,ii].nonzero()[0].tolist()            
        itemparents = [self.reverseindex[item] for item in itemparents ]
        return itemparents
        
    def itemchildren(self,C,child):
        '''return the children of a particular node.  The input connection matrix C determines what type of relationship'''
        array = numpy.array(C)
        ii = self.forwardindex[child]
        itemparents = array[ii,:].nonzero()[0].tolist()            
        itemparents = [self.reverseindex[item] for item in itemparents ]
        return itemparents
            
    def fixsequence(self,sequence):
        '''given an input sequence, return a correctly-ordered sequence which contains all necessary parents.'''
        extendedlist = self.buildfullsequence(sequence)
        reverseindex = dict([(ii,item) for ii,item in enumerate(extendedlist)])
        
        subA,subB = self.generatesubmatrices(extendedlist)

        currentindeces = []
        for ii,item in enumerate(extendedlist):
            temp = subB.copy()
            temp[:,currentindeces]=1
            temp[currentindeces,:]=1
            nextrows = sum(temp,0)==len(currentindeces)
            nextrows = nextrows.nonzero()[0].tolist()
            currentindeces.extend(nextrows)
            if len(currentindeces)>=len(extendedlist):
                break
        sequence  = [reverseindex[item] for item in currentindeces]

        if len(set(extendedlist) - set(sequence))>0:
            raise(Exception('Invalid Sequence'))

        return sequence
        
    def buildfullsequence(self,sequence):
        '''for a given sequence, return a sequence which contains all necessary parent nodes'''
        extendedlist = []
        [extendedlist.extend(self.itemparents(self.B,item)) for item in sequence]
        extendedlist = (list(set(extendedlist+sequence)))
        return extendedlist

    def generatesubmatrices(self,sequence):
        '''return connection submatrices consisting just of nodes and connections in the given sequence.'''
        iis = [self.forwardindex[item] for item in sequence]
        subA = numpy.array(self.A)[iis,:][:,iis]
        subB = numpy.array(self.B)[iis,:][:,iis]
        return subA,subB        

    def sortedallchildrensequence(self,node):
        '''return a correctly ordered sequence of a node and all its children'''
        newsequence = self.fixsequence([node]+self.itemchildren(numpy.array(self.B),node))
        ii = newsequence.index(node)
        return newsequence[ii:]    

    def sortedallchildrenofnodes(self,nodes):
        '''return a correctly ordered sequence of nodes and all their children'''

        allchildren = [child for node in nodes for child in self.itemchildren(self.B,node)]
        newsequence = self.fixsequence(nodes+allchildren)
        iis = [newsequence.index(node)for node in nodes]
        ii = min(iis)
        return newsequence[ii:]    

if __name__=='__main__':
    pass