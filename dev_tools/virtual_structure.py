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
#import shutil
import glob

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

def children(module):
    a = sorted(set(dir(module)) - set(dummy_vars))
    items = [(item,getattr(module,item)) for item in a]
    modules = dict([(value.__name__,value) for key,value in items if isinstance(value,types.ModuleType)])
    modules.update(find_modules_in_directory(module))
    local_modules = dict([(key,value) for key,value in modules.items() if parent_name(key)==module.__name__])
    non_modules = dict([(key,value) for key,value in items if not isinstance(value,types.ModuleType)])

    classes = dict([(key,value) for key,value in non_modules.items() if inspect.isclass(value)])
    local_classes = dict([(key,value) for key, value in classes.items() if value.__module__==module.__name__])

    return modules,non_modules,local_classes,local_modules

def search_module_r(list_in,list_out,class_dict):
    item = list_in.pop(0)
    list_out.append(item)
    modules,non_modules,local_classes,local_modules = children(item)
    class_dict[item.__name__]=local_classes
    list_in.extend(local_modules.values())
    if not not list_in:
        search_module_r(list_in,list_out,class_dict)
    else:
        return
        
def find_modules_in_directory(module):
    directory,module_filename = os.path.split(module.__file__)
    dict1 = {}
    if module_filename=='__init__.py':
        files = glob.glob(directory+'/*.py')
        for filename in files:
            basename = os.path.split(filename)[1]
            basename = os.path.splitext(basename)[0]
            if basename !='__init__':
                modulename = module.__name__+'.'+basename
                mod= importlib.import_module(modulename)
                dict1[mod.__name__]=mod
    return dict1        
        
    
if __name__=='__main__':
    module_to_add = 'popupcad.filetypes'
    parent_package_name = parent_name(module_to_add)
    parent_package = importlib.import_module(parent_package_name)
    child_modules,child_non_modules,local_classes,local_modules = children(parent_package)
    child_names = [item.__name__ for item in child_modules.values()]
    
    top = importlib.import_module('popupcad')
    dummy,nonmods,lc,lm= children(top)

    top_level_packages = ['popupcad','dev_tools','popupcad_gazebo','popupcad_manufacturing_plugins','qt']
    
    list_in = [importlib.import_module(item) for item in top_level_packages]
    list_out = []
    class_dict = {}
    search_module_r(list_in,list_out,class_dict)
    
    class_dict2 = {}
    for key in class_dict:
        class_dict2[key] = sorted(class_dict[key].keys())
    
#    data = {}
#    data['modules'] = sorted([item.__name__ for item in list_out])
#    data['classes'] = class_dict2
    
    import yaml
    with open('project_structure.yaml','w') as f:
        yaml.dump(class_dict2,f)
        
    
#    file_modules = find_modules_in_directory(top)
    

#    importlib.__import__(parent(module_to_add))
#    c = importlib.import_module('popupcad.constraints.constraints')
#    classes_to_pull = []
#    classes_to_pull.append('popupcad.constraints.constraints')
#    
#    structure1 = ['popupcad.filetypes.constraints']
#    classes_to_add = {}
#    classes_to_add['popupcad.filetypes.constraints']=[]