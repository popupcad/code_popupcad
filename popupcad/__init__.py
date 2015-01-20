# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
#from __future__ import absolute_import

import sys

from shapely import speedups
if sys.platform == 'win32':
    if speedups.available:
        speedups.enable()
elif sys.platform == 'darwin':
    pass


import os

from . import basic_functions

if hasattr(sys, 'frozen'):
    localpath = os.path.normpath(os.path.join(os.path.dirname(sys.executable),''))
else:
    localpath = sys.modules['popupcad'].__path__[0]

supportfiledir = os.path.normpath(os.path.join(localpath,'supportfiles'))
#licensedir = os.path.normpath(os.path.join(localpath,'../','licenses'))
backgroundpath = os.path.normpath(os.path.join(supportfiledir,'background6.png'))

flip_y = True

user_home_dir = os.path.expanduser('~')

internal_argument_scaling = 1e3

inkscape_mm_conversion = 1./282.22293
coreldraw_mm_conversion = 1./264.581 

zoom_max = 1.
zoom_min = .00011

version = basic_functions.return_formatted_time(specificity = 'day',small_separator = '.',big_separator='.')

default_buffer_resolution = 4

program_name = 'popupCAD'
deprecated_program_name = 'popupCAD(Compatibility)'
upgrade_tool_name = 'popupCAD Upgrade Tool'
description = 'popupCAD: A design tool for developing laminate devices'
classifiers = ['Programming Language :: Python','Programming Language :: Python :: 3']
author = 'Daniel M. Aukes'
author_email = 'danaukes@seas.harvard.edu'
url = 'http://www.popupcad.com'
#import uuid
#uuid.uuid4()
windows_uuid = '{875b89db-f819-48bf-9be4-ec93f57f29c2}'

popupcad_dirname = 'popupCAD_files'
popupcad_home_path = os.path.normpath(os.path.join(user_home_dir,popupcad_dirname))

backup_timeout = 1000*60*5
backup_limit = 10

designdir = os.path.normpath(os.path.join(popupcad_home_path ,'designs'))
importdir = os.path.normpath(os.path.join(popupcad_home_path ,'import'))
exportdir = os.path.normpath(os.path.join(popupcad_home_path ,'export'))
scriptdir = os.path.normpath(os.path.join(popupcad_home_path ,'scripts'))
sketchdir = os.path.normpath(os.path.join(popupcad_home_path ,'sketches'))
shapedir = os.path.normpath(os.path.join(popupcad_home_path ,'shapes'))
backupdir = os.path.normpath(os.path.join(popupcad_home_path ,'backup'))

settings_filename = os.path.normpath(os.path.join(popupcad_home_path ,'settings.popupcad'))

lastdir = popupcad_home_path
lastdesigndir = designdir
lastsketchdir = sketchdir
lastimportdir = importdir
lastshapedir = shapedir

subdirectories = [popupcad_home_path,designdir,importdir,exportdir,scriptdir,sketchdir,shapedir,backupdir]
for path in subdirectories:
    if not os.path.isdir(path):
        os.mkdir(path)
        


from . import algorithms
from . import constraints
from . import filetypes
from popupcad.filetypes.programsettings import ProgramSettings
try:
    settings = ProgramSettings.load_yaml(settings_filename)
except IOError:
    settings = ProgramSettings()
from . import geometry
from . import graphics2d
from . import graphics3d
from . import guis
from . import manufacturing
from . import materials
from . import supportfiles
from . import widgets

