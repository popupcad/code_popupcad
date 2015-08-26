# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

class Material(object):
    display = ['color', 'thickness']
    editable = ['*']
    name = 'material'
    color = (0., 0., 0., .2)
    thickness = .025
    is_rigid=False
    is_adhesive=False

    def __init__(self, thickness=None):
        if thickness is not None:
            self.thickness = thickness
        self.id = id(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

#    def __hash__(self):
#        return self.id
#
#    def __eq__(self, other):
#        if isinstance(other, type(self)):
#            return self.id == other.id
#        return False

    def upgrade(self):
        from popupcad.filetypes.material2 import Material2
        new = Material2(self.name,self.color,self.thickness,E1 = 1,E2 = 1,density = 1,poisson = .5,is_adhesive = self.is_adhesive,is_rigid = self.is_rigid,is_conductive = False)
        new.id = self.id
        return new

    def copy(self):
        from popupcad.filetypes.material2 import Material2
        new = Material2(self.name,self.color,self.thickness,E1 = 1,E2 = 1,density = 1,poisson = .5,is_adhesive = self.is_adhesive,is_rigid = self.is_rigid,is_conductive = False)
        return new
    
class Carbon_0_90_0(Material):
    is_rigid = True
    name = 'Carbon(0-90-0)'
    color = (.2, 0.2, 0.2, .2)

class Pyralux(Material):
    is_adhesive = True
    name = 'Pyralux'
    color = (175. / 256, 81. / 256, 81. / 256, .2)

class Kapton(Material):
    name = 'Kapton'
    color = (1., 1., 0., .2)

class Cardboard(Material):
    name = 'Cardboard'
    color = (1., 0., 0., .2)

class SMP(Material):
    name = 'SMP'
    color = (.75, 1, .75, .2)

class Silicone(Material):
    name = 'Silicone'
    color = (.75, .75, .75, .2)

class Aluminum(Material):
    is_rigid = True
    name = 'Aluminum'
    color = (.75, .75, .75, .2)

class Copper(Material):
    is_rigid = True
    name = 'Copper'
    color = (1., .5, .16, .2)

class FR4(Material):
    is_rigid = True
    name = 'FR4'
    color = (1., .85, .36, .2)

class Velcro(Material):
    name = 'Velcro'
    color = (0., .5, .5, .2)

class Dummy(Material):
    name = 'Dummy'
    color = (0.5, .5, .5, .2)

available_materials = [
    Carbon_0_90_0,
    Pyralux,
    Kapton,
    Cardboard,
    Silicone,
    Velcro,
    Dummy,
    Aluminum,
    Copper,
    FR4,
    SMP]
# available_materials.sort()

if __name__ == '__main__':
    from popupcad.filetypes.layerdef import LayerDef
    sublaminate = LayerDef(
        Carbon_0_90_0(),
        Pyralux(),
        Kapton(),
        Pyralux(),
        Carbon_0_90_0())
