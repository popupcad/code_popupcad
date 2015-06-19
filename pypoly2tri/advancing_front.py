# -*- coding: utf-8 -*-
'''
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
'''


class Node(object):

    def __init__(self, p, t=None):
        self.point = p
        self.triangle = t
        self.value = p.x
        self.next = None
        self.prev = None


class AdvancingFront(object):

    def __init__(self, head, tail):
        self.head_ = head
        self.tail_ = tail
        self.search_node_ = head

    def LocateNode(self, x):
        node = self.search_node_

        if x < node.value:
            dummy = node.prev
            while (dummy is not None):
                node = dummy
                if x >= node.value:
                    self.search_node_ = node
                    return node
#                node = node.prev
                dummy = node.prev

        else:
            dummy = node.next
            while (dummy is not None):
                node = dummy
                if x < node.value:
                    self.search_node_ = node.prev
                    return node.prev
                dummy = node.next

        return None

    def FindSearchNode(self, x):
        return self.search_node_

    def LocatePoint(self, point):
        px = point.x
        node = self.FindSearchNode(px)
        nx = node.point.x

        if px == nx:
            if point != node.point:
                if point == node.prev.point:
                    node = node.prev
                elif point == node.next.point:
                    node = node.next
                else:
                    assert(0)
        elif px < nx:
            dummy = node.prev
            while(dummy is not None):
                node = dummy
                if point == node.point:
                    break
                dummy = node.prev

        else:
            dummy = node.next
            while(dummy is not None):
                node = dummy
                if point == node.point:
                    break
                dummy = node.next

        if node is not None:
            self.search_node_ = node
        return node

    def head(self):
        return self.head_

    def set_head(self, node):
        self.head_ = node

    def tail(self):
        return self.tail_

    def set_tail(self, node):
        self.tail_ = node

    def search(self):
        return self.search_node_

    def set_search(self, node):
        self.search_node_ = node
