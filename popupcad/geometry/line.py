# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
        
class Line(object):
    def __init__(self,v1,v2):
        super(Line,self).__init__()
        self.vertex1 = v1
        self.vertex2 = v2

    def vertices(self):
        return [self.vertex1,self.vertex2]  

    def lines(self):
        return [self]

    def p1(self):
        return self.vertex1.p()
    def p2(self):
        return self.vertex2.p()
    def v(self):
        return self.p2() - self.p1()
    def lv(self):
        v = self.v()
        return (v.dot(v))**.5        

    def output_interactive(self):
        from popupcad.interactive.interactiveedge import InteractiveEdge
        v = InteractiveEdge(self.vertex1.gen_interactive(),self.vertex2.gen_interactive())
        return v

class ReferenceLine(Line):
    def output_interactive(self):
        from popupcad.interactive.interactiveedge import ReferenceEdge
        v = ReferenceEdge(self.vertex1.gen_interactive(),self.vertex2.gen_interactive())
        v.handleupdate()
        return v
