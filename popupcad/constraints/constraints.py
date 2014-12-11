# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import sympy
import scipy.integrate as integ
import sympy.utilities 
import numpy
import PySide.QtGui as qg
import scipy.optimize as opt
import popupcad
from popupcad.filetypes.enum import enum

class Variable(sympy.Symbol):
    pass

class ConstraintSystem(object):
    atol = 1e-10
    rtol = 1e-10
    tfinal = 10
    tsegments = 10
    def __init__(self):
        self.constraints = []
        
    def link_vertex_builder(self,callback):
        self._vertex_builder = callback        
    def vertex_builder(self):
        try:
            return self._vertex_builder()
        except AttributeError:
            return []
        
    def add_constraint(self,constraint):
        self.constraints.append(constraint)
    
    def inilist(self,variables,ini):
        listout = []
        for item in variables:
            listout.append(ini[item])
        return listout
        
    def copy(self):
        new = ConstraintSystem()
        new.constraints = [constraint.copy() for constraint in self.constraints]
        return new

    def ini(self):
        objects = self.vertex_builder()
        ini = {}
        vertexdict = {}
        for vertex in objects:
            p = vertex.p()[0:2]

            vertexdict[p[0]]=vertex
            vertexdict[p[1]]=vertex

            pos = vertex.getpos()
            for key,value in zip(p,pos):     
                ini[key]=value
        return ini,vertexdict
        
        
    def regenerate(self):
        self.generated_variables = self.regenerate_inner()
        
    def regenerate_inner(self):
        from popupcad.geometry.vertex import BaseVertex
        from popupcad.geometry.line import Line
        
        if len(self.constraints)>0:
            objects = self.vertex_builder()
            if len(objects)>0:
                variables,qout = [],[]
                
                staticvertices = []
                for item in objects:
                    if isinstance(item,BaseVertex):
                        if item.is_static():
                            staticvertices.append(item)
                    elif isinstance(item,Line):
                        if item.vertex1.is_static():
                            staticvertices.append(item.vertex1)
                        if item.vertex2.is_static():
                            staticvertices.append(item.vertex2)
                constants = []
                for item in staticvertices:
                    constants.extend(SymbolicVertex(item.id).p()[:2])
                constants = list(set(constants))
    
                constraint_eqs = sympy.Matrix([equation for constraint in self.constraints for equation in constraint.generated_equations])
                allvariables = list(set([item for equation in constraint_eqs for item in list(equation.atoms(Variable))]))
                variables = list(set(allvariables)-set(constants))
                J = constraint_eqs.jacobian(sympy.Matrix(variables))
    
                f_constraints1 = sympy.utilities.lambdify(constants,constraint_eqs)
                f_J_1 = sympy.utilities.lambdify(constants,J)
    
                ini,vertexdict = self.ini()
                constvals = self.inilist(constants,ini)
    
                f_constraints2 = sympy.utilities.lambdify(variables,sympy.Matrix(f_constraints1(*constvals)))
                f_J_2 = sympy.utilities.lambdify(variables,sympy.Matrix(f_J_1(*constvals)))
    
                def dq(q):
                    qlist = q.flatten().tolist()
                    zero = f_constraints2(*(qlist))
                    zero = numpy.array(zero[:]).flatten()
                    n = len(zero)
                    m = len(q)
                    if m>n:
                        zero = numpy.r_[zero,[0]*(m-n)]
                    return zero        
    
                def j(q):
                    qlist = q.flatten().tolist()
                    jnum= f_J_2(*(qlist))
                    jnum=numpy.array(jnum[:])
                    m,n= jnum.shape
                    if n>m:
                        jnum= numpy.r_[jnum,numpy.zeros((n-m,n))]
                    return jnum  
                return dq,variables,j,vertexdict,constraint_eqs,constants,allvariables
        
    def update(self):
        try:
            dq,variables,j,vertexdict,constraint_eqs,constants,allvariables = self.generated_variables
            ini,vertexdict = self.ini()
            qout = opt.root(dq,numpy.array(self.inilist(variables,ini)),jac = j,tol = self.atol,method = 'lm')
            qout = qout.x.tolist()
    
    #            qout = opt.newton_krylov(dq2,numpy.array(self.inilist(variables,ini)),f_tol = self.atol,f_rtol = self.rtol)
    #            qout = opt.anderson(dq2,numpy.array(self.inilist(variables,ini)),f_tol = self.atol,f_rtol = self.rtol)
    #            qout = qout.tolist()
    #            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'hybr')
    #            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'linearmixing')
    #            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'excitingmixing')
    #            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'lm')
    #            qout = qout.x.tolist()
    
            for ii,variable in enumerate(variables):
                vertexdict[variable].setsymbol(variable,qout[ii])   
        except (AttributeError,TypeError):
            pass
    def constrained_shift(self,items):
        ini,vertexdict = self.ini()
        try:
            dq,variables,j,vertexdict,constraint_eqs,constants,allvariables = self.generated_variables
    
            dx_dict = {}
            for vertex,dxdy in items:
    #            vertex.shift(dxdy)
                key_x,key_y = vertex.constraints_ref().p()[:2]
                dx_dict[key_x]=dxdy[0]
                dx_dict[key_y]=dxdy[1]
    
    
            dx = numpy.zeros(len(variables))
            for key in dx_dict:
                if key in variables:
                    dx[variables.index(key)]=dx_dict[key]
#                elif key in allvariables:
#                    pass
#                else:
#                    vertexdict[key].setsymbol(key,ini[key]+dx_dict[key])   
                
    
            x0 = numpy.array(self.inilist(variables,ini))
            Jnum = j(x0)
            import scipy
            L,S,R = scipy.linalg.svd(Jnum)
            aS = abs(S)
            m = (aS>(aS[0]/100)).sum()
            n = len(variables)
            d = m-n
            rnull = R[d:]
            lnull = ((rnull**2).sum(1))**.5
            comp =   ((rnull*dx).sum(1))/lnull
            x_motion = (comp*rnull.T).sum(1)

            x = x0 + x_motion
    
            for ii,variable in enumerate(variables):
                vertexdict[variable].setsymbol(variable,x[ii])   
        except (AttributeError,TypeError):
            for vertex,dxdy in items:
                vertex.shift(dxdy)
        
    def cleanup(self):
        sketch_objects = self.vertex_builder()
        for ii in range(len(self.constraints))[::-1]:
            if self.constraints[ii].cleanup(sketch_objects)==Constraint.CleanupFlags.Deletable:
                self.constraints.pop(ii)


class ExactlyTwoPoints(object):
    def valid(self):
        return len(set(self.vertex_ids+self.vertices_in_lines()))==2
    def throwvalidityerror(self):
        raise(Exception('Need exactly two points'))
class AtLeastTwoPoints(object):
    def valid(self):
        return len(set(self.vertex_ids+self.vertices_in_lines()))>=2
    def throwvalidityerror(self):
        raise(Exception('Need at least two points'))
class ExactlyTwoLines(object):
    def valid(self):
        return len(self.segment_ids)==2
    def throwvalidityerror(self):
        raise(Exception('Need exactly two lines'))
class AtLeastTwoLines(object):
    def valid(self):
        return len(self.segment_ids)>=2
    def throwvalidityerror(self):
        raise(Exception('Need at least two lines'))
class AtLeastOneLine(object):
    def valid(self):
        return len(self.segment_ids)>=1
    def throwvalidityerror(self):
        raise(Exception('Need at least one line'))
class ExactlyOnePointOneLine(object):
    def valid(self):
        return len(self.segment_ids)==1 and len(self.vertex_ids)==1
    def throwvalidityerror(self):
        raise(Exception('Need one point and one line'))
class AtLeastOnePoint(object):
    def valid(self):
        return len(set(self.vertex_ids+self.vertices_in_lines()))>=1
    def throwvalidityerror(self):
        raise(Exception('Need at least one point'))
        
class SymbolicVertex(object):
    def __init__(self,id):
        self.id = id
    def p(self):
        p_x = Variable(str(self)+'_x')
        p_y = Variable(str(self)+'_y')
        return sympy.Matrix([p_x,p_y,0])
    def __hash__(self):
        return self.id
    def __eq__(self,other):
        if type(self)==type(other):
            return self.id == other.id
        return False
    def __lt__(self,other):
        return self.id<other.id
    def __str__(self):
        return 'vertex'+str(self.id)

class SymbolicLine(object):
    def __init__(self,v1,v2):
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

class Constraint(object):
    name = 'Constraint'
    deletable = []

    CleanupFlags = enum(NotDeletable=101,Deletable=102)

    def __init__(self,vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
        self.id = id(self)
        self.init_symbolics()
        self.generate_equations()

    def init_symbolics(self):
        self._vertices = [SymbolicVertex(id) for id in self.vertex_ids]
        self._segments = [SymbolicLine(SymbolicVertex(id1),SymbolicVertex(id2)) for id1,id2 in self.segment_ids]
        self._segment_vertices = [SymbolicVertex(id) for id in self.vertices_in_lines()]        
        
    @classmethod
    def new(cls,*objects):
        temp = cls._define_internals(*objects)
        obj = cls(*temp)
        if not obj.valid():
            obj.throwvalidityerror()
        return obj

    def generate_equations(self):
        self.generated_equations = self.equations()
        
    def copy(self,identical = True):
        new = type(self)(self.vertex_ids,self.segment_ids)
        if identical:
            new.id = self.id
        return new

    def edit(self):
        pass

    @staticmethod    
    def _define_internals(*objects):
        from popupcad.geometry.line import Line
        from popupcad.geometry.vertex import BaseVertex
    
        vertex_ids = []
        segment_ids = []
        segment_vertex_ids = []

        vertices = []
        segments = []
        segment_vertices = []

        for item in objects:
            if isinstance(item,BaseVertex):
                vertex_ids.append(item.id)
                vertices.append(item.constraints_ref())
            if isinstance(item,Line)                :
                segment_ids.append(tuple(sorted((item.vertex1.id,item.vertex2.id))))

                segment_vertex_ids.append(item.vertex1.id)
                segment_vertex_ids.append(item.vertex2.id)

                segments.append(item.constraints_ref())
                segment_vertices.extend(item.vertex_constraints_ref())
        return vertex_ids,segment_ids

    def vertices_in_lines(self):
        return [vertex for tuple1 in self.segment_ids for vertex in tuple1]

    def __str__(self):
        return self.name        

    def getlines(self):
        try:
            return self._segments
        except AttributeError:
            self.init_symbolics()
            return self._segments
            
    def getallvertices(self):
        try:
            return self._vertices+self._segment_vertices
        except AttributeError:
            self.init_symbolics()
            return self._vertices+self._segment_vertices
            
    def getvertices(self):
        try:
            return self._vertices
        except AttributeError:
            self.init_symbolics()
            return self._vertices

    def equations(self):
        return []

    def properties(self):
        from popupcad.widgets.propertyeditor import PropertyEditor
        return PropertyEditor(self)

    def cleanup(self,objects):
        self.cleanup_objects(objects)
        if self.valid():
            return self.CleanupFlags.NotDeletable
        else:
            return self.CleanupFlags.Deletable

    def cleanup_objects(self,objects):
        current_ids = frozenset([item.id for item in objects])
        self.vertex_ids = list(frozenset(self.vertex_ids).intersection(current_ids))
        segment_ids = []
        for id1, id2 in self.segment_ids:
            if (id1 in current_ids) and (id2 in current_ids):
                segment_ids.append((id1,id2))
        self.segment_ids = segment_ids

class ValueConstraint(Constraint):
    name = 'ValueConstraint'
    def __init__(self,value,vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
        self.value = value

        self.id = id(self)
        self.init_symbolics()

        self.generate_equations()

    @classmethod
    def new(cls,*objects):
        value,ok = cls.getValue()                
        if ok:
            vertex_ids, segment_ids = cls._define_internals(*objects)
            obj = cls(value,vertex_ids, segment_ids)
            if not obj.valid():
                obj.throwvalidityerror()
            return obj

    def copy(self,identical = True):
        new = type(self)(self.value,self.vertex_ids,self.segment_ids)
        if identical:
            new.id = self.id
        return new

    @classmethod    
    def getValue(cls):
        return qg.QInputDialog.getDouble(None, 'Edit Value', 'Value', 0,-10000, 10000, 5)
        
    def edit(self):
        value, ok = qg.QInputDialog.getDouble(None, "Edit Value", "Value:", self.value, -10000, 10000, 5)
        if ok:
            self.value = value
        self.generate_equations()

class fixed(Constraint,AtLeastOnePoint):
    name = 'fixed'
    def __init__(self,vertex_ids,values):
        self.vertex_ids = vertex_ids
        self.segment_ids = []
        self.values = values
        self.id = id(self)
        self.init_symbolics()
        self.generate_equations()

    @classmethod
    def new(cls,*objects):
        from popupcad.geometry.line import Line
        from popupcad.geometry.vertex import BaseVertex
    
        segment_ids = [tuple(sorted((line.vertex1.id,line.vertex2.id))) for line in objects if isinstance(line,Line)]
        segment_ids = list(set(segment_ids))
        
        vertex_ids = []
        vertex_ids.extend([(vertex.id,vertex.getpos()) for vertex in objects if isinstance(vertex,BaseVertex)])
        vertex_ids.extend([(vertex.id,vertex.getpos()) for line in objects if isinstance(line,Line) for vertex in (line.vertex1,line.vertex2)])
        vertex_ids = dict(vertex_ids)
        
        obj = cls(list(vertex_ids.keys()),list(vertex_ids.values()))
        if not obj.valid():
            obj.throwvalidityerror()
        return obj

    def copy(self,identical = True):
        new = type(self)(self.vertex_ids,self.values)
        if identical:
            new.id = self.id
        return new

    def equations(self):
        eqs = []
        for vertex,val in zip(self.getvertices(),self.values):
            eqs.append(vertex.p()[0] - val[0])
            eqs.append(vertex.p()[1] - val[1])
        return eqs         

class horizontal(Constraint,AtLeastTwoPoints):
    name = 'horizontal'
    def equations(self):
        vertices = self.getallvertices()
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[1] - p0[1])
        return eqs         

class vertical(Constraint,AtLeastTwoPoints):
    name = 'vertical'
    def equations(self):
        vertices = self.getallvertices()
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[0] - p0[0])
        return eqs

class distance(ValueConstraint,ExactlyTwoPoints):
    name = 'distance'
    def equations(self):
        vertices = self.getallvertices()
        p0 = vertices[0].p()
        p1 = vertices[1].p()
        if self.value==0.:
            eq = []
            eq.append(p1[0] - p0[0])
            eq.append(p1[1] - p0[1])
            return eq
        else:
            v1 = p1 - p0
            l1 = v1.dot(v1)**.5
            eq = l1 - self.value*popupcad.internal_argument_scaling
            return [eq]  

class coincident(Constraint,AtLeastTwoPoints):
    name = 'coincident'
    def equations(self):
        vertices = self.getallvertices()
        eq = []
        p0 = vertices.pop().p()
        for vertex in vertices:
            p = vertex.p()
            eq.append(p[0] - p0[0])
            eq.append(p[1] - p0[1])
        return eq

class distancex(ValueConstraint,AtLeastOnePoint):
    name = 'distancex'
    def equations(self):
        vertices = self.getallvertices()
        if len(vertices)==1:
            eq = vertices[0].p()[0]-self.value*popupcad.internal_argument_scaling
        else:
            eq = ((vertices[1].p()[0]-vertices[0].p()[0])**2)**.5-((self.value*popupcad.internal_argument_scaling)**2)**.5
        return [eq]

class distancey(ValueConstraint,AtLeastOnePoint):
    name = 'distancey'
    def equations(self):
        vertices = self.getallvertices()
        if popupcad.flip_y:
            temp = 1.
        else:
            temp = -1.
        if len(vertices)==1:
            eq = vertices[0].p()[1]-self.value*temp*popupcad.internal_argument_scaling
        else:
            eq = ((vertices[1].p()[1]-vertices[0].p()[1])**2)**.5-((self.value*popupcad.internal_argument_scaling)**2)**.5
        return [eq]

class angle(ValueConstraint,AtLeastOneLine):
    name = 'angle'
    value_text = 'enter angle(in degrees)'
    def equations(self):
        lines = self.getlines()[0:2]

        if len(lines)==1:
            v1 = lines[0].v()
            v2 = sympy.Matrix([1,0,0])
            l2 = 1
        elif len(lines)==2:
            v1 = lines[0].v()
            v2 = lines[1].v()
            l2 = v2.dot(v2)**(.5)
        if self.value!=0:
            l1 = v1.dot(v1)**(.5)
            v3 = v1.cross(v2)
            l3 = v3.dot(v3)**.5
            eq = l3-sympy.sin(self.value*sympy.pi/180)*l1*l2
        else:
            if len(lines)==1:
                eq = v1[1]
            elif len(lines)==2:
                eq = v2[0]*v1[1] - v2[1]*v1[0]
        return [eq]     

class parallel(Constraint,AtLeastTwoLines):
    name = 'parallel'
    def equations(self):
        lines = self.getlines()
        v1 = lines.pop(0).v()
        eq = []
        for line in lines:
            v2 = line.v()
            eq.append(v2[0]*v1[1] - v2[1]*v1[0])
        return eq

class equal(Constraint,AtLeastTwoLines):
    name = 'equal'
    def equations(self):
        lines = self.getlines()
        vs = [line.v() for line in lines]
        lengths = [v.dot(v)**.5 for v in vs]
        eqs = []
        length0 = lengths.pop(0)
        for length in lengths:
            eqs.append(length0 - length)
        return eqs    
        
class perpendicular(Constraint,ExactlyTwoLines):
    name = 'perpendicular'
    def equations(self):
        lines = self.getlines()[0:2]
        v1 = lines[0].v()
        v2 = lines[1].v()
        return [v2[1]*v1[1] + v2[0]*v1[0]]

class PointLine(ValueConstraint,ExactlyOnePointOneLine):
    name = 'PointLineDistance'
    def equations(self):
        line = self.getlines()[0]
        p1 = self.getvertices()[0].p()
        v1 = p1-line.p1()
        v = line.v()
        lv = line.lv()
        a = v.dot(v1)/lv
        p0 = v*a/lv + line.p1()
        
        if self.value==0.:
            eq = []
            eq.append(p1[0] - p0[0])
            eq.append(p1[1] - p0[1])
            return eq
        else:
            v1 = p1 - p0
            l1 = v1.dot(v1)**.5
            eq = l1 - self.value*popupcad.internal_argument_scaling
            return [eq]  
        return [x]

if __name__=='__main__':
    a = SymbolicVertex(123)
    b = SymbolicVertex(234)
    c = tuple(sorted((a,b)))
    d = tuple(sorted((a,b)))
    