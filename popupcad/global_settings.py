# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import sys
import os

from . import basic_functions

if hasattr(sys, 'frozen'):
    localpath = os.path.normpath(
        os.path.join(
            os.path.dirname(
                sys.executable),
            ''))
else:
    localpath = sys.modules['popupcad'].__path__[0]

supportfiledir = os.path.normpath(os.path.join(localpath, 'supportfiles'))
iconfile = os.path.normpath(os.path.join(supportfiledir, 'printapede.ico'))
graphics_scene_background_color = (.8,.8,.8,1)

flip_y = True

user_home_dir = os.path.expanduser('~')

deprecated_internal_argument_scaling = 1e3
view_scaling = 1e3
csg_processing_scaling = 1e3
triangulation_scaling = 1e3

geometry_round_value = 8
distinguishable_number_difference = 10**(-geometry_round_value)
undistinguishable_number_difference = 10**(-geometry_round_value - 1)

SI_length_scaling = 1000

inkscape_mm_conversion = 1. / 282.22293
coreldraw_mm_conversion = 1. / 264.581

zoom_max = 1.
zoom_min = 1e-6
zoom_scale_factor = 1.2
view_initial_size = 10, 10

version = basic_functions.return_formatted_time(
    specificity='day',
    small_separator='.',
    big_separator='.')

default_buffer_resolution = 4

program_name = 'popupCAD'
deprecated_program_name = 'popupCAD(Compatibility)'
upgrade_tool_name = 'popupCAD Upgrade Tool'
description = 'popupCAD: A design tool for developing laminate devices'
classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3']
author = 'Daniel M. Aukes'
author_email = 'danaukes@seas.harvard.edu'
url = 'http://www.popupcad.com'
update_url = 'http://www.popupcad.org/docs/download/'
#import uuid
# uuid.uuid4()
windows_uuid = '{875b89db-f819-48bf-9be4-ec93f57f29c2}'

popupcad_dirname = 'popupCAD_files'
popupcad_home_path = os.path.normpath(
    os.path.join(
        user_home_dir,
        popupcad_dirname))

backup_timeout = 1000 * 60 * 5
#backup_timeout = 1000 * 2
backup_limit = 10
#backup_limit = 3

designdir = os.path.normpath(os.path.join(popupcad_home_path, 'designs'))
importdir = os.path.normpath(os.path.join(popupcad_home_path, 'import'))
exportdir = os.path.normpath(os.path.join(popupcad_home_path, 'export'))
scriptdir = os.path.normpath(os.path.join(popupcad_home_path, 'scripts'))
sketchdir = os.path.normpath(os.path.join(popupcad_home_path, 'sketches'))
shapedir = os.path.normpath(os.path.join(popupcad_home_path, 'shapes'))
backupdir = os.path.normpath(os.path.join(popupcad_home_path, 'backup'))

local_settings_filename = os.path.normpath(
    os.path.join(
        popupcad_home_path,
        'settings.popupcad'))
user_materials_filename = os.path.normpath(os.path.join(popupcad_home_path,'materials.yaml'))
internal_materials_filename = os.path.normpath(os.path.join(supportfiledir,'materials.yaml'))
error_log_filename = os.path.normpath(os.path.join(popupcad_home_path,'log.txt'))

lastdir = popupcad_home_path
lastdesigndir = designdir
lastsketchdir = sketchdir
lastimportdir = importdir
lastshapedir = shapedir

subdirectories = [
    popupcad_home_path,
    designdir,
    importdir,
    exportdir,
    scriptdir,
    sketchdir,
    shapedir,
    backupdir]
for path in subdirectories:
    if not os.path.isdir(path):
        os.mkdir(path)
