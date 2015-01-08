# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
               
def findallconnectedneighborgeoms(design,geomid,generic_geometry):
    '''find all the connected shapes'''
    connectedgeomids = [geomid]
    testids= [geomid]
    while len(testids)>0:
        result = findconnectedneighborgeoms(design,testids.pop(),generic_geometry)
        result = list(set(result)-set(connectedgeomids))
        testids.extend(result)
        connectedgeomids.extend(result)
    return connectedgeomids

def findconnectedneighborgeoms(design,geomid,generic_geometry):
    '''find geoms in neighboring layers which are overlapping'''
    geom = design.geomrefs()[geomid]
    geom = geom.outputshapely()
    layer = findgeomlayerinstep(geomid,generic_geometry)
    neighbors = findneigborlayers(design,layer)
    validneighbors = []
    for neighbor in neighbors:
        for item in generic_geometry[neighbor]:
            shapelygeom = item.outputshapely() 
            result = geom.intersection(shapelygeom)
            if not result.is_empty:                    
                validneighbors.append(item.id)
    return validneighbors        

def findgeomlayerinstep(geomid,generic_geometry_2d):
    '''Find the layer of a laminate a given shape is in'''
    for layer,geoms in generic_geometry_2d.items():
        if geomid in [geom.id for geom in geoms]:
            return layer     
            
def findneigborlayers(design,layer):   
    '''Find the layers above and below a given layer'''
    from popupcad.materials.materials import Adhesive
    layers = design.return_layer_definition().layers
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

