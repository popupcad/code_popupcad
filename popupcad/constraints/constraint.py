# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 17:25:08 2015

@author: danaukes
"""

import qt
qc = qt.QtCore
qg = qt.QtGui

import sympy
import sympy.utilities
import numpy
import numpy.linalg
import popupcad
from dev_tools.enum import enum
from popupcad.constraints.constraint_support import *     

class Constraint(object):
    name = 'Constraint'
    deletable = []

    CleanupFlags = enum(NotDeletable=101, Deletable=102)

    def __init__(self, vertex_ids, segment_ids):
        self.vertex_ids = vertex_ids
        self.segment_ids = segment_ids
        self.id = id(self)

    def copy(self, identical=True):
        new = type(self)(self.vertex_ids[:], self.segment_ids[:])
        if identical:
            new.id = self.id
        return new

    def upgrade(self, *args, **kwargs):
        return self

    def init_symbolics(self):
        self._vertices = [SymbolicVertex(id) for id in self.vertex_ids]
        self._segments = [SymbolicLine(SymbolicVertex(id1),SymbolicVertex(id2)) for id1,id2 in self.segment_ids]
        self._segment_vertices = [SymbolicVertex(id) for id in self.vertices_in_lines()]

    @classmethod
    def new(cls, *objects):
        obj = cls(*cls._define_internals(*objects))
        obj.check_valid()
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
        try:
            del self._generated_equations
        except AttributeError:
            pass

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
            self._f_jacobian = sympy.utilities.lambdify(self.variables,self.jacobian().tolist())
            return self._f_jacobian
            
    @property
    def f_constraints(self):
        try:
            return self._f_constraints
        except AttributeError:
            self._f_constraints = sympy.utilities.lambdify(self.variables,self.generated_equations)
            return self._f_constraints
            
    def mapped_f_constraints(self,*args):
        args = (self._B.dot(args))     
        y = self._A.dot(self.f_constraints(*args))
        return y

    def mapped_f_jacobian(self,*args):
        args = (self._B.dot(args))
        y = self._A.dot(self.f_jacobian(*args)).dot(self._B)
        return y

    @property
    def variables(self):
        variables = []
        for equation in self.generated_equations:
            variables.extend(equation.atoms(Variable))
        variables = set(variables)
        variables = sorted(variables,key=lambda var:str(var))
        return variables
        
    def jacobian(self):
        eq = sympy.Matrix(self.generated_equations)        
        J = eq.jacobian(self.variables)
        return J

    def build_system_mapping(self,sys_vars,num_eq,eq_indeces):
        m = num_eq
        n = len(self.generated_equations)
        o = len(self.variables)
        p = len(sys_vars)

        A = numpy.zeros((m,n))
        for ii,jj in zip(eq_indeces,range(len(self.generated_equations))):
            A[ii,jj] = 1

        B = numpy.zeros((o,p))
        for ii,item in enumerate(self.variables):
            jj = sys_vars.index(item)
            B[ii,jj] = 1

        self._A = A
        self._B = B
#        return A,B
    
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
        self.vertex_ids = list(frozenset(self.vertex_ids).intersection(current_ids))
        segment_ids = []
        for id1, id2 in self.segment_ids:
            if (id1 in current_ids) and (id2 in current_ids):
                segment_ids.append((id1, id2))
        self.segment_ids = segment_ids

    def exactly_two_points(self):
        return len(set(self.vertex_ids + self.vertices_in_lines())) == 2

    def at_least_two_points(self):
        return len(set(self.vertex_ids + self.vertices_in_lines())) >= 2

    def exactly_two_lines(self):
        return len(self.segment_ids) == 2

    def at_least_two_lines(self):
        return len(self.segment_ids) >= 2

    def at_least_one_line(self):
        return len(self.segment_ids) >= 1

    def exactly_one_point_and_one_line(self):
        return len(self.segment_ids) == 1 and len(self.vertex_ids) == 1

    def throwvalidityerror(self):
        raise WrongArguments('Need exactly one point and one line')

    def at_least_one_point(self):
        return len(set(self.vertex_ids + self.vertices_in_lines())) >= 1

    all_validity_tests = []
    all_validity_tests.append((exactly_two_points,'Need exactly two points'))
    all_validity_tests.append((at_least_two_points,'Need at least two points'))
    all_validity_tests.append((exactly_two_lines,'Need exactly two lines')) 
    all_validity_tests.append((at_least_two_lines,'Need at least two lines'))
    all_validity_tests.append((at_least_one_line,'Need at least one line'))
    all_validity_tests.append((exactly_one_point_and_one_line,'Need exactly one point and one line'))
    all_validity_tests.append((at_least_one_point,'Need at least one point'))

    validity_tests = [exactly_two_points,at_least_two_points,exactly_two_lines,at_least_two_lines,at_least_one_line,exactly_one_point_and_one_line,at_least_one_point]
    
    def check_valid(self):
        for check in self.validity_tests:
            if not check(self):
                raise WrongArguments(dict(self.all_validity_tests)[check])
                
    def valid(self):
        for check in self.validity_tests:
            if not check(self):
                return False
        return True
        
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
            obj.check_valid()
            return obj

    def copy(self, identical=True):
        new = type(self)(self.value, self.vertex_ids[:], self.segment_ids[:])
        if identical:
            new.id = self.id
        return new

    @classmethod
    def getValue(cls):
        return qg.QInputDialog.getDouble(None, 'Edit Value', 'Value', 0, popupcad.gui_negative_infinity, popupcad.gui_positive_infinity, popupcad.gui_default_decimals)

    def edit(self):
        value, ok = qg.QInputDialog.getDouble(None, "Edit Value", "Value:", self.value, popupcad.gui_negative_infinity, popupcad.gui_positive_infinity, popupcad.gui_default_decimals)
        if ok:
            self.value = value
        del self.generated_equations