# -*- coding: utf-8 -*-
'''
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
'''

from pypoly2tri.shapes import Point, Edge, Triangle
from pypoly2tri.advancing_front import AdvancingFront, Node


class Basin(object):

    def __init__(self):
        self.left_node = None
        self.bottom_node = None
        self.right_node = None
        self.width = 0.0
        self.left_highest = False

    def Clear(self):
        self.left_node = None
        self.bottom_node = None
        self.right_node = None
        self.width = 0.0
        self.left_highest = False


class EdgeEvent(object):

    def __init__(self):
        self.constrained_edge = None
        self.right = False


class SweepContext(object):

    def __init__(self, polyline):
        self.basin = Basin()
        self.edge_event = EdgeEvent()
        self.edge_list = []

        self.points_ = polyline
        self.triangles_ = []
        self.map_ = []
        self.kAlpha = .3

        self.InitEdges(self.points_)

        self.front_ = None
        self.head_ = None
        self.tail_ = None
        self.af_head_ = None
        self.af_middle_ = None
        self.af_tail_ = None

    def AddHole(self, polyline):
        self.InitEdges(polyline)
        self.points_.extend(polyline)

    def AddPoint(self, point):
        self.points_.append(point)

    def GetTriangles(self):
        return self.triangles_

    def GetMap(self):
        return self.map_

    def InitTriangulation(self):
        import numpy
        xs = numpy.array([item.x for item in self.points_])
        ys = numpy.array([item.y for item in self.points_])
        xmin = xs.min()
        xmax = xs.max()
        ymin = ys.min()
        ymax = ys.max()

        dx = self.kAlpha * (xmax - xmin)
        dy = self.kAlpha * (ymax - ymin)
        self.head_ = Point(xmax + dx, ymin - dy)
        self.tail_ = Point(xmin - dx, ymin - dy)

        from operator import attrgetter
        self.points_ = sorted(self.points_, key=attrgetter('y', 'x'))
#        self.points_.reverse()

    def InitEdges(self, polyline):
        self.edge_list.extend(
            [Edge(line1, line2) for line1, line2 in zip(polyline, polyline[1:] + polyline[:1])])

    def GetPoint(self, index):
        return self.points_[index]

    def AddToMap(self, triangle):
        self.map_.append(triangle)

    def LocateNode(self, point):
        return self.front_.LocateNode(point.x)

    def CreateAdvancingFront(self, nodes):
        triangle = Triangle(self.points_[0], self.tail_, self.head_)
        self.map_.append(triangle)

        self.af_head_ = Node(triangle.GetPoint(1), triangle)
        self.af_middle_ = Node(triangle.GetPoint(0), triangle)
        self.af_tail_ = Node(triangle.GetPoint(2))
        self.front_ = AdvancingFront(self.af_head_, self.af_tail_)

        self.af_head_.next = self.af_middle_
        self.af_middle_.next = self.af_tail_
        self.af_middle_.prev = self.af_head_
        self.af_tail_.prev = self.af_middle_

    def RemoveNode(self, node):
        del node

    def MapTriangleToNodes(self, t):
        for i in range(3):
            if not t.GetNeighbor(i):
                n = self.front_.LocatePoint(t.PointCW(t.GetPoint(i)))
                if n is not None:
                    n.triangle = t

    def RemoveFromMap(self, triangle):
        self.map_.remove(triangle)

    def MeshClean(self, triangle):
        if triangle is not None and not triangle.IsInterior():
            triangle.IsInterior(True)
            self.triangles_.append(triangle)
            for i in range(3):
                if not triangle.constrained_edge[i]:
                    self.MeshClean(triangle.GetNeighbor(i))

    def front(self):
        return self.front_

    def point_count(self):
        return len(self.points_)

    def set_head(self, p1):
        self.head_ = p1

    def head(self):
        return self.head_

    def set_tail(self, p1):
        self.tail_ = p1

    def tail(self):
        return self.tail_
