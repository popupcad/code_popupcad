# -*- coding: utf-8 -*-
'''
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
'''

from pypoly2tri.utils import EPSILON, Orientation, Orient2d, InScanArea
from pypoly2tri.shapes import Triangle
from pypoly2tri.advancing_front import Node
# ii=0


class Sweep(object):

    def __init__(self):
        self.nodes_ = []

    def Triangulate(self, tcx):
        tcx.InitTriangulation()
        tcx.CreateAdvancingFront(self.nodes_)
        self.SweepPoints(tcx)
        self.FinalizationPolygon(tcx)

    def SweepPoints(self, tcx):
        for ii in range(1, tcx.point_count()):
            point = tcx.GetPoint(ii)
            node = self.PointEvent(tcx, point)
            for jj in range(len(point.edge_list)):
                self.EdgeEvent(tcx, point.edge_list[jj], node)

    def FinalizationPolygon(self, tcx):
        t = tcx.front().head().next.triangle
        p = tcx.front().head().next.point
        while not t.GetConstrainedEdgeCW(p):
            t = t.NeighborCCW(p)
        tcx.MeshClean(t)

    def PointEvent(self, tcx, point):
        node = tcx.LocateNode(point)
        new_node = self.NewFrontTriangle(tcx, point, node)
        if point.x <= (node.point.x + EPSILON):
            self.Fill(tcx, node)
        self.FillAdvancingFront(tcx, new_node)
        return new_node

    def EdgeEvent(self, *args):
        if len(args) == 3:
            self.EdgeEvent1(*args)
        elif len(args) == 5:
            self.EdgeEvent2(*args)
        else:
            raise Exception

    def EdgeEvent1(self, tcx, edge, node):
        tcx.edge_event.constrained_edge = edge
        tcx.edge_event.right = edge.p.x > edge.q.x
        if (self.IsEdgeSideOfTriangle(node.triangle, edge.p, edge.q)):
            return
        self.FillEdgeEvent(tcx, edge, node)
        self.EdgeEvent(tcx, edge.p, edge.q, node.triangle, edge.q)

    def EdgeEvent2(self, tcx, ep, eq, triangle, point):
        if self.IsEdgeSideOfTriangle(triangle, ep, eq):
            return
        p1 = triangle.PointCCW(point)
        o1 = Orient2d(eq, p1, ep)
        if o1 == Orientation.COLLINEAR:
            assert(False)
        p2 = triangle.PointCW(point)
        o2 = Orient2d(eq, p2, ep)
        if o2 == Orientation.COLLINEAR:
            assert(False)
        if o1 == o2:
            if o1 == Orientation.CW:
                triangle = triangle.NeighborCCW(point)
            else:
                triangle = triangle.NeighborCW(point)
#            if triangle==None:
#                assert(0)
            self.EdgeEvent(tcx, ep, eq, triangle, point)
        else:
            self.FlipEdgeEvent(tcx, ep, eq, triangle, point)

    def IsEdgeSideOfTriangle(self, triangle, ep, eq):
        index = triangle.EdgeIndex(ep, eq)
        if index != -1:
            triangle.MarkConstrainedEdge(index)
            t = triangle.GetNeighbor(index)
            if t:
                t.MarkConstrainedEdge(ep, eq)
            return True
        return False

    def NewFrontTriangle(self, tcx, point, node):
        p1 = point
        p2 = node.point
        p3 = node.next.point

        triangle = Triangle(p1, p2, p3)
        triangle.MarkNeighbor(node.triangle)
        tcx.AddToMap(triangle)
        new_node = Node(point)
        self.nodes_.append(new_node)
        new_node.next = node.next
        new_node.prev = node
        node.next.prev = new_node
        node.next = new_node
        if not self.Legalize(tcx, triangle):
            tcx.MapTriangleToNodes(triangle)
        return new_node

    def Fill(self, tcx, node):
        p1 = node.prev.point
        if p1 is None:
            assert(0)
        p2 = node.point
        if p2 is None:
            assert(0)
        p3 = node.next.point
        if p3 is None:
            assert(0)
        triangle = Triangle(p1, p2, p3)
        triangle.MarkNeighbor(node.prev.triangle)
        triangle.MarkNeighbor(node.triangle)
        tcx.AddToMap(triangle)
        node.prev.next = node.next
        node.next.prev = node.prev
        if not self.Legalize(tcx, triangle):
            tcx.MapTriangleToNodes(triangle)

    def FillAdvancingFront(self, tcx, n):
        from math import pi
        node = n.next

        while node.next is not None:
            angle = self.HoleAngle(node)
            if angle > pi / 2 or angle < -pi / 2:
                break
            self.Fill(tcx, node)
            node = node.next

        node = n.prev

        while node.prev is not None:
            angle = self.HoleAngle(node)
            if angle > pi / 2 or angle < -pi / 2:
                break
            self.Fill(tcx, node)
            node = node.prev

        if (n.next is not None and n.next.next is not None):
            angle = self.BasinAngle(n)
            if angle < 3. * pi / 4:
                self.FillBasin(tcx, n)

    def BasinAngle(self, node):
        from math import atan2
        ax = node.point.x - node.next.next.point.x
        ay = node.point.y - node.next.next.point.y
        return atan2(ay, ax)

    def HoleAngle(self, node):
        from math import atan2
        ax = node.next.point.x - node.point.x
        ay = node.next.point.y - node.point.y
        bx = node.prev.point.x - node.point.x
        by = node.prev.point.y - node.point.y
        return atan2(ax * by - ay * bx, ax * bx + ay * by)

    def Legalize(self, tcx, t):
        for i in range(3):
            if t.delaunay_edge[i]:
                continue
            ot = t.GetNeighbor(i)
            if isinstance(ot, Triangle):
                p = t.GetPoint(i)
                op = ot.OppositePoint(t, p)
                oi = ot.Index(op)
                if ot.constrained_edge[oi] or ot.delaunay_edge[oi]:
                    t.constrained_edge[i] = ot.constrained_edge[oi]
                    continue
                inside = self.Incircle(p, t.PointCCW(p), t.PointCW(p), op)
                if inside:
                    t.delaunay_edge[i] = True
                    ot.delaunay_edge[oi] = True
                    self.RotateTrianglePair(t, p, ot, op)
                    not_legalized = not self.Legalize(tcx, t)
                    if not_legalized:
                        tcx.MapTriangleToNodes(t)
                    not_legalized = not self.Legalize(tcx, ot)
                    if not_legalized:
                        tcx.MapTriangleToNodes(ot)
                    t.delaunay_edge[i] = False
                    ot.delaunay_edge[oi] = False
                    return True
        return False

    def Incircle(self, pa, pb, pc, pd):
        adx = pa.x - pd.x
        ady = pa.y - pd.y
        bdx = pb.x - pd.x
        bdy = pb.y - pd.y

        adxbdy = adx * bdy
        bdxady = bdx * ady
        oabd = adxbdy - bdxady
        if oabd <= 0:
            return False

        cdx = pc.x - pd.x
        cdy = pc.y - pd.y

        cdxady = cdx * ady
        adxcdy = adx * cdy
        ocad = cdxady - adxcdy
        if ocad <= 0:
            return False

        bdxcdy = bdx * cdy
        cdxbdy = cdx * bdy

        alift = adx * adx + ady * ady
        blift = bdx * bdx + bdy * bdy
        clift = cdx * cdx + cdy * cdy

        det = alift * (bdxcdy - cdxbdy) + blift * ocad + clift * oabd

        return det > 0

    def RotateTrianglePair(self, t, p, ot, op):
        n1 = t.NeighborCCW(p)
        n2 = t.NeighborCW(p)
        n3 = ot.NeighborCCW(op)
        n4 = ot.NeighborCW(op)

        ce1 = t.GetConstrainedEdgeCCW(p)
        ce2 = t.GetConstrainedEdgeCW(p)
        ce3 = ot.GetConstrainedEdgeCCW(op)
        ce4 = ot.GetConstrainedEdgeCW(op)

        de1 = t.GetDelunayEdgeCCW(p)
        de2 = t.GetDelunayEdgeCW(p)
        de3 = ot.GetDelunayEdgeCCW(op)
        de4 = ot.GetDelunayEdgeCW(op)

        t.Legalize(p, op)
        ot.Legalize(op, p)

        ot.SetDelunayEdgeCCW(p, de1)
        t.SetDelunayEdgeCW(p, de2)
        t.SetDelunayEdgeCCW(op, de3)
        ot.SetDelunayEdgeCW(op, de4)

        ot.SetConstrainedEdgeCCW(p, ce1)
        t.SetConstrainedEdgeCW(p, ce2)
        t.SetConstrainedEdgeCCW(op, ce3)
        ot.SetConstrainedEdgeCW(op, ce4)

        t.ClearNeighbors()
        ot.ClearNeighbors()
        if (n1):
            ot.MarkNeighbor(n1)
        if (n2):
            t.MarkNeighbor(n2)
        if (n3):
            t.MarkNeighbor(n3)
        if (n4):
            ot.MarkNeighbor(n4)
        t.MarkNeighbor(ot)

    def FillBasin(self, tcx, node):
        global ii
        if (Orient2d(node.point,
                     node.next.point,
                     node.next.next.point) == Orientation.CCW):
            tcx.basin.left_node = node.next.next
        else:
            tcx.basin.left_node = node.next

        tcx.basin.bottom_node = tcx.basin.left_node
        while (tcx.basin.bottom_node.next and tcx.basin.bottom_node.point.y >=
               tcx.basin.bottom_node.next.point.y):
            tcx.basin.bottom_node = tcx.basin.bottom_node.next
        if (tcx.basin.bottom_node == tcx.basin.left_node):
            return

        tcx.basin.right_node = tcx.basin.bottom_node
        while (tcx.basin.right_node.next and tcx.basin.right_node.point.y <
               tcx.basin.right_node.next.point.y):
            tcx.basin.right_node = tcx.basin.right_node.next

        if (tcx.basin.right_node == tcx.basin.bottom_node):
            return

        tcx.basin.width = tcx.basin.right_node.point.x - \
            tcx.basin.left_node.point.x
        tcx.basin.left_highest = tcx.basin.left_node.point.y > tcx.basin.right_node.point.y
        ii = 0
        self.FillBasinReq(tcx, tcx.basin.bottom_node)

    def FillBasinReq(self, tcx, node):
        #        global ii
        if self.IsShallow(tcx, node):
            return
        self.Fill(tcx, node)
        if node.prev == tcx.basin.left_node and node.next == tcx.basin.right_node:
            return
        elif node.prev == tcx.basin.left_node:
            o = Orient2d(node.point, node.next.point, node.next.next.point)
            if o == Orientation.CW:
                return
            node = node.next
        elif node.next == tcx.basin.right_node:
            o = Orient2d(node.point, node.prev.point, node.prev.prev.point)
            if o == Orientation.CCW:
                return
            node = node.prev
        else:
            if node.prev.point.y < node.next.point.y:
                node = node.prev
            else:
                node = node.next
#        print('recursion depth: ',ii)
#        ii+=1
        self.FillBasinReq(tcx, node)

    def IsShallow(self, tcx, node):
        if tcx.basin.left_highest:
            height = tcx.basin.left_node.point.y - node.point.y
        else:
            height = tcx.basin.right_node.point.y - node.point.y

        if tcx.basin.width > height:
            return True
        return False

    def FillEdgeEvent(self, tcx, edge, node):
        if tcx.edge_event.right:
            self.FillRightAboveEdgeEvent(tcx, edge, node)
        else:
            self.FillLeftAboveEdgeEvent(tcx, edge, node)

    def FillRightAboveEdgeEvent(self, tcx, edge, node):
        while node.next.point.x < edge.p.x:
            if Orient2d(edge.q, node.next.point, edge.p) == Orientation.CCW:
                self.FillRightBelowEdgeEvent(tcx, edge, node)
            else:
                node = node.next

    def FillRightBelowEdgeEvent(self, tcx, edge, node):
        if node.point.x < edge.p.x:
            if Orient2d(
                    node.point,
                    node.next.point,
                    node.next.next.point) == Orientation.CCW:
                self.FillRightConcaveEdgeEvent(tcx, edge, node)
            else:
                self.FillRightConvexEdgeEvent(tcx, edge, node)
                self.FillRightBelowEdgeEvent(tcx, edge, node)

    def FillRightConcaveEdgeEvent(self, tcx, edge, node):
        self.Fill(tcx, node.next)
        if node.next.point != edge.p:
            if Orient2d(edge.q, node.next.point, edge.p) == Orientation.CCW:
                if Orient2d(
                        node.point,
                        node.next.point,
                        node.next.next.point) == Orientation.CCW:
                    self.FillRightConcaveEdgeEvent(tcx, edge, node)
                else:
                    pass

    def FillRightConvexEdgeEvent(self, tcx, edge, node):
        if Orient2d(
                node.next.point,
                node.next.next.point,
                node.next.next.next.point) == Orientation.CCW:
            self.FillRightConcaveEdgeEvent(tcx, edge, node.next)
        else:
            if Orient2d(
                    edge.q,
                    node.next.next.point,
                    edge.p) == Orientation.CCW:
                self.FillRightConvexEdgeEvent(tcx, edge, node.next)
            else:
                pass

    def FillLeftAboveEdgeEvent(self, tcx, edge, node):
        while node.prev.point.x > edge.p.x:
            if Orient2d(edge.q, node.prev.point, edge.p) == Orientation.CW:
                self.FillLeftBelowEdgeEvent(tcx, edge, node)
            else:
                node = node.prev

    def FillLeftBelowEdgeEvent(self, tcx, edge, node):
        if node.point.x > edge.p.x:
            if Orient2d(
                    node.point,
                    node.prev.point,
                    node.prev.prev.point) == Orientation.CW:
                self.FillLeftConcaveEdgeEvent(tcx, edge, node)
            else:
                self.FillLeftConvexEdgeEvent(tcx, edge, node)
                self.FillLeftBelowEdgeEvent(tcx, edge, node)

    def FillLeftConvexEdgeEvent(self, tcx, edge, node):
        if Orient2d(
                node.prev.point,
                node.prev.prev.point,
                node.prev.prev.prev.point) == Orientation.CW:
            self.FillLeftConcaveEdgeEvent(tcx, edge, node.prev)
        else:
            if Orient2d(
                    edge.q,
                    node.prev.prev.point,
                    edge.p) == Orientation.CW:
                self.FillLeftConvexEdgeEvent(tcx, edge, node.prev)
            else:
                pass

    def FillLeftConcaveEdgeEvent(self, tcx, edge, node):
        self.Fill(tcx, node.prev)
        if node.prev.point != edge.p:
            if Orient2d(edge.q, node.prev.point, edge.p) == Orientation.CW:
                if Orient2d(
                        node.point,
                        node.prev.point,
                        node.prev.prev.point) == Orientation.CW:
                    self.FillLeftConcaveEdgeEvent(tcx, edge, node)
                else:
                    pass

    def FlipEdgeEvent(self, tcx, ep, eq, t, p):
        ot = t.NeighborAcross(p)
        op = ot.OppositePoint(t, p)
        if ot is None:
            assert(0)

        if InScanArea(p, t.PointCCW(p), t.PointCW(p), op):
            self.RotateTrianglePair(t, p, ot, op)
            tcx.MapTriangleToNodes(t)
            tcx.MapTriangleToNodes(ot)

            if p == eq and op == ep:
                if eq == tcx.edge_event.constrained_edge.q and ep == tcx.edge_event.constrained_edge.p:
                    t.MarkConstrainedEdge(ep, eq)
                    ot.MarkConstrainedEdge(ep, eq)
                    self.Legalize(tcx, t)
                    self.Legalize(tcx, ot)
                else:
                    pass
            else:
                o = Orient2d(eq, op, ep)
                t = self.NextFlipTriangle(tcx, int(o), t, ot, p, op)
                self.FlipEdgeEvent(tcx, ep, eq, t, p)
        else:
            newP = self.NextFlipPoint(ep, eq, ot, op)
            self.FlipScanEdgeEvent(tcx, ep, eq, t, ot, newP)
            self.EdgeEvent(tcx, ep, eq, t, p)

    def NextFlipTriangle(self, tcx, o, t, ot, p, op):
        if o == Orientation.CCW:
            edge_index = ot.EdgeIndex(p, op)
            ot.delaunay_edge[edge_index] = True
            self.Legalize(tcx, ot)
            ot.ClearDelaunayEdges()
            return t

        edge_index = t.EdgeIndex(p, op)

        t.delaunay_edge[edge_index] = True
        self.Legalize(tcx, t)
        t.ClearDelaunayEdges()
        return ot

    def NextFlipPoint(self, ep, eq, ot, op):
        o2d = Orient2d(eq, op, ep)
        if o2d == Orientation.CW:
            return ot.PointCCW(op)
        elif o2d == Orientation.CCW:
            return ot.PointCW(op)
        else:
            assert(0)

    def FlipScanEdgeEvent(self, tcx, ep, eq, flip_triangle, t, p):
        ot = t.NeighborAcross(p)
        op = ot.OppositePoint(t, p)

        if t.NeighborAcross(p) is None:
            assert(0)
        if InScanArea(
                eq,
                flip_triangle.PointCCW(eq),
                flip_triangle.PointCW(eq),
                op):
            self.FlipEdgeEvent(tcx, eq, op, ot, op)
        else:
            newP = self.NextFlipPoint(ep, eq, ot, op)
            self.FlipScanEdgeEvent(tcx, ep, eq, flip_triangle, ot, newP)
