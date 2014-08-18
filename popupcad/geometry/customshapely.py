# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import shapely.geometry as sg

def iscollection(item):
    collections = [sg.MultiPolygon,sg.GeometryCollection,sg.MultiLineString,sg.multilinestring.MultiLineString]
    iscollection = [isinstance(item,cls) for cls in collections]
    return any(iscollection)

def multiinit(*geoms):
    while any([iscollection(item) for item in geoms]):
        geoms2 = []
        for item in geoms:
            if iscollection(item):
                geoms2.extend(item.geoms)
            else:
                geoms2.append(item)
        geoms = geoms2
    geoms2 = []
    for geom in geoms:
        if not geom.is_empty:
            if isinstance(geom,sg.Polygon):
                geoms2.append(ShapelyPolygon(geom.exterior,geom.interiors))
            elif isinstance(geom,sg.LineString):
                geoms2.append(ShapelyLineString(geom))
            else:
                raise(Exception('unknown type: '+str(type(geom))))
                geoms2.append(geom)
    for geom in geoms2:
        if geom.is_empty:
            raise(Exception('Empty Polygon'))
    return geoms2

class ShapelyLineString(sg.LineString):
    def genpoints_generic(self):
        coords = [coord for coord in self.coords]
        return coords,[]
        
class ShapelyPolygon(sg.Polygon):
    def genpoints_generic(self):
        exterior = [coord for coord in self.exterior.coords]
        interiors = [[coord for coord in interior.coords] for interior in self.interiors]
        return exterior,interiors
        
def unary_union_safe(listin):
    '''try to perform a unary union.  if that fails, fall back to iterative union'''    
    import shapely
    import shapely.ops as so

    try:
        return so.unary_union(listin)
    except (shapely.geos.TopologicalError,ValueError):
        workinglist = listin[:]
        try:
            result = workinglist.pop(0)
            for item in workinglist:
                try:
                    newresult = result.union(item)
                    result = newresult
                except (shapely.geos.TopologicalError,ValueError):
                    raise
            return result
        except IndexError:
#            return sg.GeometryCollection()
            raise
