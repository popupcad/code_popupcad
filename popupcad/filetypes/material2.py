# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

class Material2(object):
    editable = ['*']

    def __init__(self,name,color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive):
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

        self.id = id(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
    
    def copy(self):
        new = type(self)(self.name,self.color,self.thickness,self.E1,self.E2,self.density,self.poisson,self.is_adhesive,self.is_rigid,self.is_conductive)
        return new

    def upgrade(self):
        return self
        
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
default_sublaminate = [default_material_types[key].copy() for key in default_sublaminate_keys]

#material_defaults = {}
#material_defaults['default_sublaminate_keys'] = default_sublaminate_keys
#material_defaults['default_material_types'] = default_material_types
#
#import popupcad
#import yaml

#with open(popupcad.internal_materials_filename,'w') as f:
#    yaml.dump(material_defaults,f)
