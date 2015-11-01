# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 17:57:33 2015

@author: danaukes
"""

import sys
import os
import types
import importlib
import inspect
import shutil

#dummy = types.ModuleType('dummy')
#dummy_vars = set(dir(dummy))




with open('dummy.py','w') as f:
    f.writelines(['# -*- coding: utf-8 -*-'])
dummy = importlib.import_module('dummy')
dummy_vars = dir(dummy)
os.remove('dummy.py')
del dummy

def filter_dummy_vars(list_in):
    return sorted(set(list_in)-dummy)

def make_new_module(name):
    new_module = types.ModuleType(name)
    sys.modules[name] = new_module
    return new_module

def from_x_import_y(x, y):
    exec('from {0} import {1}'.format(x, y))

def remap_module(source_location, dest_location):
    #    print(source_location,dest_location)
    exec('{0}={1}'.format(dest_location, source_location))
    exec('sys.modules["{0}"]={1}'.format(dest_location, source_location))

def remap_class(source_location, dest_location):
    exec('{0}={1}'.format(dest_location, source_location))

def parent_name(module_name):
    return '.'.join(module_name.split('.')[:-1])

def child_modules(module):
    items = [getattr(module,item) for item in dir(module)]
    children = [item for item in items if isinstance(item,types.ModuleType)]
    return children

def get_non_modules(module):
    a = sorted(set(dir(child_modules[2])) - set(dummy_vars))
#    return list0
#    list1 = filter_dummy_vars(list0)
    items = [(item,getattr(module,item)) for item in a]
    children = dict([(key,value) for key,value in items if not isinstance(value,types.ModuleType)])
    return children

if __name__=='__main__':
    module_to_add = 'popupcad.filetypes.constraints'
    parent_package_name = parent_name(module_to_add)
    parent_package = importlib.import_module(parent_package_name)
    child_modules = child_modules(parent_package)
    child_names = [item.__name__ for item in child_modules]
    
    mod_name = child_names[2]
    mod = child_modules[2]
    nonmods = get_non_modules(mod)
    classes = dict([(key,value) for key,value in nonmods.items() if inspect.isclass(value)])
    local_classes = dict([(key,value) for key, value in classes.items() if value.__module__==mod_name])
    
    

#    importlib.__import__(parent(module_to_add))
#    c = importlib.import_module('popupcad.constraints.constraints')
#    classes_to_pull = []
#    classes_to_pull.append('popupcad.constraints.constraints')
#    
#    structure1 = ['popupcad.filetypes.constraints']
#    classes_to_add = {}
#    classes_to_add['popupcad.filetypes.constraints']=[]