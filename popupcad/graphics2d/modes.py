# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""


class Modes(object):
    modelist = []

    def __init__(self):
        [setattr(self, item, item) for item in self.modelist]


class InteractiveModes(Modes):
    modelist = []
    modelist.append('mode_defined')
    modelist.append('mode_edit')
    modelist.append('mode_selectable_edges')
    modelist.append('mode_render')


class EdgeVertexStates(Modes):
    modelist = []
    modelist.append('state_hover')
    modelist.append('state_neutral')
    modelist.append('state_pressed')


class EdgeVertexModes(Modes):
    modelist = []
    modelist.append('mode_normal')
    modelist.append('mode_edit')
    modelist.append('mode_select')
    modelist.append('mode_render')
