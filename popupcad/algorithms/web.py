# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.geometry.genericpolygon import GenericShapeBase
from popupcad.materials.laminatesheet import Laminate
import numpy

def supportsheet(layerdef,lsin,value):
    allext = []
    for layer,layer_geometry in lsin.layer_sequence.items():
        for geom in layer_geometry.geoms:
            geom2 = GenericShapeBase.genfromshapely(geom)
            allext.extend(geom2.exteriorpoints())
    allext = numpy.array(allext)
    minx = allext[:,0].min()-value
    miny = allext[:,1].min()-value
    maxx = allext[:,0].max()+value
    maxy = allext[:,1].max()+value
    exterior = [[minx,miny],[maxx,miny],[maxx,maxy],[minx,maxy]]
    geom = GenericShapeBase.gengenericpoly(exterior,[])
    geom = geom.outputshapely()
    ls = Laminate(layerdef)
    [ls.replacelayergeoms(layer,[geom]) for layer in layerdef.layers]
    return ls,exterior[0]

def find_outer(ls,minpoint):
    import points
    lsouter = Laminate(ls.layerdef)
    lsinner = Laminate(ls.layerdef)
    for layer,layer_geometry in ls.layer_sequence.items():
        outergeoms = []
        innergeoms = []
        for geom in layer_geometry.geoms:
            if points.pointinpoints(minpoint,GenericShapeBase.genfromshapely(geom).exteriorpoints(),GenericShapeBase.tolerance):
                outergeoms.append(geom)
            else:
                innergeoms.append(geom)
        lsouter.replacelayergeoms(layer,outergeoms)
        lsinner.replacelayergeoms(layer,innergeoms)
    return lsouter,lsinner
    
def firstpass(robot,keepout,layerdef):
    firstpass= keepout.difference(robot)
    return firstpass
    
def generate_web(robot,keepout,layerdef,value_outer,value_inner):
    buffered_keepout = keepout.buffer(value_inner)
    robot_support,minpoint = supportsheet(layerdef,robot,value_outer)
    buffered_web = robot_support.difference(buffered_keepout)
    outer_web, inner_elements = find_outer(buffered_web,minpoint)
    return robot_support, outer_web, inner_elements,buffered_keepout

def autosupport(robot,keepout,layerdef,value_inner,value_gap):
    cleanup = 1e-4
    buffered_keepout = keepout.buffer(value_inner)
    allsupport = buffered_keepout.difference(keepout)
    invalidsupport = keepout.difference(robot)
    buffered_invalidsupport = invalidsupport.buffer(-cleanup)
    buffered_invalidsupport = buffered_invalidsupport.buffer(value_gap+cleanup)
    valid_support = allsupport.difference(buffered_invalidsupport)
    buffered_valid_support = valid_support.buffer(cleanup)
    return buffered_valid_support


