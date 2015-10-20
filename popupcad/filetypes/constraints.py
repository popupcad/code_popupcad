# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import sympy
import sympy.utilities
import numpy
import PySide.QtGui as qg
import scipy.optimize
import numpy.linalg
import popupcad
from dev_tools.enum import enum

class Variable(sympy.Symbol):
    pass

class UnknownType(Exception):
    pass        
        
class WrongArguments(Exception):
    pass        

class ConstraintSystem(object):
    atol = 1e-10
    rtol = 1e-10
    tfinal = 10
    tsegments = 10

    def __init__(self):
        self.constraints = []

    def get_vertices_callback(self, callback):
        self._get_vertices = callback

    @property
    def get_vertices(self):
        try:
            return self._get_vertices()
        except AttributeError:
            return []

    @get_vertices.setter
    def get_vertices(self,callback):
        self._get_vertices = callback

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def inilist(self, variables, ini):
        listout = []
        for item in variables:
            listout.append(ini[item])
        return numpy.array(listout)

    def copy(self):
        new = ConstraintSystem()
        new.constraints = [constraint.copy() for constraint in self.constraints]
        return new

    def upgrade(self):
        new = ConstraintSystem()
        new.constraints = [constraint.upgrade() for constraint in self.constraints]
        return new

    def vertex_dict(self):
        objects = self.get_vertices
        vertex_dict = {}
        for vertex in objects:
            p = vertex.p()[0:2]
            vertex_dict[p[0]] = vertex
            vertex_dict[p[1]] = vertex
        return vertex_dict

    def ini(self,vertex_dict):
        objects = self.get_vertices
        ini = {}
        for vertex in objects:
            p = vertex.p()[0:2]
            pos = vertex.getpos()
            for key, value in zip(p, pos):
                ini[key] = value
        return ini

    def regenerate(self):
        del self.generated_variables
        self.generated_variables
        
    @property
    def generated_variables(self):
        try:
            return self._generated_variables
        except AttributeError:
            self._generated_variables = self.regenerate_inner()
            return self._generated_variables
            
    @generated_variables.deleter
    def generated_variables(self):
        try:
            del self._generated_variables
        except AttributeError:
            pass
        
    def equations(self):
        equations = [eq for con in self.constraints for eq in con.generated_equations]
        return equations
        
    def variables(self):
        variables = [item for equation in self.equations() for item in list(equation.atoms(Variable))]
        variables = sorted(set(variables),key=lambda item:str(item))
        return variables

    def build_constraint_mappings(self):
        ii = 0
        m = len(self.equations())
        variables = self.variables()
        for constraint in self.constraints:
            l=len(constraint.generated_equations)
            constraint.build_system_mapping(variables,m,range(ii,ii+l))
            ii+=l

    def constants(self):
        constants = [item for equation in self.equations() for item in list(equation.atoms(Variable))]
        constants = sorted(set(constants),key=lambda item:str(item))
        return constants
        
    def regenerate_inner(self):
        vertexdict = self.vertex_dict()
        
        if len(self.constraints) > 0:
            objects = self.get_vertices
            if len(objects) > 0:
                equations = self.equations()
                num_equations = len(equations)
                
                variables = self.variables()
                num_variables = len(variables)

                self.build_constraint_mappings()
                
                def dq(q):
                    qlist = q.flatten().tolist()

                    zero = numpy.zeros(num_equations,dtype=float)
                    for constraint in self.constraints:
                        result = constraint.mapped_f_constraints(*qlist[:])
                        zero+=result

                    if num_variables > num_equations:
                        zero = numpy.r_[zero.flatten(), [0] * (num_variables - num_equations)]
                    return zero

                def j(q):
                    qlist = q.flatten().tolist()

                    jnum = numpy.zeros((num_equations,num_variables))
                    for constraint in self.constraints:
                        jnum+=constraint.mapped_f_jacobian(*qlist[:])
                    
                    if num_variables > num_equations:
                        jnum = numpy.r_[jnum, numpy.zeros((num_variables - num_equations, num_variables))]
                    return jnum
                
                return dq, variables, j, vertexdict

        return None
        
    def update(self):
        if self.generated_variables is None:
            pass
        else:
            dq, variables, j, vertexdict = self.generated_variables
            vertexdict = self.vertex_dict()
            ini = self.ini(vertexdict)
            q0 = self.inilist(variables,ini)
            qout = scipy.optimize.root(dq,q0,jac=j,tol=self.atol,method='lm')
            qout = qout.x.tolist()

#            qout = opt.newton_krylov(dq2,numpy.array(self.inilist(variables,ini)),f_tol = self.atol,f_rtol = self.rtol)
#            qout = opt.anderson(dq2,numpy.array(self.inilist(variables,ini)),f_tol = self.atol,f_rtol = self.rtol)
#            qout = qout.tolist()
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'hybr')
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'linearmixing')
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'excitingmixing')
#            qout = opt.root(dq2,numpy.array(self.inilist(variables,ini)),tol = self.atol,method = 'lm')
#            qout = qout.x.tolist()

            for ii, variable in enumerate(variables):
                vertexdict[variable].setsymbol(variable, qout[ii])
#        except (AttributeError, TypeError):
#            pass

    def update_selective(self,vertices):
        self.update()
        
    def constrained_shift(self, items):
        vertexdict = self.vertex_dict()
        ini = self.ini(vertexdict)
        if self.generated_variables is None:
            for vertex, dxdy in items:
                vertex.shift(dxdy)
        else:
            dq, variables, j, vertexdict = self.generated_variables
    
            dx_dict = {}
            for vertex, dxdy in items:
                key_x, key_y = vertex.constraints_ref().p()[:2]
                dx_dict[key_x] = dxdy[0]
                dx_dict[key_y] = dxdy[1]
    
            dx = numpy.zeros(len(variables))
            for key in dx_dict:
                if key in variables:
                    dx[variables.index(key)] = dx_dict[key]
                else:
                    vertexdict[key].setsymbol(key, ini[key] + dx_dict[key])
    
            x0 = numpy.array(self.inilist(variables, ini))
            Jnum = j(x0)
            L, S, R = numpy.linalg.svd(Jnum)
            aS = abs(S)
            m = (aS > (aS[0] / 100)).sum()
    
            rnull = R[m:]
            lnull = ((rnull**2).sum(1))**.5
            comp = ((rnull * dx).sum(1)) / lnull
            x_motion = (comp * rnull.T).sum(1)
    
            x = x0 + x_motion
    
            for ii, variable in enumerate(variables):
                vertexdict[variable].setsymbol(variable, x[ii])
#
    def cleanup(self):
        sketch_objects = self.get_vertices
        for ii in range(len(self.constraints))[::-1]:
            if self.constraints[ii].cleanup(
                    sketch_objects) == Constraint.CleanupFlags.Deletable:
                self.constraints.pop(ii)


class ExactlyTwoPoints(object):

    def valid(self):
        return len(set(self.vertex_ids + self.vertices_in_lines())) == 2

    def throwvalidityerror(self):
        raise WrongArguments('Need exactly two points')


class AtLeastTwoPoints(object):

    def valid(self):
        return len(set(self.vertex_ids + self.vertices_in_lines())) >= 2

    def throwvalidityerror(self):
        raise WrongArguments('Need at least two points')


class ExactlyTwoLines(object):

    def valid(self):
        return len(self.segment_ids) == 2

    def throwvalidityerror(self):
        raise WrongArguments('Need exactly two lines')


class AtLeastTwoLines(object):

    def valid(self):
        return len(self.segment_ids) >= 2

    def throwvalidityerror(self):
        raise WrongArguments('Need at least two lines')


class AtLeastOneLine(object):

    def valid(self):
        return len(self.segment_ids) >= 1

    def throwvalidityerror(self):
        raise WrongArguments('Need at least one line')


class ExactlyOnePointOneLine(object):

    def valid(self):
        return len(self.segment_ids) == 1 and len(self.vertex_ids) == 1

    def throwvalidityerror(self):
        raise WrongArguments('Need exactly one point and one line')


class AtLeastOnePoint(object):

    def valid(self):
        return len(set(self.vertex_ids + self.vertices_in_lines())) >= 1

    def throwvalidityerror(self):
        raise WrongArguments('Need at least one point')


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


class Constraint(object):
    name = 'Constraint'
    deletable = []

    CleanupFlags = enum(NotDeletable=101, Deletable=102)

    def __init__(self, vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
        self.id = id(self)

    def init_symbolics(self):
        self._vertices = [SymbolicVertex(id) for id in self.vertex_ids]
        self._segments = [
            SymbolicLine(
                SymbolicVertex(id1),
                SymbolicVertex(id2)) for id1,
            id2 in self.segment_ids]
        self._segment_vertices = [
            SymbolicVertex(id) for id in self.vertices_in_lines()]

    @classmethod
    def new(cls, *objects):
        obj = cls(*cls._define_internals(*objects))
        if not obj.valid():
            obj.throwvalidityerror()
        return obj
    
    @property
    def generated_equations(self):
        try:
            return self._generated_equations
        except AttributeError:
            self._generated_equations = self.symbolic_equations()
            return self._generated_equations

    @generated_equations.deleter
    def generated_equations(self):
        del self._generated_equations

        try:
            del self._f_constraints
        except AttributeError:
            pass

        try:
            del self._f_J
        except AttributeError:
            pass
    
    @property
    def f_jacobian(self):
        try:
            return self._f_jacobian
        except AttributeError:
            self._f_jacobian = sympy.utilities.lambdify(self.variables(),self.jacobian().tolist())
            return self._f_jacobian
            
    @property
    def f_constraints(self):
        try:
            return self._f_constraints
        except AttributeError:
            self._f_constraints = sympy.utilities.lambdify(self.variables(),self.generated_equations)
            return self._f_constraints
            
    def mapped_f_constraints(self,*args):
        args = (self._B.dot(args))     
        y = self._A.dot(self.f_constraints(*args))
        return y

    def mapped_f_jacobian(self,*args):
        args = (self._B.dot(args))
        y = self._A.dot(self.f_jacobian(*args)).dot(self._B)
        return y

    def variables(self):
        variables = []
        for equation in self.generated_equations:
            variables.extend(equation.atoms(Variable))
        variables = set(variables)
        variables -= set(self.constants())
        variables = sorted(variables,key=lambda var:str(var))
        return variables
        
    def constants(self):
        return []

    def jacobian(self):
        eq = sympy.Matrix(self.generated_equations)        
        J = eq.jacobian(self.variables())
        return J

    def build_system_mapping(self,sys_vars,num_eq,eq_indeces):
        m = num_eq
        n = len(self.generated_equations)
        o = len(self.variables())
        p = len(sys_vars)

        A = numpy.zeros((m,n))
        for ii,jj in zip(eq_indeces,range(len(self.generated_equations))):
            A[ii,jj] = 1

        B = numpy.zeros((o,p))
        for ii,item in enumerate(self.variables()):
            jj = sys_vars.index(item)
            B[ii,jj] = 1

        self._A = A
        self._B = B
#        return A,B
    
    def copy(self, identical=True):
        new = type(self)(self.vertex_ids[:], self.segment_ids[:])
        if identical:
            new.id = self.id
        return new

    def upgrade(self, *args, **kwargs):
        return self

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
            if isinstance(item, BaseVertex):
                vertex_ids.append(item.id)
                vertices.append(item.constraints_ref())
            elif isinstance(item, Line):
                segment_ids.append(
                    tuple(
                        sorted(
                            (item.vertex1.id, item.vertex2.id))))

                segment_vertex_ids.append(item.vertex1.id)
                segment_vertex_ids.append(item.vertex2.id)

                segments.append(item.constraints_ref())
                segment_vertices.extend(item.vertex_constraints_ref())
            else:
                print('wrong thing supplied')
        return vertex_ids, segment_ids

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
            return self._vertices + self._segment_vertices
        except AttributeError:
            self.init_symbolics()
            return self._vertices + self._segment_vertices

    def getvertices(self):
        try:
            return self._vertices
        except AttributeError:
            self.init_symbolics()
            return self._vertices

    def symbolic_equations(self):
        return []

    def properties(self):
        from dev_tools.propertyeditor import PropertyEditor
        return PropertyEditor(self)

    def cleanup(self, objects):
        self.cleanup_objects(objects)
        if self.valid():
            return self.CleanupFlags.NotDeletable
        else:
            return self.CleanupFlags.Deletable

    def cleanup_objects(self, objects):
        current_ids = frozenset([item.id for item in objects])
        self.vertex_ids = list(
            frozenset(
                self.vertex_ids).intersection(current_ids))
        segment_ids = []
        for id1, id2 in self.segment_ids:
            if (id1 in current_ids) and (id2 in current_ids):
                segment_ids.append((id1, id2))
        self.segment_ids = segment_ids

class ValueConstraint(Constraint):
    name = 'ValueConstraint'

    def __init__(self, value, vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
        self.value = value

        self.id = id(self)

    @classmethod
    def new(cls, *objects):
        value, ok = cls.getValue()
        if ok:
            obj = cls(value, *cls._define_internals(*objects))
            if not obj.valid():
                obj.throwvalidityerror()
            return obj

    def copy(self, identical=True):
        new = type(self)(self.value, self.vertex_ids[:], self.segment_ids[:])
        if identical:
            new.id = self.id
        return new

    @classmethod
    def getValue(cls):
        return qg.QInputDialog.getDouble(None, 'Edit Value', 'Value', 0, popupcad.gui_negative_infinity, popupcad.gui_positive_infinity, popupcad.default_gui_rounding)

    def edit(self):
        value, ok = qg.QInputDialog.getDouble(None, "Edit Value", "Value:", self.value, popupcad.gui_negative_infinity, popupcad.gui_positive_infinity, popupcad.default_gui_rounding)
        if ok:
            self.value = value
        del self.generated_equations


class fixed(Constraint, AtLeastOnePoint):
    name = 'fixed'

    def __init__(self, vertex_ids, values):
        self.vertex_ids = vertex_ids
        self.segment_ids = []
        self.values = values
        self.id = id(self)

    @classmethod
    def new(cls, *objects):
        from popupcad.geometry.line import Line
        from popupcad.geometry.vertex import BaseVertex

        segment_ids = [
            tuple(
                sorted(
                    (line.vertex1.id, line.vertex2.id))) for line in objects if isinstance(
                line, Line)]
        segment_ids = list(set(segment_ids))

        vertex_ids = []
        vertex_ids.extend([(vertex.id, vertex.getpos())
                           for vertex in objects if isinstance(vertex, BaseVertex)])
        vertex_ids.extend([(vertex.id,
                            vertex.getpos()) for line in objects if isinstance(line,
                                                                               Line) for vertex in (line.vertex1,
                                                                                                    line.vertex2)])
        vertex_ids = dict(vertex_ids)

        obj = cls(list(vertex_ids.keys()), list(vertex_ids.values()))
        if not obj.valid():
            obj.throwvalidityerror()
        return obj

    def copy(self, identical=True):
        new = type(self)(self.vertex_ids, self.values)
        if identical:
            new.id = self.id
        return new

    def symbolic_equations(self):
        eqs = []
        for vertex, val in zip(self.getvertices(), self.values):
            eqs.append(vertex.p()[0] - val[0])
            eqs.append(vertex.p()[1] - val[1])
        return eqs


class horizontal(Constraint, AtLeastTwoPoints):
    name = 'horizontal'

    def symbolic_equations(self):
        vertices = self.getallvertices()
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[1] - p0[1])
        return eqs


class vertical(Constraint, AtLeastTwoPoints):
    name = 'vertical'

    def symbolic_equations(self):
        vertices = self.getallvertices()
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[0] - p0[0])
        return eqs


class distance(ValueConstraint, ExactlyTwoPoints):
    name = 'distance'

    def symbolic_equations(self):
        vertices = self.getallvertices()
        p0 = vertices[0].p()
        p1 = vertices[1].p()
        if self.value == 0.:
            eq = []
            eq.append(p1[0] - p0[0])
            eq.append(p1[1] - p0[1])
            return eq
        else:
            v1 = p1 - p0
            l1 = v1.dot(v1)**.5
            eq = l1 - self.value
            return [eq]


class coincident(Constraint, AtLeastTwoPoints):
    name = 'coincident'

    def symbolic_equations(self):
        vertices = self.getallvertices()
        eq = []
        p0 = vertices.pop().p()
        for vertex in vertices:
            p = vertex.p()
            eq.append(p[0] - p0[0])
            eq.append(p[1] - p0[1])
        return eq


class distancex(ValueConstraint, AtLeastOnePoint):
    name = 'distancex'

    def symbolic_equations(self):
        vertices = self.getallvertices()
        if len(vertices) == 1:
            eq = vertices[0].p()[0] - self.value
        else:
            eq = ((vertices[1].p()[0] - vertices[0].p()[0])**2)**.5 - \
                ((self.value)**2)**.5
        return [eq]


class distancey(ValueConstraint, AtLeastOnePoint):
    name = 'distancey'

    def symbolic_equations(self):
        vertices = self.getallvertices()
        if popupcad.flip_y:
            temp = 1.
        else:
            temp = -1.
        if len(vertices) == 1:
            eq = vertices[0].p()[1] - self.value * temp
        else:
            eq = ((vertices[1].p()[1] - vertices[0].p()[1])**2)**.5 - \
                ((self.value)**2)**.5
        return [eq]


class angle(ValueConstraint, AtLeastOneLine):
    name = 'angle'
    value_text = 'enter angle(in degrees)'

    def symbolic_equations(self):
        lines = self.getlines()[0:2]

        if len(lines) == 1:
            v1 = lines[0].v()
            v2 = sympy.Matrix([1, 0, 0])
            l2 = 1
        elif len(lines) == 2:
            v1 = lines[0].v()
            v2 = lines[1].v()
            l2 = v2.dot(v2)**(.5)
        if self.value != 0:
            l1 = v1.dot(v1)**(.5)
            v3 = v1.cross(v2)
            l3 = v3.dot(v3)**.5
            eq = l3 - sympy.sin(self.value * sympy.pi / 180) * l1 * l2
        else:
            if len(lines) == 1:
                eq = v1[1]
            elif len(lines) == 2:
                eq = v2[0] * v1[1] - v2[1] * v1[0]
        return [eq]


class parallel(Constraint, AtLeastTwoLines):
    name = 'parallel'

    def symbolic_equations(self):
        lines = self.getlines()
        v1 = lines.pop(0).v()
        eq = []
        for line in lines:
            v2 = line.v()
            eq.append(v2[0] * v1[1] - v2[1] * v1[0])
        return eq


class equal(Constraint, AtLeastTwoLines):
    name = 'equal'

    def symbolic_equations(self):
        lines = self.getlines()
        vs = [line.v() for line in lines]
        lengths = [v.dot(v)**.5 for v in vs]
        eqs = []
        length0 = lengths.pop(0)
        for length in lengths:
            eqs.append(length0 - length)
        return eqs


class perpendicular(Constraint, ExactlyTwoLines):
    name = 'perpendicular'

    def symbolic_equations(self):
        lines = self.getlines()[0:2]
        v1 = lines[0].v()
        v2 = lines[1].v()
        return [v2[1] * v1[1] + v2[0] * v1[0]]


class PointLine(ValueConstraint, ExactlyOnePointOneLine):
    name = 'PointLineDistance'

    def symbolic_equations(self):
        line = self.getlines()[0]
        p1 = self.getvertices()[0].p()
        v1 = p1 - line.p1()
        v = line.v()
        lv = line.lv()
        a = v.dot(v1) / lv
        p0 = v * a / lv + line.p1()

        if self.value == 0.:
            eq = []
            eq.append(p1[0] - p0[0])
            eq.append(p1[1] - p0[1])
            return eq
        else:
            v1 = p1 - p0
            l1 = v1.dot(v1)**.5
            eq = l1 - self.value
            return [eq]


class LineMidpoint(Constraint, ExactlyOnePointOneLine):
    name = 'Line Midpoint'

    def symbolic_equations(self):
        line = self.getlines()[0]
        p1 = self.getvertices()[0].p()
        p0 = (line.p1() + line.p2()) / 2

        eq = []
        eq.append(p1[0] - p0[0])
        eq.append(p1[1] - p0[1])
        return eq

if __name__ == '__main__':
#    a = SymbolicVertex(1)
#    b = SymbolicVertex(2)
#    c = SymbolicVertex(3)
#    d = SymbolicVertex(4)
    
#    line1 = a,b
#    line2 = b,c

    constraint = perpendicular([],[(1,2),(3,4)])