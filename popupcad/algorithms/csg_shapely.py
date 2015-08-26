# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import shapely.geometry as sg
import popupcad

filter_list = [sg.Polygon,sg.LineString,sg.Point]

class GeometryNotHandled(Exception):
    pass

def entity_is_handled(entity):
    return any([isinstance(entity,item) for item in filter_list])
    
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
        [extract_individual_entities_recursive(list_in,item) for item in entity_in.geoms]
    else:
        list_in.append(entity_in)
            
def extract_individual_entities(entities):
    entities_out = []
    [extract_individual_entities_recursive(entities_out,item) for item in entities]
    return entities_out

def condition_shapely_entities(*entities):
    entities = extract_individual_entities(entities)
    entities = [item for item in entities if any([isinstance(item,classitem) for classitem in filter_list])]
    entities = [item for item in entities if not item.is_empty]
#    entities = [item for item in entities if not item.is_valid]
    return entities

def get_shapely_vertices(entity,scaling = 1.0):
    import shapely.geometry as sg
    import numpy
    
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

def to_generic(entity):
    import shapely.geometry as sg
    from popupcad.filetypes.genericshapes import GenericPoly, GenericPolyline
    from popupcad.geometry.vertex import DrawnPoint
    from popupcad.geometry.vertex import ShapeVertex

    exterior_p, interiors_p = get_shapely_vertices(entity,1/popupcad.csg_processing_scaling)
    exterior = [ShapeVertex(point) for point in exterior_p]
    interiors= [[ShapeVertex(point) for point in interior] for interior in interiors_p]

    if isinstance(entity, sg.Polygon):
        subclass = GenericPoly
    elif isinstance(entity, sg.LineString):
        subclass = GenericPolyline
    elif isinstance(entity, sg.Point):
        s = DrawnPoint(exterior_p[0])
        return s
    else:
        raise GeometryNotHandled()
    return subclass(exterior, interiors)
        
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
