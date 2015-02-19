# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:50:00 2015

@author: danb0b
"""
#import popupcad

import pynamics
pynamics.script_mode = False
from pynamics.frame import Frame        
from pynamics.system import System
from pynamics.variable_types import Differentiable,Constant
#from pynamics.tree_topology import TreeTopology
from pynamics.particle import Particle
from pynamics.output import Output
import numpy
import popupcad
import scipy.integrate
import sympy
import os

system = System()
g=Constant('g',9.81,system)
k=Constant('k',1e3,system)
b=Constant('b',1e2,system)
#N = Frame('N')

import yaml
directory = 'C:\\Users\\danaukes\\popupCAD_files\\designs'
filename = 'pendulum1.cad.joints'
with open(os.path.join(directory,filename),'r') as f:
    connections = yaml.load(f)
    
unused_connections = dict(connections)

bodies = []
for line,items in connections:
    for item in items:
        if not item in bodies:
            bodies.append(item)
        
#bodies = [value[1] for value in connections]
#bodies = list(set([item for list1 in bodies for item in list1]))
frames = [Frame(body.get_basename()) for body in bodies]
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
            if not other in searched:
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

def build_rotations(dict1):
    for parent in dict1.keys():
        for child in dict1[parent].keys():
            points = numpy.c_[connections_rev[frozenset([parent,child])].exteriorpoints(),[0,0]]
            axis = points[1] - points[0]
#            axisvector = axis[0]*parent.x+axis[1]*parent
            x,x_d,x_dd = Differentiable(system)
            child.rotate_fixed_axis_directed(parent,axis.tolist(),x,system)  
            fixedaxis = parent.connections[child].fixedaxis
            print(fixedaxis)
            fixedaxis = parent.x*fixedaxis[0]+parent.y*fixedaxis[1]+parent.z*fixedaxis[2]
            w = parent.getw_(child)
            t_damper = -b*w
            t_spring = -k*x*fixedaxis
            system.addforce(t_damper,w)
            system.addforce(t_spring,w)
        build_rotations(dict1[parent])

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
    
        

hierarchy = {frame_dict[top]:build_hierarchy(top)}
build_rotations(hierarchy)
#TreeTopology.search(hierarchy)
system.set_newtonian(top_frame)
#p=Particle(system,0*N.x,1)
#gen_info(top)
particles = []
for body,frame in zip(bodies,frames):
    area, centroid = gen_info(body)
    print(area,centroid)
    pCM = centroid[0]*frame.x+centroid[1]*frame.y
#    mass = area*1
    mass = 1
    particles.append(Particle(system,pCM,mass))

statevariables = system.get_q(0)+system.get_q(1)

points1 = [point.pCM for point in particles]
points1 = [[point.dot(top_frame.x),point.dot(top_frame.y),point.dot(top_frame.z)] for point in points1]
points1 = sympy.Matrix(points1)
points1 = points1.subs(system.constants)
fpoints1 = sympy.lambdify(statevariables,points1)

system.addforcegravity(-g*top_frame.z)

t = numpy.r_[0:50:.01]
outputs = [particle.pCM.dot(top_frame.z) for particle in particles]
outputs = Output(outputs,system.constants)

pynamics.tic()
print('solving dynamics...')
var_dd = system.solvedynamics('LU',auto_z=True)
pynamics.toc()
print('substituting constants...')
#replacement = dict([(str(item.func),sympy.Symbol(str(item.func))) for item in system.get_q(0)+system.get_q(1)])
#modules = [{'ImmutableMatrix': numpy.array},'math','mpmath','numpy',replacement]
#fvdd = sympy.lambdify(system.constants.keys(),var_dd,modules = modules)
#var_dd = fvdd(*system.constants.values())
var_dd=var_dd.subs(system.constants)
print('creating second order function...')
ini = [0]*len(statevariables)
func1 = system.createsecondorderfunction(var_dd,statevariables,system.get_q(1),func_format = 'odeint')
print('integrating...')
states=scipy.integrate.odeint(func1,ini,t,rtol=1e-5,atol=1e-5)
#states=scipy.integrate.odeint(func1,ini,t,rtol=1e-12,atol=1e-12,hmin=1e-14)
pynamics.toc()
print('calculating outputs..')
outputs.calc(statevariables,states)
pynamics.toc()
import matplotlib.pyplot as plt
plt.ion()
plt.plot(t,outputs.outputs)
from mpl_toolkits.mplot3d import Axes3D

y = numpy.array([fpoints1(*item) for item in states])
y = y.transpose(1,0,2)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for item in y:
    ax.plot(item[:,0],item[:,1],zs = item[:,2])
plt.show()


