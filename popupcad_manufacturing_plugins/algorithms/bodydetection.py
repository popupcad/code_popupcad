# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
               
def findallconnectedneighborgeoms(geomid,generic_geometry,geom_dict,layerdef):
    '''find all the connected shapes'''
    connectedgeomids = [geomid]
    testids= [geomid]
    while len(testids)>0:
        result = findconnectedneighborgeoms(testids.pop(),generic_geometry,geom_dict,layerdef)
        result = list(set(result)-set(connectedgeomids))
        testids.extend(result)
        connectedgeomids.extend(result)
    [geom_dict.pop(item) for item in connectedgeomids]
    return connectedgeomids

def findconnectedneighborgeoms(geomid,generic_geometry,geom_dict,layerdef):
    '''find geoms in neighboring layers which are overlapping'''
    geom = geom_dict[geomid]
    geom = geom.outputshapely()
    layer = findgeomlayerinstep(geomid,generic_geometry)
    neighbors = layerdef.connected_neighbors(layer)
    validneighbors = []
    for neighbor in neighbors:
        for item in generic_geometry[neighbor]:
            shapelygeom = item.outputshapely() 
            result = geom.intersection(shapelygeom)
            if not result.is_empty:                    
                validneighbors.append(item.id)
            else:
                pass
    return validneighbors        

def findgeomlayerinstep(geomid,generic_geometry_2d):
    '''Find the layer of a laminate a given shape is in'''
    for layer,geoms in generic_geometry_2d.items():
        if geomid in [geom.id for geom in geoms]:
            return layer     
