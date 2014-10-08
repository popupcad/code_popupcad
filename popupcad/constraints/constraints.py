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
class Constant(sympy.Symbol):
    pass

class ConstraintSystem(object):
    atol = 1e-10
    rtol = 1e-10
    tfinal = 10
    tsegments = 10
    def __init__(self):
        self.constraints = []
        
    def add_constraint(self,constraint):
        self.constraints.append(constraint)
    
    def inilist(self,variables,ini):
        listout = []
        for item in variables:
            listout.append(ini[item])
        return listout
        
    def deriveJ(self,objects):
        constraint_eqs = sympy.Matrix([equation for constraint in self.constraints for equation in constraint.equations(objects)])
        variables = list(set([item for equation in constraint_eqs for item in list(equation.atoms(Variable))]))
        constants = list(set([item for equation in constraint_eqs for item in list(equation.atoms(Constant))]))
        J = constraint_eqs.jacobian(sympy.Matrix(variables))
        return constraint_eqs,variables,constants,J
    
    def copy(self):
        new = ConstraintSystem()
        new.constraints = [constraint.copy() for constraint in self.constraints]
        return new

    def gendq(self,Jfun,constfun,constvals):
        def dq(q,t):
            qlist = q.flatten().tolist()
            dq  = Jfun(*(qlist+constvals))
            dq=numpy.array(dq[:])
            kf  = constfun(*(qlist+constvals))
            kf=numpy.array(kf[:])
            dq = -dq*kf
            dq = dq.sum(0)*5
            return dq        
        return dq
        
    def gendq2(self,dq):
        return lambda x:dq(x,0)
        
    def integrate(self,dq,qini,fun2,vertices,variables):
        q = numpy.array(qini)
        totalerror = (numpy.array(fun2(*(q.flatten().tolist()))[:])).sum(0)
        while abs(totalerror)>self.atol:
            dq1 =dq(q,0)
            q = q+dq1
            totalerror = (numpy.array(fun2(*(q.flatten().tolist()))[:])).sum(0)
        return q

    def getlinks(self,vertices):
        ini = {}
        vertexdict = {}
        for vertex in vertices:
            p = vertex.p()[0:2]

            vertexdict[p[0]]=vertex
            vertexdict[p[1]]=vertex

            pos = vertex.getpos()
            for key,value in zip(p,pos):     
                ini[key]=value
        return ini,vertexdict

#    def getpersistentobjects(self):
#        vertices = []
#        for constraint in self.constraints:
#            vertices.extend(constraint.persistentobjects())
#        return vertices
            
    def process(self,vertices): 
#        vertices += self.getpersistentobjects()
        ini,vertexdict = self.getlinks(vertices)
        variables,qout = [],[]
        if len(self.constraints)>0:
            constraint_eqs,variables,constants,J= self.deriveJ(vertices)
            Jfun= sympy.utilities.lambdify(variables+constants,J)
            constfun = sympy.utilities.lambdify(variables+constants,constraint_eqs)
            constvals = self.inilist(constants,ini)
            dq = self.gendq(Jfun,constfun,constvals)
#            t = numpy.r_[0:self.tfinal:self.tsegments*1j]
#            qout = integ.odeint(dq,numpy.array(self.inilist(variables,ini)),t,atol=self.atol,rtol=self.rtol) 
#            qout = qout[-1,:].tolist()
            dq2 = self.gendq2(dq)
#            qout = opt.newton_krylov(dq2,numpy.array(self.inilist(variables,ini)),f_tol = self.atol,f_rtol = self.rtol)
#            qout = qout.tolist()
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'hybr')
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'linearmixing')
            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'lm')
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'excitingmixing')
            qout = qout.x.tolist()
        for ii,variable in enumerate(variables):
            vertexdict[variable].setsymbol(variable,qout[ii])   
    def cleanup(self,sketch_objects):
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
        return len(self.segment_ids)==2
    def throwvalidityerror(self):
        raise(Exception('Need at least two lines'))
class ExactlyOnePointOneLine(object):
    def valid(self):
        return len(self.segment_ids)==1 and len(self.vertex_ids)==1
    def throwvalidityerror(self):
        raise(Exception('Need one point and one line'))
        

class Constraint(object):
    name = 'Constraint'
    deletable = []

    CleanupFlags = enum(NotDeletable=101,Deletable=102)
    CurrentFlags= enum(AllCurrent=201,SomeCurrent=202,NoneCurrent=203)
    
#    def __init__(self,vertex_ids, segment_ids,persistentobjects):
    def __init__(self,vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
#        self._persistentobjects = persistentobjects
        self.id = id(self)
        
    @classmethod
    def new(cls,parent,*objects):
        temp = cls._define_internals(*objects)
        obj = cls(*temp)
        if not obj.valid():
            obj.throwvalidityerror()
        return obj
        
    def copy(self,identical = True):
#        new = type(self)(self.vertex_ids,self.segment_ids,self.persistentobjects())
        new = type(self)(self.vertex_ids,self.segment_ids)
        if identical:
            new.id = self.id
        return new

    def edit(self):
        pass

    @staticmethod    
    def _define_internals(*objects):
        from popupcad.geometry.line import Line
        from popupcad.geometry.vertex import Vertex,ReferenceVertex
    
        segment_ids = [(line.vertex1.id,line.vertex2.id) for line in objects if isinstance(line,Line)]
        segment_ids = list(set(segment_ids))
        
        vertices = []
        vertices.extend([vertex for vertex in objects if isinstance(vertex,Vertex)])
        vertex_ids = [vertex.id for vertex in vertices]
        vertex_ids = list(set(vertex_ids))

        vertices_in_lines = []
        vertices_in_lines.extend([vertex for line in objects if isinstance(line,Line) for vertex in [line.vertex1,line.vertex2]])

#        persistentobjects = []
#        persistentobjects.extend([vertex for vertex in vertices if isinstance(vertex,ReferenceVertex)])
#        persistentobjects.extend([vertex for vertex in vertices_in_lines if isinstance(vertex,ReferenceVertex)])

#        return vertex_ids,segment_ids,persistentobjects
        return vertex_ids,segment_ids
#
#    def persistentobjects(self):
#        try:
#            self._persistentobjects
#        except AttributeError:
#            self._persistentobjects = []
#        return self._persistentobjects
        
    def vertices_in_lines(self):
        return [vertex for tuple1 in self.segment_ids for vertex in tuple1]

    def __str__(self):
        return self.name        


    def getlines(self,objectlist):
        from popupcad.geometry.line import Line
        id_dict = dict(zip([obj.id for obj in objectlist],objectlist))
        segmentlist = []
        for id1,id2 in self.segment_ids:
            try:
                segmentlist.append(Line(id_dict[id1],id_dict[id2]))
            except KeyError:
                pass
        return segmentlist

    def getallvertices(self,objectlist):
        id_dict = dict(zip([obj.id for obj in objectlist],objectlist))

        vertexlist = []
        for id1 in self.vertex_ids+self.vertices_in_lines():
            try:
                vertexlist.append(id_dict[id1])
            except KeyError:
                pass

        return vertexlist

    def getvertices(self,objectlist):
        id_dict = dict(zip([obj.id for obj in objectlist],objectlist))
        vertexlist = []
        for id1 in self.vertex_ids:
            try:
                vertexlist.append(id_dict[id1])
            except KeyError:
                pass
        return vertexlist

    def equations(self,objects):
        return []

    def properties(self):
        from popupcad.widgets.propertyeditor import PropertyEditor
        return PropertyEditor(self)

#    def checkcurrent(self,objects):
#        flag = self.CurrentFlags.NoneCurrent
#        if len(self.persistentobjects())>0:
#            current = [item in objects for item in self.persistentobjects()]
#            if all(current):
#                flag = self.CurrentFlags.AllCurrent
#            elif any(current):
#                flag = self.CurrentFlags.SomeCurrent
#            else:
#                flag = self.CurrentFlags.NoneCurrent
#        else:
#            flag = self.CurrentFlags.AllCurrent
#        return flag
        
        
    def cleanup(self,objects):
        self.cleanup_objects(objects)
        if self.valid():
            return self.CleanupFlags.NotDeletable
        else:
            return self.CleanupFlags.Deletable
#        currentflag = self.checkcurrent(objects)
#        if currentflag == self.CurrentFlags.AllCurrent:
#            return self.CleanupFlags.NotDeletable
#        elif currentflag == self.CurrentFlags.SomeCurrent:
#            return self.CleanupFlags.Deletable
#        elif currentflag == self.CurrentFlags.NoneCurrent:
#            return self.CleanupFlags.Deletable

    def cleanup_objects(self,objects):
        current_ids = frozenset([item.id for item in objects])
        self.vertex_ids = list(frozenset(self.vertex_ids).intersection(current_ids))
        segment_ids = []
        for id1, id2 in self.segment_ids:
            if (id1 in current_ids) and (id2 in current_ids):
                segment_ids.append((id1,id2))
        self.segment_ids = segment_ids
#        self.vertex_ids = list(frozenset(self.vertex_ids).intersect(current_ids))

class ValueConstraint(Constraint):
    name = 'ValueConstraint'
    
#    def __init__(self,value,vertex_ids, segment_ids,persistentobjects):
    def __init__(self,value,vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
        self.value = value
#        self._persistentobjects = persistentobjects
        self.id = id(self)

    @classmethod
    def new(cls,parent,*objects):
        value,ok = cls.getValue(parent)                
        if ok:
#            vertex_ids, segment_ids,persistentobjects = cls._define_internals(*objects)
            vertex_ids, segment_ids = cls._define_internals(*objects)
#            obj = cls(value,vertex_ids, segment_ids,persistentobjects)
            obj = cls(value,vertex_ids, segment_ids)
            if not obj.valid():
                obj.throwvalidityerror()
            return obj

    def copy(self,identical = True):
#        new = type(self)(self.value,self.vertex_ids,self.segment_ids,self.persistentobjects())
        new = type(self)(self.value,self.vertex_ids,self.segment_ids)
        if identical:
            new.id = self.id
        return new

    @classmethod    
    def getValue(cls,parent):
        return qg.QInputDialog.getDouble(parent, 'Edit Value', 'Value', 0,-10000, 10000, 5)
        
    def edit(self):
        value, ok = qg.QInputDialog.getDouble(None, "Edit Value", "Value:", self.value, -10000, 10000, 5)
        if ok:
            self.value = value

class horizontal(Constraint,AtLeastTwoPoints):
    name = 'horizontal'
    def equations(self,objects):
        vertices = self.getallvertices(objects)
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[1] - p0[1])
        return eqs         

class vertical(Constraint,AtLeastTwoPoints):
    name = 'vertical'
    def equations(self,objects):
        vertices = self.getallvertices(objects)
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[0] - p0[0])
        return eqs

class distance(ValueConstraint,ExactlyTwoPoints):
    name = 'distance'
    def equations(self,objects):
        vertices = self.getallvertices(objects)
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
    def equations(self,objects):
        vertices = self.getallvertices(objects)
        eq = []
        p0 = vertices.pop().p()
        for vertex in vertices:
            p = vertex.p()
            eq.append(p[0] - p0[0])
            eq.append(p[1] - p0[1])
        return eq

class distancex(ValueConstraint,ExactlyTwoPoints):
    name = 'distancex'
    def equations(self,objects):
        vertices = self.getallvertices(objects)
        if len(vertices)==1:
            eq = vertices[0].p()[0]-self.value*popupcad.internal_argument_scaling
        else:
            eq = ((vertices[1].p()[0]-vertices[0].p()[0])**2)**.5-((self.value*popupcad.internal_argument_scaling)**2)**.5
        return [eq]

class distancey(ValueConstraint,ExactlyTwoPoints):
    name = 'distancey'
    def equations(self,objects):
        vertices = self.getallvertices(objects)
        if popupcad.flip_y:
            temp = 1.
        else:
            temp = -1.
        if len(vertices)==1:
            eq = vertices[0].p()[1]-self.value*temp*popupcad.internal_argument_scaling
        else:
            eq = ((vertices[1].p()[1]-vertices[0].p()[1])**2)**.5-((self.value*popupcad.internal_argument_scaling)**2)**.5
        return [eq]

class angle(ValueConstraint,ExactlyTwoLines):
    name = 'angle'
    value_text = 'enter angle(in degrees)'
    def equations(self,objects):
        lines = self.getlines(objects)[0:2]

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
    def equations(self,objects):
        lines = self.getlines(objects)
        v1 = lines.pop(0).v()
        eq = []
        for line in lines:
            v2 = line.v()
            eq.append(v2[0]*v1[1] - v2[1]*v1[0])
        return eq

class equal(Constraint,AtLeastTwoLines):
    name = 'equal'
    def equations(self,objects):
        lines = self.getlines(objects)
        vs = [line.v() for line in lines]
        lengths = [v.dot(v)**.5 for v in vs]
        eqs = []
        length0 = lengths.pop(0)
        for length in lengths:
            eqs.append(length0 - length)
        return eqs    
        
class perpendicular(Constraint,ExactlyTwoLines):
    name = 'perpendicular'
    def equations(self,objects):
        lines = self.getlines(objects)[0:2]
        v1 = lines[0].v()
        v2 = lines[1].v()
        return [v2[1]*v1[1] + v2[0]*v1[0]]

class PointLine(ValueConstraint,ExactlyOnePointOneLine):
    name = 'PointLineDistance'
    def equations(self,objects):
        line = self.getlines(objects)[0]
        p1 = self.getvertices(objects)[0].p()
        
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
