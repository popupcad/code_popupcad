# -*- coding: utf-8 -*-
'''
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
'''


class Point(object):
    def __init__(self,x=0.,y=0.):
        self.x = x
        self.y = y
        self.edge_list = []
    def set_zero(self):
        self.x = 0.
        self.y = 0.
    def set(self,x,y):
        self.x = x
        self.y = y
    def __neg__(self):
        return Point(-self.x,-self.y)
    def __sub__(self,a):
        return Point(a.x-self.x,a.y-self.y)
    def __add__(self,a):
        return Point(a.x+self.x,a.y+self.y)
    def __mul__(self,a):
        return Point(a*self.x,a*self.y)
    def Length(self):
        import math
        return math.sqrt(self.x*self.x+self.y*self.y)
    def Normalize(self):
        l=self.Length
        self.x /= l
        self.y /= l
        return l
    def __eq__(self,a):
        return self.x==a.x and self.y==a.y
    def __neq__(self,a):
        return not self==a
#        return self.x!=a.x and self.y!=a.y
    def toTuple(self):
        return self.x,self.y
def Dot(p,a):
    return p.x*a.x+p.y*a.y
def Cross_p(p,a):
    return p.x*a.y-p.y*a.x
def Cross_s(p,a):
    return Point(a*p.y,-a*p.x)
def Cross_s2(a,p):
    return Point(-a*p.y,a*p.x)
def Cross(*args):
    if isinstance(args[0],Point):
        if isinstance(args[1],Point):
            return Cross_p(*args)
        else:
            return Cross_s(*args)
    else:
        return Cross_s2(*args)

class Edge(object):
    def __init__(self,p1,p2):
        self.p = p1
        self.q = p2
        if p1.y>p2.y:
            self.q = p1
            self.p = p2
        elif p1.y == p2.y:
            if p1.x > p2.x:
                self.q = p1
                self.p = p2
            elif p1.x==p2.x:
#                raise(Exception('repeat points'))
                assert(False)
        self.q.edge_list.append(self)

class Triangle(object):
    def toList(self):
        return [point.toTuple() for point in self.points_]
    def __init__(self,a,b,c):
        self.points_ = [a,b,c]
        self.neighbors_ = [None]*3
        self.constrained_edge = [False]*3        
        self.delaunay_edge = [False]*3
        self.interior_ = False
    def MarkNeighbor_p(self,p1,p2,t):
        ii = self.points_.index(p1)
        jj = self.points_.index(p2)
        index = list(set(range(3)) - set([ii,jj]))[0]
        self.neighbors_[index] = t

    def MarkNeighbor_t(self,t):
        a = set(self.points_)
        b = set(t.points_)
        aa = list(a-b)[0]
        ii = self.points_.index(aa)
        bb = list(b-a)[0]
        jj = t.points_.index(bb)
        self.neighbors_[ii] = t
        t.neighbors_[jj] = self
        
    def MarkNeighbor(self,*args):
        if len(args)==1:
            self.MarkNeighbor_t(*args)
        elif len(args)==3:
            self.MarkNeighbor_p(*args)
        else:
            raise(Exception('wrong number of args'))
            
    def ClearNeighbors(self):
        self.neighbors_ = [None]*3
    def ClearDelaunayEdges(self):
        self.delaunay_edge = [False]*3
    def OppositePoint(self,t,p):
        cw = t.PointCW(p)
#        cw.x = p.x
#        cw.y = p.y
#        ham = self.PointCW(cw)
        return self.PointCW(cw)
    def Legalize_p(self,point):
        self.points_[1] = self.points_[0]
        self.points_[0] = self.points_[2]
        self.points_[2] = point
    def Legalize_t(self,opoint,npoint):
        if opoint == self.points_[0]:
            self.points_[1] = self.points_[0]
            self.points_[0] = self.points_[2]
            self.points_[2] = npoint
        elif opoint == self.points_[1]:
            self.points_[2] = self.points_[1]
            self.points_[1] = self.points_[0]
            self.points_[0] = npoint
        elif opoint == self.points_[2]:
            self.points_[0] = self.points_[2]
            self.points_[2] = self.points_[1]
            self.points_[1] = npoint
        else:
            assert(0)
    def Legalize(self,*args):
        if len(args)==1:
            self.Legalize_p(*args)
        elif len(args)==2:
            self.Legalize_t(*args)
        else:
            raise(Exception('wrong number of args'))
    def Index(self,p):
        return self.points_.index(p)
    def EdgeIndex(self,p1,p2):
        try:
            index1 = self.points_.index(p1)        
            index2 = self.points_.index(p2)        
            return list(set(range(3))-set([index1,index2]))[0]
        except ValueError:
            return -1
    def MarkConstrainedEdge_i(self,index):
        self.constrained_edge[index]=True
    def MarkConstrainedEdge_e(self,edge):
        index = self.EdgeIndex(edge.p,edge.q)
        self.MarkConstrainedEdge_i(index)
    def MarkConstrainedEdge_pq(self,p,q):
        index = self.EdgeIndex(p,q)
        self.MarkConstrainedEdge_i(index)
    def MarkConstrainedEdge(self,*args):
        if len(args)==1:
            if isinstance(args[0],Edge):
                self.MarkConstrainedEdge_e(*args)
            else:
                self.MarkConstrainedEdge_i(*args)
        elif len(args)==2:
            self.MarkConstrainedEdge_pq(*args)
    def PointCW(self,point):
        i = self.Index(point)
        return self.points_[(i-1)%3]
    def PointCCW(self,point):
        i = self.Index(point)
        return self.points_[(i+1)%3]
    def NeighborCW(self,point):
        ii = self.Index(point)
        return self.neighbors_[(ii+1)%3]
    def NeighborCCW(self,point):
        ii = self.Index(point)
        return self.neighbors_[(ii-1)%3]
    def GetConstrainedEdgeCCW(self,point):
        ii = self.Index(point)
        return self.constrained_edge[(ii-1)%3]
    def GetConstrainedEdgeCW(self,point):
        ii = self.Index(point)
        return self.constrained_edge[(ii+1)%3]
    def SetConstrainedEdgeCCW(self,point,ce):
        ii = self.Index(point)
        self.constrained_edge[(ii-1)%3] = ce
    def SetConstrainedEdgeCW(self,point,ce):
        ii = self.Index(point)
        self.constrained_edge[(ii+1)%3] = ce
    def GetDelunayEdgeCCW(self,point):
        ii = self.Index(point)
        return self.delaunay_edge[(ii-1)%3]
    def GetDelunayEdgeCW(self,point):
        ii = self.Index(point)
        return self.delaunay_edge[(ii+1)%3]
    def SetDelunayEdgeCCW(self,point,ce):
        ii = self.Index(point)
        self.delaunay_edge[(ii-1)%3] = ce
    def SetDelunayEdgeCW(self,point,ce):
        ii = self.Index(point)
        self.delaunay_edge[(ii+1)%3] = ce
    def NeighborAcross(self,point):
        ii = self.Index(point)
        return self.neighbors_[ii]
    def DebugPrint(self):
        print(self.points_)
    def GetPoint(self,index):
        return self.points_[index]        
    def GetNeighbor(self,index):
        return self.neighbors_[index]        
    def Contains(self,*args):
        if len(args)==1:
            item=args[0]
            if isinstance(item,Point):
                return item in self.points_
            elif isinstance(item,Edge):
                return item.p in self.points_ and item.q in self.points_
        else:
            return all([isinstance(item,Point) for item in args]) and all([item in self.points_ for item in args])
    def IsInterior(self,*args):
        if len(args)==0:
            return self.interior_
        else:
            self.interior_ = args[0]
    
        
def cmp(a,b):
    if a.y<b.y:
        return True
    elif a.y==b.y:
        if a.x<b.x:
            return True
    return False
    