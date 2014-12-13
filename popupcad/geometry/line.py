# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.constraints.constraints import SymbolicLine

class Line(object):
    def __init__(self,v1,v2):
        super(Line,self).__init__()
        self.vertex1 = v1
        self.vertex2 = v2

    def vertices(self):
        return [self.vertex1,self.vertex2]  

    def constrained_shift(self,dxdy,constraintsystem):
        constraintsystem.constrained_shift([(self.vertex1,dxdy),(self.vertex2,dxdy)])

    def is_moveable(self):
        return True
        
    def constraints_ref(self):
        try:
            return self._constraints_ref
        except AttributeError:
            self._constraints_ref = SymbolicLine(self.vertex1.constraints_ref(),self.vertex2.constraints_ref())
            return self._constraints_ref

    def vertex_constraints_ref(self):
        return [self.vertex1.constraints_ref(),self.vertex2.constraints_ref()]

    def gen_interactive(self):
        from popupcad.graphics2d.interactiveedge import InteractiveEdge
        v = InteractiveEdge(self)
        v.handleupdate()
        return v

class ShapeLine(Line):
    pass

class ReferenceLine(Line):
    def gen_interactive(self):
        from popupcad.graphics2d.interactiveedge import ReferenceInteractiveEdge
        v = ReferenceInteractiveEdge(self)
        v.handleupdate()
        return v
        
