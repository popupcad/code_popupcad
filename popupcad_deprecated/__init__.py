# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
import types
import sys
import popupcad_manufacturing_plugins

modules_before = sys.modules.copy()

def make_new_module(name):
    new_module = types.ModuleType(name)
    sys.modules[name] = new_module
    exec('{0}=new_module'.format(name))

def load_local(source_location,name):
    exec('from {0} import {1}'.format(source_location,name))    

def remap_module(source_location,dest_location):
    exec('{0}={1}'.format(dest_location,source_location))    
    exec('sys.modules["{0}"]={1}'.format(dest_location,source_location))    

def remap_class(source_location,dest_location):
    exec('{0}={1}'.format(dest_location,source_location))    

local_modules = []
local_modules.append('placeop4')
local_modules.append('placeop5')
local_modules.append('placeop6')
local_modules.append('sketchoperation')
local_modules.append('cutop')
local_modules.append('customsupport2')
local_modules.append('genericpolygon')

new_modules = []
new_modules.append('popupcad.plugins')
new_modules.append('popupcad.plugins.manufacturing')

my_manufacturing_modules = []
my_manufacturing_modules.append('placeop4')
my_manufacturing_modules.append('placeop5')
my_manufacturing_modules.append('placeop6')
my_manufacturing_modules.append('sketchoperation')
my_manufacturing_modules.append('cutop')
my_manufacturing_modules.append('customsupport2')

remapped_manufacturing_modules = []
remapped_manufacturing_modules.append('identifybodies')
remapped_manufacturing_modules.append('identifyrigidbodies')
remapped_manufacturing_modules.append('customsupport3')
remapped_manufacturing_modules.append('supportcandidate3')
remapped_manufacturing_modules.append('toolclearance2')
remapped_manufacturing_modules.append('autoweb3')
remapped_manufacturing_modules.append('keepout2')
remapped_manufacturing_modules.append('outersheet2')
remapped_manufacturing_modules.append('removability')

modules_remap = []
modules_remap.append(('popupcad.manufacturing.locateoperation2','popupcad.manufacturing.locateoperation'))
for module in my_manufacturing_modules:
    modules_remap.append((module,'popupcad.manufacturing.'+module))
for module in remapped_manufacturing_modules:
    modules_remap.append(('popupcad_manufacturing_plugins.manufacturing.'+module,'popupcad.manufacturing.'+module))
    modules_remap.append(('popupcad_manufacturing_plugins.manufacturing.'+module,'popupcad.plugins.manufacturing.'+module))
modules_remap.append(('popupcad.filetypes.laminate','popupcad.materials.laminatesheet'))
modules_remap.append(('popupcad.filetypes.genericshapes','popupcad.geometry.genericpolygon'))
modules_remap.append(('popupcad.filetypes.genericshapebase','popupcad.geometry.genericshapebase'))

classes_remap = []
classes_remap.append(('popupcad.geometry.vertex.ShapeVertex','popupcad.geometry.vertex.Vertex'))
classes_remap.append(('genericpolygon.GenericShape','popupcad.filetypes.genericshapes.GenericShape'))
classes_remap.append(('popupcad.filetypes.layerdef.LayerDef','popupcad.materials.LayerDef'))
classes_remap.append(('popupcad.filetypes.layerdef.LayerDef','popupcad.materials.materials.LayerDef'))
classes_remap.append(('popupcad.filetypes.layer.Layer','popupcad.filetypes.laminate.Layer'))
classes_remap.append(('popupcad.manufacturing.locateoperation2.LocateOperation2','popupcad.manufacturing.locateoperation2.LocateOperation'))

for module in local_modules:
    load_local('.',module)

for module in new_modules:
    make_new_module(module)

for item in modules_remap:
    remap_module(*item)

for item in classes_remap:
    remap_class(*item)

modules_after = sys.modules.copy()
modules_diff = list(set(modules_after.keys()) - set(modules_before.keys()))
#
#def undeprecate():
#    for path in local_modules:
#        sys.modules.pop('popupcad_deprecated.'+path)
#        try:
#            exec('del {0}'.format(path))
#        except Exception as ex:
#            print(ex,path)
#
#    for path in new_modules:
#        sys.modules.pop(path)
#        try:
#            exec('del {0}'.format(path))
#        except Exception as ex:
#            print(ex,path)
#
#    for source,path in modules_remap:
#        sys.modules.pop(path)
#        try:
#            exec('del {0}'.format(path))
#        except Exception as ex:
#            print(ex,path)
#        
#    for source,path in classes_remap:
#        try:
#            exec('del {0}'.format(path))
#        except Exception as ex:
#            print(ex,path)
#    
#    try:
#        for path in modules_diff:
#            sys.modules.pop('popupcad_deprecated.'+path)
#            exec('del {0}'.format(path))
#            
#    except Exception as ex:
#        print(ex)