# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

class Material2(object):
    editable = ['*']

    def __init__(self,name,color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive,is_flexible):
        self.name = name
        self.color = color
        self.thickness = thickness
        self.E1 = E1
        self.E2 = E2
        self.density = density
        self.poisson = poisson
        self.is_adhesive = is_adhesive
        self.is_rigid = is_rigid
        self.is_conductive = is_conductive
        self.is_flexible = is_flexible

        self.id = id(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
    
    def copy(self,identical = True):
        try:
            self.is_flexible
        except AttributeError:
            if not (self.is_adhesive or self.is_conductive or self.is_rigid):
                self.is_flexible = True
            else:
                self.is_flexible = False
            
        new = type(self)(self.name,self.color,self.thickness,self.E1,self.E2,self.density,self.poisson,self.is_adhesive,self.is_rigid,self.is_conductive,self.is_flexible)
        
        if identical:
            new.id = self.id
        return new

    def upgrade(self):
        try:
            self.is_flexible
        except AttributeError:
            if not (self.is_adhesive or self.is_conductive or self.is_rigid):
                self.is_flexible = True
            else:
                self.is_flexible = False
        return self

    def scale_length(self,factor):
        self.thickness *= factor
        
    def to_foldable(self):
        from foldable_robotics.dynamics_info import MaterialProperty
        prop = MaterialProperty(self.name,self.color,self.thickness,self.E1,self.E2,self.density,self.poisson,self.is_adhesive,self.is_rigid,self.is_conductive,self.is_flexible)
        return prop
        
import popupcad
import yaml
with open(popupcad.internal_materials_filename) as f:
    material_defaults = yaml.load(f)


default_sublaminate_keys = material_defaults['default_sublaminate_keys']
default_material_types = material_defaults['default_material_types']

#rigid = Material2('rigid',(.5,.5,.5,.5),.1,1,1,1,.5,False,True,False)
#adhesive = Material2('adhesive',(.5,.5,.5,.5),.1,1,1,1,.5,True,False,False)
#flexible = Material2('flexible',(.5,.5,.5,.5),.1,1,1,1,.5,False,False,False)
#
#default_sublaminate_keys = ['rigid','adhesive','flexible','adhesive','rigid']
#
#default_material_types = {}
#default_material_types['rigid'] = rigid
#default_material_types['adhesive'] = adhesive
#default_material_types['flexible'] = flexible

#
default_materials = list(default_material_types.values())
default_sublaminate = [default_material_types[key].copy(identical=False) for key in default_sublaminate_keys]

#material_defaults = {}
#material_defaults['default_sublaminate_keys'] = default_sublaminate_keys
#material_defaults['default_material_types'] = default_material_types
#
#import popupcad
#import yaml

#with open(popupcad.internal_materials_filename,'w') as f:
#    yaml.dump(material_defaults,f)
