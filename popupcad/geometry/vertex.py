# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
   
import sympy
    
from popupcad.constraints.constraints import Variable, Constant
    
class Vertex(object):
    editable = ['pos','static']
    deletable = []
    
    roundvalue = 5
    def __init__(self):
        self.id = id(self)
        self._pos = None
        self.static = False        
        self._persistent = False

    def setstatic(self,test):
        self.static = test

    def is_persistent(self):
        try:
            self._persistent
        except AttributeError:
            self._persistent = False
        finally:
            return self._persistent

    def set_persistent(self,test):
        self._persistent = test

    def __str__(self):
        return 'vertex'+str(self.id)
        
    def vertices(self):
        return [self]

    def lines(self):
        return []

    def __hash__(self):
        return self.id

    def __eq__(self,other):
        if type(self)==type(other):
            return self.id == other.id
        return False
        
    def p(self):
        if self.static:
            p_x = Constant(str(self)+'_x')
            p_y = Constant(str(self)+'_y')
        else:
            p_x = Variable(str(self)+'_x')
            p_y = Variable(str(self)+'_y')
        return sympy.Matrix([p_x,p_y,0])

    def setpos(self,pos):
        import numpy
        pos = numpy.array(pos)
        pos.round(self.roundvalue)
        self._pos = tuple(pos.tolist())

    def getpos(self):
        try:
            if self._pos==None:
                self._pos = self.__pos
                del self.__pos
                return self._pos
            else:
                return self._pos
        except AttributeError:
            self._pos = self.__pos
            del self.__pos
            return self._pos
        

    def setsymbol(self,variable,value):
        p = self.p()
        if p[0] == variable:
            self.setpos((value,self.getpos()[1]))            
        if p[1] == variable:
            self.setpos((self.getpos()[0],value))
            
    def properties(self):
        from popupcad.widgets.propertyeditor import PropertyEditor
        return PropertyEditor(self)
        
    def copy(self,identical = True):
        new = Vertex()
        new.setpos(self.getpos())
        new.static = self.static
        if identical:
            new.id = self.id
        return new            

    def gen_interactive(self):
        from popupcad.graphics2d.interactivevertex import InteractiveVertex
        iv = InteractiveVertex(self)
        iv.updatefromsymbolic()
        return iv
        
    def get_interactive(self):
        try:
            return self.interactivevertex
        except AttributeError:
            self.interactivevertex = self.gen_interactive()
            return self.interactivevertex
