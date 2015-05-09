# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
import types
import sys

def map_module(name,source_location,dest_location):
    exec('from {0} import {1}'.format(source_location,name))    
    exec('{0}.{1}={1}'.format(dest_location,name))    
    exec('sys.modules["{0}.{1}"]={1}'.format(dest_location,name))    

def map_module2(name,source_location,dest_location1,dest_location2):
    
#    exec('{0}.{1} = {2}.{3}'.format(dest_location1,name,source_location,name))    
#    exec('sys.modules["{0}.{1}"]={2}.{3}'.format(dest_location1,name,source_location,name))    
#    exec('sys.modules["{0}.{1}"]={2}.{3}'.format(dest_location2,name,source_location,name))    

    exec('from {1} import {0}'.format(name,source_location,dest_location1,dest_location2))    
    exec('{2}.{0} = {0}'.format(name,source_location,dest_location1,dest_location2))    
    exec('sys.modules["{2}.{0}"]={0}'.format(name,source_location,dest_location1,dest_location2))    
    exec('{3}.{0} = {0}'.format(name,source_location,dest_location1,dest_location2))    
    exec('sys.modules["{3}.{0}"]={0}'.format(name,source_location,dest_location1,dest_location2))    

import popupcad.manufacturing.locateoperation2 as locateoperation
locateoperation.LocateOperation = locateoperation.LocateOperation2
popupcad.manufacturing.locateoperation = locateoperation
sys.modules['popupcad.manufacturing.locateoperation']  = locateoperation

my_modules = []
my_modules.append(('placeop4','.','popupcad.manufacturing'))
my_modules.append(('placeop5','.','popupcad.manufacturing'))
my_modules.append(('placeop6','.','popupcad.manufacturing'))
my_modules.append(('sketchoperation','.','popupcad.manufacturing'))
my_modules.append(('cutop','.','popupcad.manufacturing'))
my_modules.append(('customsupport2','.','popupcad.manufacturing'))
for module in my_modules:
    map_module(*module)

from . import genericpolygon

remapped_modules = []
remapped_modules.append(('identifybodies','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('identifyrigidbodies','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('customsupport3','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('supportcandidate3','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('toolclearance2','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('autoweb3','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('keepout2','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('outersheet2','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))
remapped_modules.append(('removability','popupcad_manufacturing_plugins.manufacturing','popupcad.manufacturing','popupcad.plugins.manufacturing'))

try:
    import popupcad_manufacturing_plugins
    popupcad.plugins = types.ModuleType('popupcad.plugins')
    sys.modules['popupcad.plugins'] = popupcad.plugins
    popupcad.plugins.manufacturing = types.ModuleType('popupcad.plugins.manufacturing')
    sys.modules['popupcad.plugins.manufacturing'] = popupcad.plugins.manufacturing
    for module in remapped_modules:
        map_module2(*module)
#    popupcad.manufacturing.identifybodies  = popupcad_manufacturing_plugins.manufacturing.identifybodies
#    popupcad.manufacturing.identifyrigidbodies  = popupcad_manufacturing_plugins.manufacturing.identifyrigidbodies
#    popupcad.manufacturing.customsupport3  = popupcad_manufacturing_plugins.manufacturing.customsupport3
#    popupcad.manufacturing.supportcandidate3  = popupcad_manufacturing_plugins.manufacturing.supportcandidate3
#    popupcad.manufacturing.toolclearance2  = popupcad_manufacturing_plugins.manufacturing.toolclearance2
#    popupcad.manufacturing.autoweb3  = popupcad_manufacturing_plugins.manufacturing.autoweb3
#    popupcad.manufacturing.keepout2  = popupcad_manufacturing_plugins.manufacturing.keepout2
#    popupcad.manufacturing.outersheet2  = popupcad_manufacturing_plugins.manufacturing.outersheet2
#    popupcad.manufacturing.removability  = popupcad_manufacturing_plugins.manufacturing.removability
#    
#    sys.modules['popupcad.manufacturing.identifybodies']  = popupcad_manufacturing_plugins.manufacturing.identifybodies
#    sys.modules['popupcad.manufacturing.identifyrigidbodies']  = popupcad_manufacturing_plugins.manufacturing.identifyrigidbodies
#    sys.modules['popupcad.manufacturing.customsupport3']  = popupcad_manufacturing_plugins.manufacturing.customsupport3
#    sys.modules['popupcad.manufacturing.supportcandidate3']  = popupcad_manufacturing_plugins.manufacturing.supportcandidate3
#    sys.modules['popupcad.manufacturing.toolclearance2']  = popupcad_manufacturing_plugins.manufacturing.toolclearance2
#    sys.modules['popupcad.manufacturing.autoweb3']  = popupcad_manufacturing_plugins.manufacturing.autoweb3
#    sys.modules['popupcad.manufacturing.keepout2']  = popupcad_manufacturing_plugins.manufacturing.keepout2
#    sys.modules['popupcad.manufacturing.outersheet2']  = popupcad_manufacturing_plugins.manufacturing.outersheet2
#    sys.modules['popupcad.manufacturing.removability']  = popupcad_manufacturing_plugins.manufacturing.removability
#    
#    popupcad.plugins = popupcad_manufacturing_plugins
#    sys.modules['popupcad.plugins']  = popupcad_manufacturing_plugins
except ImportError:
    pass

Vertex = popupcad.geometry.vertex.ShapeVertex
popupcad.geometry.vertex.Vertex =popupcad.geometry.vertex.ShapeVertex

popupcad.materials.laminatesheet = popupcad.filetypes.laminate
sys.modules['popupcad.materials.laminatesheet']  = popupcad.filetypes.laminate
popupcad.filetypes.laminate.Layer = popupcad.filetypes.layer.Layer

popupcad.geometry.genericpolygon= popupcad.filetypes.genericshapes
sys.modules['popupcad.geometry.genericpolygon']  = popupcad.filetypes.genericshapes
popupcad.filetypes.genericshapes.GenericShape = genericpolygon.GenericShape

popupcad.geometry.genericshapebase= popupcad.filetypes.genericshapebase
sys.modules['popupcad.geometry.genericshapebase']  = popupcad.filetypes.genericshapebase

popupcad.materials.LayerDef = popupcad.filetypes.layerdef.LayerDef
popupcad.materials.materials.LayerDef = popupcad.filetypes.layerdef.LayerDef

