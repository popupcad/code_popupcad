# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
def findgeomlayerindesign(design,geomid,opref=None,output_key = None):
    '''Search through a design file for a given geom id, and return the layer, operation, and output index'''
    if opref != None:
        op = design.op_from_ref(opref)
        if output_key != None:
            generic_geometry_2d = op.output[output_key].generic_geometry_2d()
            result = findgeomlayerinstep(geomid,generic_geometry_2d)
            return result, opref, output_key
        else:
            for index,output in enumerate(op.output):
                result = findgeomlayerinstep(geomid,output.generic_geometry_2d())
                if result!=None:
                    return result,opref,index
    else:
        for op in design.operations:
            if output_key != None:
                result = findgeomlayerinstep(geomid,op.output[output_key].generic_geometry_2d())
                if result!=None:
                    return result,op.id,output_key
            else:
                for index,output in enumerate(op.output):
                    result = findgeomlayerinstep(geomid,output.generic_geometry_2d())
                    if result!=None:
                        return result,op.id,index
                        
def findgeomlayerinstep(geomid,generic_geometry_2d):
    '''Find the layer of a laminate a given shape is in'''
    for layer,geoms in generic_geometry_2d.items():
        if geomid in [geom.id for geom in geoms]:
            return layer     

               
def findallconnectedneighborgeoms(design,geomid,generic_geometry=None,opref=None):
    '''find all the connected shapes'''
    connectedgeomids = [geomid]
    testids= [geomid]
    while len(testids)>0:
        result = findconnectedneighborgeoms(design,testids.pop(),generic_geometry,opref)
        result = list(set(result)-set(connectedgeomids))
        testids.extend(result)
        connectedgeomids.extend(result)
    return connectedgeomids
            
def findconnectedneighborgeoms(design,geomid,generic_geometry=None,opref=None):
    '''find geoms in neighboring layers which are overlapping'''
    geom = design.geomrefs()[geomid]
    geom = geom.outputshapely()
    layer,opref,output_key = findgeomlayerindesign(design,geomid,opref)
    neighbors = findneigborlayers(design,layer)
    validneighbors = []
    if generic_geometry==None:
        op = design.operations[design.operation_index(opref)]
        generic_geometry = op.output[output_key].generic_geometry_2d()
    for neighbor in neighbors:
        for item in generic_geometry[neighbor]:
            shapelygeom = item.outputshapely() 
            result = geom.intersection(shapelygeom)
            if not result.is_empty:                    
                validneighbors.append(item.id)
    return validneighbors        
    
def findneigborlayers(design,layer):   
    '''Find the layers above and below a given layer'''
    from popupcad.materials.materials import Adhesive
    layers = design.layerdef().layers
    layerindex = layers.index(layer)
    nextneighbors = []
    if layerindex>0:
        neighbor = layers[layerindex-1]
        if isinstance(neighbor,Adhesive) or isinstance(layer,Adhesive):
            nextneighbors.append(neighbor)
    if layerindex<len(layers)-1:
        neighbor = layers[layerindex+1]
        if isinstance(neighbor,Adhesive) or isinstance(layer,Adhesive):
            nextneighbors.append(neighbor)
    return nextneighbors                 


def findrigidbodies(design,geomid,generic_geometry):
    '''find all the rigidly connected bodies'''
    pass
