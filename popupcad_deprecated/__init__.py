# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
import dev_tools
import types
import sys
import popupcad_manufacturing_plugins

modules_before = sys.modules.copy()


def make_new_module(name):
    new_module = types.ModuleType(name)
    sys.modules[name] = new_module
    exec('{0}=new_module'.format(name))


def load_local(source_location, name):
    #    print(name)
    exec('from {0} import {1}'.format(source_location, name))


def remap_module(source_location, dest_location):
    #    print(source_location,dest_location)
    exec('{0}={1}'.format(dest_location, source_location))
    exec('sys.modules["{0}"]={1}'.format(dest_location, source_location))


def remap_class(source_location, dest_location):
    exec('{0}={1}'.format(dest_location, source_location))

local_modules0 = []
local_modules0.append('multivalueoperation2')
local_modules0.append('sketchoperation2')

modules_remap0 = []
my_manufacturing_modules0 = []
my_manufacturing_modules0.append('multivalueoperation2')
my_manufacturing_modules0.append('sketchoperation2')
for module in my_manufacturing_modules0:
    modules_remap0.append((module, 'popupcad.manufacturing.' + module))
    modules_remap0.append((module, 'popupcad.plugins.manufacturing.' + module))
    modules_remap0.append((module, 'popupcad_manufacturing_plugins.' + module))

local_modules = []
local_modules.append('autoweb3')
local_modules.append('bufferop2')
local_modules.append('cleanup')
local_modules.append('customsupport2')
local_modules.append('customsupport3')
local_modules.append('cutop')
local_modules.append('cutop2')
local_modules.append('genericpolygon')
local_modules.append('identifybodies')
local_modules.append('identifyrigidbodies')
local_modules.append('jointop')
local_modules.append('keepout2')
local_modules.append('laminateoperation')
local_modules.append('layerop')
#local_modules.append('materials')
# local_modules.append('locateoperation')
local_modules.append('locateoperation2')
local_modules.append('outersheet2')
local_modules.append('placeop4')
local_modules.append('placeop5')
local_modules.append('placeop6')
local_modules.append('placeop7')
local_modules.append('removability')
local_modules.append('scrapoperation')
local_modules.append('shiftflip2')
local_modules.append('simplify')
local_modules.append('sketchoperation')
local_modules.append('supportcandidate3')
local_modules.append('toolclearance2')
local_modules.append('toolclearance3')

new_modules = []
new_modules.append('popupcad.plugins')
new_modules.append('popupcad.plugins.manufacturing')
new_modules.append('popupcad.constraints')
#new_modules.append('popupcad.materials')
# new_modules.append('popupcad.manufacturing.freeze')

my_manufacturing_modules = []
# my_manufacturing_modules.append('multivalueoperation2')
my_manufacturing_modules.append('autoweb3')
my_manufacturing_modules.append('bufferop2')
my_manufacturing_modules.append('cleanup')
my_manufacturing_modules.append('customsupport2')
my_manufacturing_modules.append('customsupport3')
my_manufacturing_modules.append('cutop')
my_manufacturing_modules.append('cutop2')
my_manufacturing_modules.append('identifybodies')
my_manufacturing_modules.append('identifyrigidbodies')
my_manufacturing_modules.append('jointop')
my_manufacturing_modules.append('keepout2')
my_manufacturing_modules.append('laminateoperation')
my_manufacturing_modules.append('layerop')
# my_manufacturing_modules.append('locateoperation')
my_manufacturing_modules.append('locateoperation2')
my_manufacturing_modules.append('outersheet2')
my_manufacturing_modules.append('placeop4')
my_manufacturing_modules.append('placeop5')
my_manufacturing_modules.append('placeop6')
my_manufacturing_modules.append('placeop7')
my_manufacturing_modules.append('removability')
my_manufacturing_modules.append('scrapoperation')
my_manufacturing_modules.append('shiftflip2')
my_manufacturing_modules.append('simplify')
my_manufacturing_modules.append('sketchoperation')
my_manufacturing_modules.append('supportcandidate3')
my_manufacturing_modules.append('toolclearance2')
my_manufacturing_modules.append('toolclearance3')

modules_remap = []
modules_remap.append(
    ('locateoperation2',
     'popupcad.manufacturing.locateoperation'))
for module in my_manufacturing_modules:
    modules_remap.append((module, 'popupcad.manufacturing.' + module))
    modules_remap.append((module, 'popupcad.plugins.manufacturing.' + module))
    modules_remap.append(
        (module,
         'popupcad_manufacturing_plugins.manufacturing.' +
         module))
modules_remap.append(
    ('popupcad_manufacturing_plugins.manufacturing.cutop2',
     'popupcad.manufacturing.cutop2'))
modules_remap.append(
    ('popupcad.filetypes.laminate',
     'popupcad.materials.laminatesheet'))
modules_remap.append(
    ('popupcad.filetypes.genericshapes',
     'popupcad.geometry.genericpolygon'))
modules_remap.append(
    ('popupcad.filetypes.genericshapebase',
     'popupcad.geometry.genericshapebase'))
modules_remap.append(
    ('popupcad.filetypes.constraints',
     'popupcad.constraints.constraints'))
modules_remap.append(
    ('popupcad.filetypes.constraints',
     'dev_tools.constraints'))
modules_remap.append(
    ('popupcad.manufacturing.freeze',
     'popupcad.manufacturing.flatten'))
#modules_remap.append(
#    ('materials',
#     'popupcad.materials.materials'))

classes_remap = []
classes_remap.append(
    ('popupcad.geometry.vertex.ShapeVertex',
     'popupcad.geometry.vertex.Vertex'))
classes_remap.append(
    ('genericpolygon.GenericShape',
     'popupcad.filetypes.genericshapes.GenericShape'))
classes_remap.append(
    ('popupcad.filetypes.layerdef.LayerDef',
     'popupcad.materials.LayerDef'))
classes_remap.append(
    ('popupcad.filetypes.layerdef.LayerDef',
     'popupcad.materials.materials.LayerDef'))
classes_remap.append(
    ('popupcad.filetypes.layer.Layer',
     'popupcad.filetypes.laminate.Layer'))
classes_remap.append(
    ('locateoperation2.LocateOperation2',
     'popupcad.manufacturing.locateoperation2.LocateOperation'))
classes_remap.append(
    ('popupcad.manufacturing.freeze.Freeze',
     'popupcad.manufacturing.flatten.Flatten'))


# load_local('.','multivalueoperation2')
# remap_module('multivalueoperation2','popupcad.manufacturing.multivalueoperation2')

for module in new_modules:
    make_new_module(module)

for module in local_modules0:
    load_local('.', module)

for item in modules_remap0:
    remap_module(*item)

for module in local_modules:
    load_local('.', module)

for item in modules_remap:
    remap_module(*item)

for item in classes_remap:
    remap_class(*item)

modules_after = sys.modules.copy()
modules_diff = list(set(modules_after.keys()) - set(modules_before.keys()))

Vertex = popupcad.geometry.vertex.Vertex
