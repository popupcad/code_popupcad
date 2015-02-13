# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:50:00 2015

@author: danb0b
"""
#import popupcad

import pynamics
pynamics.script_mode = False
#from pynamics.frame import Frame        
#from pynamics.system import System
from pynamics.variable_types import Differentiable
#from pynamics.tree_topology import TreeTopology
#from pynamics.particle import Particle
from pynamics.output import Output
from pynamics.name import Name
from sympy.physics.mechanics import dynamicsymbols,ReferenceFrame,Point,Particle
from pydevtools.pydy.kane import KanesMethod
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

import yaml
directory = 'C:\\Users\\danaukes\\popupCAD_files\\designs'
filename = 'pendulum1.cad.joints'
with open(os.path.join(directory,filename),'r') as f:
    connections = yaml.load(f)

accounting = Accounting()
accounting.add_constant(sympy.Symbol('g'),9.81)
accounting.add_constant(sympy.Symbol('k'),1e3)
accounting.add_constant(sympy.Symbol('b'),1e2)
g,k,b = symbols('g,k,b')

unused_connections = dict(connections)

bodies = []
for line,items in connections:
    for item in items:
        if not item in bodies:
            bodies.append(item)
        
#bodies = [value[1] for value in connections]
#bodies = list(set([item for list1 in bodies for item in list1]))
frames = [ReferenceFrame(body.get_basename()) for body in bodies]
frame_dict = dict([(body,frame) for body,frame in zip(bodies,frames)])
body_dict = dict([(frame,body) for body,frame in zip(bodies,frames)])

connections_rev = dict([(frozenset([frame_dict[value1],frame_dict[value2]]),key) for key,(value1,value2) in connections])

top = bodies[2]
top_frame = frame_dict[top]
searched = {}
searchqueue = [top]

while not not searchqueue:
    current = searchqueue.pop()
    searched[current]=[]
    for line,connection in connections:
        if current in connection:
            other = connection[1-connection.index(current)]
            if (not other in searched) and (not other in searchqueue):
                searchqueue.append(other)
                searched[current].append((other,line))
                unused_connections.pop(line)
                
#for key in searched.keys():
#    if not searched[key]:
#        searched.pop(key)
#parent_child = dict([item for item in connections.values()])
#parent_child.update(dict([item[::-1] for item in connections.values()]))
                 
for item in bodies:
    if not item in searched:
        searched[item]=[]

def build_hierarchy(frame):
    return dict([(frame_dict[item[0]],build_hierarchy(item[0])) for item in searched[frame]])

fixed_parent_vectors = {}
fixed_parent_points = {}
kds = []
q_ind = []
u_ind = []
def build_rotations(dict1):
    ii=0
    for frame in dict1.keys():
        for child in dict1[frame].keys():
            points = numpy.c_[connections_rev[frozenset([frame,child])].exteriorpoints(),[0,0]]
            axis = points[1] - points[0]
            point = points[0] - fixed_parent_vectors[frame]
            fixed_parent_vectors[child] = point
            fixed_parent_points[child] = fixed_parent_points[frame].locatenew(Name.point(),point[0]*frame.x+point[1]*frame.y+point[2]*frame.z)
            fixed_parent_points[child].v2pt_theory(fixed_parent_points[frame], top_frame, frame)
            l = (axis.dot(axis))**.5
            axis = axis/l
            fixedaxis = axis[0]*frame.x+axis[1]*frame.y+axis[2]*frame.z
#            axisvector = axis[0]*frame.x+axis[1]*frame
            x = dynamicsymbols('x{0:04.2f}'.format(ii))
            x_d = dynamicsymbols('x{0:04.2f}'.format(ii),1)
            v = dynamicsymbols('v{0:04.2f}'.format(ii))
            v_d = dynamicsymbols('v{0:04.2f}'.format(ii),1)
            q_ind.append(x)
            u_ind.append(v)
            kds.append(x_d-v)
#            child.rotate(frame,axis.tolist(),x)  
            child.orient(frame,'Axis', [x, fixedaxis])
            child.set_ang_vel(frame, v * fixedaxis)
            
            w = child.ang_vel_in(frame)
            t_damper = -b*w
            spring_stretch = x*fixedaxis
            accounting.add_force(t_damper,w)
            accounting.add_spring_force(k,spring_stretch,w)
            ii+=1
        build_rotations(dict1[frame])

def gen_info(body):
    lam = body.toLaminate()
    #lam.unarylayeroperation('union',top.layerdef.layers,top.layerdef.layers)
    layers = lam[:]
    layer = layers[0].unary_union(layers)
    areas = numpy.array([shape.area for shape in layer.geoms])/popupcad.internal_argument_scaling**2
    centroids = numpy.array([shape.centroid.coords[0] for shape in layer.geoms])/popupcad.internal_argument_scaling
    
    area = sum(areas)
    centroid = (areas*centroids).sum(0)/area
#    print(areas,centroids,area,centroid)
    return area,centroid
    
O = Point('O')        

hierarchy = {frame_dict[top]:build_hierarchy(top)}
fixed_parent_vectors[top_frame]=numpy.array([0,0,0])
fixed_parent_points[top_frame]=O
build_rotations(hierarchy)
#TreeTopology.search(hierarchy)
accounting.set_newtonian(top_frame)
#p=Particle(system,0*N.x,1)
#gen_info(top)
#lastpoint = O
#lastframe = N
for body,frame in zip(bodies,frames):
    area, centroid = gen_info(body)
    print(area,centroid)
#    pCM = centroid[0]*frame.x+centroid[1]*frame.y
    centroid = numpy.array([centroid[0],centroid[1],0])
    fixed_point = fixed_parent_vectors[frame]
    pCM_vec = centroid - fixed_point
    pCM = pCM_vec[0]*frame.x+pCM_vec[1]*frame.y+pCM_vec[2]*frame.z
    pCM = fixed_parent_points[frame].locatenew(Name.point(),pCM)
    fixed_point = fixed_parent_points[frame]
    pCM.v2pt_theory(fixed_point, top_frame, frame)
    

#    mass = area*1
    mass = 1
    accounting.add_particle(Particle(Name.particle(),O.locatenew(Name.point(),pCM),mass))

statevariables = q_ind+u_ind

points1 = [point.get_point().pos_from(O) for point in accounting.particles]
points1 = [[point.dot(top_frame.x),point.dot(top_frame.y),point.dot(top_frame.z)] for point in points1]
points1 = sympy.Matrix(points1)
points1 = points1.subs(accounting.constants)
fpoints1 = sympy.lambdify(statevariables,points1)

accounting.addforcegravity(-g*top_frame.z)

t = numpy.r_[0:50:.01]
outputs = [particle.get_point().pos_from(O).dot(top_frame.z) for particle in accounting.particles]
outputs = Output(outputs,accounting.constants)


KM = KanesMethod(top_frame, q_ind=q_ind, u_ind=u_ind, kd_eqs=kds)
KM.kanes_equations(FL, BL)
sys = System(KM, constants=constants,initial_conditions=initial_conditions)

sys.times = numpy.r_[tinitial:tfinal:tstep]

x = sys.integrate()

PE = sum([particle.get_point().pos_from(O).dot(force) for particle,force in zip(BL,gravity_forces)]) - .5*k*(q1-preload1)**2 - .5*k*(q2-preload2)**2- .5*k*(q3-preload3)**2
KE = sum([particle.kinetic_energy(N) for particle in BL])
energy = KE-PE
energy = energy.subs(constants)
fEnergy = sympy.lambdify([q1,q2,q3,u1,u2,u3],energy)

pos = []
pos.append((pAcm.pos_from(O).dot(N.x),pAcm.pos_from(O).dot(N.y)))
pos.append((pBcm.pos_from(O).dot(N.x),pBcm.pos_from(O).dot(N.y)))
pos.append((pCcm.pos_from(O).dot(N.x),pCcm.pos_from(O).dot(N.y)))
pos = sympy.Matrix(pos)
pos = pos.subs(constants)
fpos = sympy.lambdify([q1,q2,q3,u1,u2,u3],pos)

plt.ion()
plt.figure()
plt.plot(x[:,0:3])
plt.show()
y = [fEnergy(*item) for item in x]
plt.figure()
plt.plot(sys.times,y)
plt.figure()
y = numpy.array([fpos(*item) for item in x])
plt.plot(y[:,:,0],y[:,:,1])
