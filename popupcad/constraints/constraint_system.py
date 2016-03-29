# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg

import numpy
import scipy.optimize
import numpy.linalg
from popupcad.constraints.constraint_support import *     
from popupcad.constraints.constraint import Constraint

class Generator(object):
    def __init__(self,constraints,vertex_dict,objects):
        self.constraints = constraints
        self.vertex_dict = vertex_dict
        self.equations = self.get_equations()
        self.variables = self.get_variables()
#        self.build_constraint_mappings(self.constraints,self.variables,self.n_eq())
        self.regenerate_inner(objects,self.constraints,self.variables,self.n_eq())
        
    def get_equations(self):
        equations = [eq for con in self.constraints for eq in con.generated_equations]
        return equations
        
    def get_variables(self):
        variables = [item for equation in self.equations for item in list(equation.atoms(Variable))]
        variables = sorted(set(variables),key=lambda item:str(item))
        return variables

    def n_constraints(self):
        return len(self.constraints)
        
    def n_eq(self):
        return len(self.equations)
        
    def n_vars(self):
        return len(self.variables)    

    @staticmethod
    def build_constraint_mappings(constraints,variables,n_eq):
        ii = 0
        for constraint in constraints:
            l=len(constraint.generated_equations)
            constraint.build_system_mapping(variables,n_eq,range(ii,ii+l))
            ii+=l

    def regenerate_inner(self,objects,constraints,variables,n_eq):
        n_constraints = self.n_constraints()
        n_eq = self.n_eq()
        n_vars = self.n_vars()
        
        if n_constraints > 0:
            if len(objects) > 0:
                
                self.build_constraint_mappings(constraints,variables,n_eq)
                 
                def dq(q):
                    qlist = q.flatten().tolist()

                    zero = numpy.zeros(n_eq,dtype=float)
                    for constraint in self.constraints:
                        result = constraint.mapped_f_constraints(*qlist[:])
                        zero+=result

                    if n_vars > n_eq:
                        zero = numpy.r_[zero.flatten(), [0] * (n_vars - n_eq)]
                    return zero

                def j(q):
                    qlist = q.flatten().tolist()

                    jnum = numpy.zeros((n_eq,n_vars))
                    for constraint in self.constraints:
                        jnum+=constraint.mapped_f_jacobian(*qlist[:])
                    
                    if n_vars > n_eq:
                        jnum = numpy.r_[jnum, numpy.zeros((n_vars - n_eq, n_vars))]
                    return jnum
                
                self.dq = dq
                self.j = j
                self.empty = False
                return

        self.empty = True

#        return None,None
        
class ConstraintSystem(object):
    atol = 1e-10
    rtol = 1e-10

    def __init__(self):
        self.constraints = []

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

    @property
    def generator(self):
        try:
            return self._generator
        except AttributeError:
            self._generator = Generator(self.constraints,self.vertex_dict(),self.get_vertices)
            return self._generator

    @generator.deleter
    def generator(self):
        try:
            del self._generator
        except AttributeError:
            pass
        
    def update(self):
        if not self.generator.empty:
            dq = self.generator.dq
            variables = self.generator.variables
            j = self.generator.j
            vertexdict = self.generator.vertex_dict
    
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

    def update_selective(self,vertices):
        self.update()
        
    def constrained_shift(self, items):
        vertexdict = self.vertex_dict()
        ini = self.ini(vertexdict)
        if self.generator.empty:
            for vertex, dxdy in items:
                vertex.shift(dxdy)
        else:
            variables = self.generator.variables
            j = self.generator.j
            vertexdict = self.generator.vertex_dict
    
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
        for constraint in self.constraints:
            if constraint.cleanup(sketch_objects) == Constraint.CleanupFlags.Deletable:
                self.constraints.pop(self.constraints.index(constraint))