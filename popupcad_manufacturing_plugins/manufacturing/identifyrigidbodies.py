# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation2 import MultiValueOperation2
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.materials.laminatesheet import Laminate
from popupcad.filetypes.layer import Layer
#from popupcad.geometry.customshapely import ShapelyPolygon
import shapely.geometry as sg
import numpy
from .identifybodies import find_minimum_xy,sort_lams


class IdentifyRigidBodies(MultiValueOperation2):
    name = 'Identify Rigid Bodies'
    show = []
    valuenames = []
    defaults = []

    def generate(self,design):
        from popupcad.materials.materials import Rigid

        generic = design.op_from_ref(self.operation_link1).output[self.getoutputref()].generic_geometry_2d()
        
        layerdef = design.layerdef()

        layer_dict = dict([(geom.id,layer) for layer,geoms in generic.items() for geom in geoms])
        geom_dict = dict([(geom.id,geom) for layer,geoms in generic.items() for geom in geoms])
#        csg_dict = dict([(geom.id,geom.outputshapely()) for layer,geoms in generic.items() for geom in geoms])

        layerdef = design.layerdef()
        rigid_geoms = []    
        
        connections = []
        source_geoms= [{'id':None,'csg':sg.Polygon()}]
        for layer in layerdef.layers:
            if isinstance(layer,Rigid):
                rigid_geoms.extend(generic[layer])
                while not not source_geoms: 
                    source_geom = source_geoms.pop()
                    new_geoms = [dict([('csg',geom.outputshapely()),('id',geom.id)]) for geom in generic[layer]]
                    for new_geom in new_geoms:
                        connection = source_geom['csg'].intersection(new_geom['csg'])
                        if not (connection.is_empty):
                            connections.append((source_geom['id'],new_geom['id']))
                source_geoms = new_geoms
            else: 
                new_source_geoms = []
                while not not source_geoms: 
                    source_geom = source_geoms.pop()
                    layer_geoms = [geom.outputshapely() for geom in generic[layer]]
                    for layer_geom in layer_geoms:
                        new_geom = source_geom['csg'].intersection(layer_geom)
                        if not (new_geom.is_empty):
                            new_source_geoms.append({'id':source_geom['id'],'csg':new_geom})                        
                source_geoms = new_source_geoms
        
        print connections
        
        ids = [geom.id for geom in rigid_geoms]
        m = len(ids)
        C = numpy.zeros((m,m),dtype = bool)
        for id1,id2 in connections:
            ii = ids.index(id1)
            jj = ids.index(id2)
            C[ii,jj]=True
            C[jj,ii]=True

        done = False
        D_last = C.copy()

        while not done:
            D = D_last.dot(C)+C
            done = (D==D_last).all()
            D_last = D
        print D

        rigid_bodies = []
        rigid_geoms_set = set(rigid_geoms[:])
        while not not rigid_geoms_set:
            geom = list(rigid_geoms_set)[0]
            ii = ids.index(geom.id)
            a = list(set((D[ii,:]==True).nonzero()[0].tolist()+[ii]))
            b = set(numpy.array(rigid_geoms)[a])    
            rigid_geoms_set-=b
            rigid_bodies.append(list(b))
        
        print rigid_bodies

        values = [tuple((numpy.array([find_minimum_xy(geom) for geom in body])).min(0)) for body in rigid_bodies]
        rigid_bodies = sort_lams(rigid_bodies,values)

        new_csgs = []
        for rigid_body in rigid_bodies:
            new_csg = Laminate(layerdef)
            for geom in rigid_body:
                new_csg.insertlayergeoms(layer_dict[geom.id],[geom.outputshapely()])
            new_csgs.append(new_csg)
        
        self.output = []
        for ii,item in enumerate(new_csgs):
            self.output.append(OperationOutput(item,'Rigid Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])
        return Laminate(design.layerdef())
                