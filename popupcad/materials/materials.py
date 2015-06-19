# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad


class Adhesive(object):
    pass


class Rigid(object):
    pass


class Material(object):
    display = ['color', 'thickness']
    editable = ['*']
#    editable = ['color','thickness']
    name = 'material'
    color = (0., 0., 0., .2)
    thickness = .025

    def __init__(self, thickness=None):
        if thickness is not None:
            self.thickness = thickness
        self.id = id(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Carbon_0_90_0(Material, Rigid):
    name = 'Carbon(0-90-0)'
    color = (.2, 0.2, 0.2, .2)


class Pyralux(Material, Adhesive):
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


class Aluminum(Material, Rigid):
    name = 'Aluminum'
    color = (.75, .75, .75, .2)


class Copper(Material, Rigid):
    name = 'Copper'
    color = (1., .5, .16, .2)


class FR4(Material, Rigid):
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
