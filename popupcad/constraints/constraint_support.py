# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import sympy

class Variable(sympy.Symbol):
    pass

class UnknownType(Exception):
    pass        
        
class WrongArguments(Exception):
    pass   

class SymbolicVertex(object):

    def __init__(self, id):
        self.id = id

    def p(self):
        p_x = Variable(str(self) + '_x')
        p_y = Variable(str(self) + '_y')
        return sympy.Matrix([p_x, p_y, 0])

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.id == other.id
        return False

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        return 'vertex' + str(self.id)


class SymbolicLine(object):

    def __init__(self, v1, v2):
        self.vertex1 = v1
        self.vertex2 = v2

    def p1(self):
        return self.vertex1.p()

    def p2(self):
        return self.vertex2.p()

    def v(self):
        return self.p2() - self.p1()

    def lv(self):
        v = self.v()
        return (v.dot(v))**.5
