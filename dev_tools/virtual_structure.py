# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import sys
import importlib
import types
#import shutil

def split(module_name):
    a = module_name.split('.')
    parent_path = '.'.join(a[:-1])
    basename = a[-1]
    return parent_path,basename

def make_new_module(new_module_path):
    new_module = types.ModuleType(new_module_path)
    sys.modules[new_module_path] = new_module

    parent_path,base_name = split(new_module_path)
    if parent_path!='':    
        parent_module = importlib.import_module(parent_path)
        setattr(parent_module,base_name,new_module)
        
    return new_module

def remap_module(old_module_path,new_module_path):
    new_module = importlib.import_module(old_module_path)
    sys.modules[new_module_path] = new_module

    parent_path,base_name = split(new_module_path)
    if parent_path!='':    
        parent_module = importlib.import_module(parent_path)
        setattr(parent_module,base_name,new_module)
    return new_module

def remap_class(old_class,new_class):
    old_path,old_basename = split(old_class)
    old_module = importlib.import_module(old_path)
    item = getattr(old_module,old_basename)

    new_path,new_basename = split(new_class)
    new_module = importlib.import_module(new_path)
    setattr(new_module,new_basename,item)

command_mapping = {}
command_mapping['make_new_module'] = make_new_module
command_mapping['remap_module'] = remap_module
command_mapping['remap_class'] = remap_class

def save_commands(commands,filename):    
    import yaml
    with open(filename,'w') as f:
        yaml.dump(commands,f)

def load_commands(filename):    
    import yaml
    with open(filename) as f:
        commands = yaml.load(f)
    return commands

def run_commands(commands):    
    for command,args in commands:
        command_mapping[command](*args)
        
if __name__=='__main__':
    modules_to_make = []
#    modules_to_make.append('popupcad.filetypes.constraints')
    
    modules_to_remap = []
#    modules_to_remap.append(('popupcad.filetypes.design','popupcad.filetypes.design2'))
#    modules_to_remap.append(('popupcad.filetypes.design','ogle'))
    
    remap_classes = []
#    remap_classes.append(['popupcad.constraints.constraint_system.ConstraintSystem', 'popupcad.filetypes.constraints.ConstraintSystem'])
#    remap_classes.append(['popupcad.constraints.constraints.FixedConstraint', 'popupcad.filetypes.constraints.fixed'])
#    remap_classes.append(['popupcad.constraints.constraints.HorizontalConstraint', 'popupcad.filetypes.constraints.horizontal'])
#    remap_classes.append(['popupcad.constraints.constraints.VerticalConstraint', 'popupcad.filetypes.constraints.vertical'])
#    remap_classes.append(['popupcad.constraints.constraints.DistanceConstraint', 'popupcad.filetypes.constraints.distance'])
#    remap_classes.append(['popupcad.constraints.constraints.CoincidentConstraint', 'popupcad.filetypes.constraints.coincident'])
#    remap_classes.append(['popupcad.constraints.constraints.XDistanceConstraint', 'popupcad.filetypes.constraints.distancex'])
#    remap_classes.append(['popupcad.constraints.constraints.YDistanceConstraint', 'popupcad.filetypes.constraints.distancey'])
#    remap_classes.append(['popupcad.constraints.constraints.AngleConstraint', 'popupcad.filetypes.constraints.angle'])
#    remap_classes.append(['popupcad.constraints.constraints.ParallelLinesConstraint', 'popupcad.filetypes.constraints.parallel'])
#    remap_classes.append(['popupcad.constraints.constraints.EqualLengthLinesConstraint', 'popupcad.filetypes.constraints.equal'])
#    remap_classes.append(['popupcad.constraints.constraints.PerpendicularLinesConstraint', 'popupcad.filetypes.constraints.perpendicular'])
#    remap_classes.append(['popupcad.constraints.constraints.PointLineDistanceConstraint', 'popupcad.filetypes.constraints.PointLine'])
#    remap_classes.append(['popupcad.constraints.constraints.LineMidpointConstraint', 'popupcad.filetypes.constraints.LineMidpoint'])
#    remap_classes.append(['popupcad.constraints.constraint_support.SymbolicLine', 'popupcad.filetypes.constraints.SymbolicLine'])
#    remap_classes.append(['popupcad.constraints.constraint_support.SymbolicVertex', 'popupcad.filetypes.constraints.SymbolicVertex'])
    
    commands = []
    for item in modules_to_make:
        commands.append(['make_new_module',[item]])
    for item in modules_to_remap:
        commands.append(['remap_module',list(item)])
    for item in remap_classes:
        commands.append(['remap_class',item])
        

    filename = 'C:/Users/daukes/code/popupcad/popupcad/supportfiles/virtual_structure.yaml'
    save_commands(commands,filename)
#    commands2 = load_commands(filename)
#    for command,args in commands2:
#        command_mapping[command](*args)
