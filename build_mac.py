# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
import sys
from cx_Freeze import setup, Executable
import glob, os

def include_entire_directory(source_dir,dest_dir):
    m = len(source_dir)
    include = [(source_dir, dest_dir)]
    for root, subfolders, files in os.walk(source_dir):
        for filename in files:
            source = os.path.normpath(os.path.join(root, filename))
            dest = os.path.normpath(os.path.join(dest_dir, root[m+1:], filename))
            include.append((source,dest))
    return include
    
iconfile = os.path.normpath(os.path.join(popupcad.supportfiledir,'printapede.ico'))

packages = []
packages.append('popupcad')
packages.append('popupcad.algorithms')
packages.append('popupcad.filetypes')
packages.append('popupcad.geometry')
packages.append('popupcad.graphics2d')
packages.append('popupcad.graphics3d')
packages.append('popupcad.manufacturing')
packages.append('popupcad.materials')
packages.append('popupcad.supportfiles')
packages.append('popupcad.widgets')

packages.append('dev_tools')
packages.append('pypoly2tri')
packages.append('popupcad_manufacturing_plugins')
packages.append('popupcad_deprecated')

#packages.append("numpy")
#packages.append("scipy")
#packages.append('scipy.integrate.vode')
#packages.append('scipy.integrate.lsoda')
#packages.append('OpenGL.platform.darwin')
packages.append('scipy.sparse.csgraph._validation')
packages.append('scipy.special._ufuncs_cxx')
packages.append('scipy.integrate.vode')
packages.append('scipy.integrate.lsoda')
packages.append('OpenGL.platform.darwin')

include_files = []

base = None
toinclude = []
includes = []
#packages = []
files = []
excludes = []
#excludes.append'Tkinter')
#excludes.append('scipy.special')
toinclude = []
zip_includes = []

import site
sites = site.getsitepackages()
    
include_files.extend(glob.glob('/usr/local/Cellar/geos/3.4.2/lib/*.dylib'))

include_files.append(('LICENSE.txt','LICENSE.txt'))
include_files.extend(include_entire_directory(popupcad.supportfiledir,'supportfiles'))
include_files.extend(include_entire_directory('licenses','licenses'))
#include_files.extend(include_entire_directory('/Users/WOODGROUP/Desktop/newdlls',''))

     
build_exe_options = {"include_files":include_files,"zip_includes": zip_includes,'packages':packages,'includes':includes,'excludes':excludes,'icon':iconfile }

bdist_dmg_options = {}
base = None

setup_options = {}
setup_options['bdist_dmg']=bdist_dmg_options
setup_options['build_exe']=build_exe_options

setup_arguments = {}
setup_arguments['name'] = popupcad.program_name
setup_arguments['author'] = popupcad.author
setup_arguments['author_email'] = popupcad.author_email
setup_arguments['version'] = popupcad.version
setup_arguments['description'] = popupcad.description
setup_arguments['executables'] = [Executable("popupcad.py", base=base,shortcutName=popupcad.program_name,shortcutDir="ProgramMenuFolder")]
setup_arguments['options'] = setup_options

setup(**setup_arguments)      