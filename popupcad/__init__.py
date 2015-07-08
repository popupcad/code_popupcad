# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
#from __future__ import absolute_import

import sys

from shapely import speedups

# necessary for homebrewed libgeos which does not work with speedups for
# some reason.
if sys.platform != 'darwin':
    if speedups.available:
        speedups.enable()

from .global_settings import *

from popupcad.filetypes.programsettings import ProgramSettings
try:
    local_settings = ProgramSettings.load_yaml(settings_filename)
#except IOError:
#    local_settings = ProgramSettings()
except:
    local_settings = ProgramSettings()

from . import algorithms
from . import filetypes
from . import geometry
from . import graphics2d
from . import graphics3d
from . import guis
from . import manufacturing
from . import materials
from . import supportfiles
from . import widgets

import yaml
#try:
with open(user_materials_filename) as f:
    user_materials = yaml.load(f)
#except:
#    user_materials = []
