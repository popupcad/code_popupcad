# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:50:00 2015

@author: danb0b
"""
#import popupcad

import matplotlib.pyplot as plt
plt.ion()
from mpl_toolkits.mplot3d import Axes3D

import pynamics
pynamics.script_mode = False
#from pynamics.frame import Frame        
#from pynamics.system import System
from pynamics.variable_types import Differentiable
#from pynamics.tree_topology import TreeTopology
#from pynamics.particle import Particle
from pynamics.output import Output
from pynamics.name import Name
from sympy.physics.mechanics import dynamicsymbols,Point,Particle
from pydevtools.pydy.kane import KanesMethod
from pydevtools.pydy.reference_frame import ReferenceFrame
from pydy.system import System
import numpy
import sympy
from sympy import pi, symbols
import pydevtools.pydy
import pydevtools.pydy.functions

import numpy
import popupcad
import scipy.integrate
import sympy
import os
from pydevtools.pydy.system import System as Accounting

t_initial = 0
t_final = 5
t_step = .001

def gen_info(body):
    lam = body.toLaminate()
    #lam.unarylayeroperation('union',top.layerdef.layers,top.layerdef.layers)
    layers = lam[:]
    layer = layers[0].unary_union(layers)
    areas = numpy.array([shape.area for shape in layer.geoms])/popupcad.internal_argument_scaling**2
    centroids = numpy.array([shape.centroid.coords[0] for shape in layer.geoms])/popupcad.internal_argument_scaling
    
    area = sum(areas)
    centroid = (areas*centroids).sum(0)/area
    print(areas,centroids,area,centroid)
    return area,centroid

import yaml
directory = 'C:\\Users\\danaukes\\popupCAD_files\\designs'
filename = 'triple_pendulum.cad.joints'
with open(os.path.join(directory,filename),'r') as f:
    connections = yaml.load(f)

accounting = Accounting()
accounting.add_constant(sympy.Symbol('g'),9.81)
accounting.add_constant(sympy.Symbol('k'),1e2)
accounting.add_constant(sympy.Symbol('b'),1e1)
g,k,b = symbols('g,k,b')

unused_connections = dict(connections)

bodies = []
for line,items in connections:
    for item in items:
        if not item in bodies:
            bodies.append(item)
        
[gen_info(body) for body in bodies]
#bodies = [value[1] for value in connections]
#bodies = list(set([item for list1 in bodies for item in list1]))
frames = [ReferenceFrame(body.get_basename()) for body in bodies]
frame_dict = dict([(body,frame) for body,frame in zip(bodies,frames)])
body_dict = dict([(frame,body) for body,frame in zip(bodies,frames)])

connections_rev = dict([(frozenset([frame_dict[value1],frame_dict[value2]]),key) for key,(value1,value2) in connections])

top = bodies[0]
top_frame = frame_dict[top]
accounting.set_newtonian(top_frame)
searchqueue = [top]
searched = {}
q_ind = []
u_ind = []
kds = []

ii = 0
while not not searchqueue:
    current = searchqueue.pop()
    searched[current]=[]
    for line,connection in connections:
        if current in connection:

            other = connection[1-connection.index(current)]
            if (not other in searched) and (not other in searchqueue):
                searchqueue.append(other)
                searched[current].append((other,line))
                
                parent = frame_dict[current]
                child = frame_dict[other]
           
                points = numpy.c_[line.exteriorpoints(),[0,0]]/popupcad.internal_argument_scaling
                axis = points[1] - points[0]
                l = (axis.dot(axis))**.5
                axis = axis/l
                fixedaxis = axis[0]*parent.x+axis[1]*parent.y+axis[2]*parent.z

                x = dynamicsymbols('x'+str(ii))
                x_d = dynamicsymbols('x'+str(ii),1)
                v = dynamicsymbols('v'+str(ii))
                v_d = dynamicsymbols('v'+str(ii),1)
                q_ind.append(x)
                u_ind.append(v)
                kds.append(x_d-v)
                child.orient(parent,'Axis', [x, fixedaxis])
                child.set_ang_vel(parent, v * fixedaxis)
                
                w = child.ang_vel_in(parent)
                t_damper = -b*w
                spring_stretch = x*fixedaxis
                accounting.add_force(t_damper,w)
                accounting.add_spring_force(k,spring_stretch,w)
                                
                ii+=1
            else:
                unused_connections[line] = connection

def get_axis(parent,child):
        line = connections_rev[frozenset([parent,child])]
        points = numpy.c_[line.exteriorpoints(),[0,0]]/popupcad.internal_argument_scaling
        return points
    
particles = []
def child_velocities(parent,referencepoint,reference_coord):
    global ii,jj
    body = body_dict[parent]
    area,centroid = gen_info(body)
    centroid = numpy.r_[centroid,[0]]
    vector = centroid - reference_coord
    vector = parent.x*vector[0]+parent.y*vector[1]+parent.z*vector[2]
    P = referencepoint.locatenew(''+str(ii),vector)
    ii+=1
    P.v2pt_theory(referencepoint,top_frame,parent)
    accounting.add_particle(Particle('Part'+str(jj),P,1))
    jj+=1

    for child in parent.children:
        points = get_axis(parent,child)
        vector = points[0] - reference_coord
        vector = parent.x*vector[0]+parent.y*vector[1]+parent.z*vector[2]
        P = referencepoint.locatenew(''+str(ii),vector)
        P.v2pt_theory(referencepoint,top_frame,parent)
        ii+=1
        child_velocities(child,P,points[0])
        
O = Point('O')        
O.set_vel(top_frame, 0)
ii = 0
jj = 0
child_velocities(top_frame,O,numpy.array([0,0,0]))
        
statevariables = q_ind+u_ind

points1 = [point.get_point().pos_from(O) for point in accounting.particles]
points1 = [[point.dot(top_frame.x),point.dot(top_frame.y),point.dot(top_frame.z)] for point in points1]
points1 = sympy.Matrix(points1)
points1 = points1.subs(accounting.constants)
fpoints1 = sympy.lambdify(statevariables,points1)

accounting.addforcegravity(-g*top_frame.z)


outputs = [particle.get_point().pos_from(O).dot(top_frame.z) for particle in accounting.particles]
outputs = Output(outputs,accounting.constants)

KM = KanesMethod(top_frame, q_ind=q_ind, u_ind=u_ind, kd_eqs=kds)
KM.kanes_equations(accounting.forces, accounting.particles)

initial_conditions = dict(zip(statevariables,[0]*len(statevariables)))
sys = System(KM, constants=accounting.constants,initial_conditions=initial_conditions)

sys.times = numpy.r_[t_initial:t_final:t_step]

x = sys.integrate()

y = numpy.array([fpoints1(*item) for item in x])
y = y.transpose(1,0,2)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for item in y:
    ax.plot(item[:,0],item[:,1],zs = item[:,2])
plt.show()

plt.figure()
plt.plot(sys.times,x[:,0:3])


#PE = sum([particle.get_point().pos_from(O).dot(force) for particle,force in zip(BL,gravity_forces)]) - .5*k*(q1-preload1)**2 - .5*k*(q2-preload2)**2- .5*k*(q3-preload3)**2
#KE = sum([particle.kinetic_energy(N) for particle in BL])
#energy = KE-PE
#energy = energy.subs(accounting.constants)
#fEnergy = sympy.lambdify(statevariables,energy)
#
#pos = []
#pos.append((pAcm.pos_from(O).dot(N.x),pAcm.pos_from(O).dot(N.y)))
#pos.append((pBcm.pos_from(O).dot(N.x),pBcm.pos_from(O).dot(N.y)))
#pos.append((pCcm.pos_from(O).dot(N.x),pCcm.pos_from(O).dot(N.y)))
#pos = sympy.Matrix(pos)
#pos = pos.subs(constants)
#fpos = sympy.lambdify([q1,q2,q3,u1,u2,u3],pos)
#
#plt.ion()
#plt.figure()
#plt.plot(x[:,0:3])
#plt.show()
#y = [fEnergy(*item) for item in x]
#plt.figure()
#plt.plot(sys.times,y)
#plt.figure()
#y = numpy.array([fpos(*item) for item in x])
#plt.plot(y[:,:,0],y[:,:,1])
