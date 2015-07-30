# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 11:13:54 2015

@author: danaukes
"""

import shapely.geometry as sg
import numpy

filter_list = [sg.Polygon,sg.LineString,sg.Point]

class GeometryNotHandled(Exception):
    pass

def iscollection(item):
    collections = [
        sg.MultiPolygon,
        sg.GeometryCollection,
        sg.MultiLineString,
        sg.multilinestring.MultiLineString,
        sg.MultiPoint]
    iscollection = [isinstance(item, cls) for cls in collections]
    return any(iscollection)
    
def extract_individual_entities_recursive(list_in,entity_in):
    if iscollection(entity_in):
        for item in entity_in.geoms:
            extract_individual_entities_recursive(list_in,item)
    else:
        list_in.append(entity_in)
            
def extract_individual_entities(entities):
    entities_out = [extract_individual_entities_recursive(item) for item in entities]
    return entities_out

def condition_shapely_entities(*entities):
    entities = extract_individual_entities(entities)
    entities = [item for item in entities if item in filter_list]
    entities = [item for item in entities if not item.is_empty]
#    entities = [item for item in entities if not item.is_valid]
    return entities

def get_generic_vertices(entity,scaling = 1.0):
    if isinstance(entity,sg.Polygon):
        exterior = (numpy.array([coord for coord in entity.exterior.coords])*scaling).tolist()
        interiors = [(numpy.array([coord for coord in interior.coords])*scaling).tolist()
                     for interior in entity.interiors]

    elif isinstance(entity,sg.LineString) or isinstance(entity,sg.Point):
        exterior = (numpy.array([coord for coord in entity.coords])*scaling).tolist()
        interiors = []
    else:
        raise GeometryNotHandled()

    return exterior, interiors
            
def unary_union_safe(listin):
    '''try to perform a unary union.  if that fails, fall back to iterative union'''
    import shapely
    import shapely.ops as so

    try:
        return so.unary_union(listin)
    except (shapely.geos.TopologicalError, ValueError):
        print('Unary Union Failed.  Falling Back...')
        workinglist = listin[:]
        try:
            result = workinglist.pop(0)
            for item in workinglist:
                try:
                    newresult = result.union(item)
                    result = newresult
                except (shapely.geos.TopologicalError, ValueError):
                    raise
            return result
        except IndexError:
            #            return sg.GeometryCollection()
            raise
