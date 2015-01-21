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
packages.append('popupcad.constraints')
packages.append('popupcad.filetypes')
packages.append('popupcad.geometry')
packages.append('popupcad.graphics2d')
packages.append('popupcad.graphics3d')
packages.append('popupcad.manufacturing')
packages.append('popupcad.materials')
packages.append('popupcad.supportfiles')
packages.append('popupcad.widgets')

packages.append('pypoly2tri')
packages.append('popupcad_manufacturing_plugins')
packages.append('popupcad_deprecated')

#packages.append("scipy.integrate.vode")
#packages.append("scipy.integrate.lsoda")
#packages.append("scipy.sparse.csgraph._validation")
#packages.append("OpenGL.platform.win32")
#packages.append("sympy.assumptions.handlers")
packages.append("numpy")
packages.append("scipy")
packages.append('scipy.integrate.vode')
packages.append('scipy.integrate.lsoda')
#packages.append('scipy.sparse.csgraph._validation')
#packages.append('sympy.assumptions.handlers')
#packages.append('scipy.special._ufuncs')
#packages.append('scipy.special._ufuncs_cxx')

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

if sys.platform=="win32":
    basedir = os.path.dirname(sys.executable)
    include_files.append((os.path.normpath(os.path.join(basedir,'Lib/site-packages/shapely/geos_c.dll')),'geos_c.dll'))
    include_files.append((os.path.normpath(os.path.join(basedir,'Lib/site-packages/numpy/core/libifcoremd.dll')),'libifcoremd.dll'))
    include_files.append((os.path.normpath(os.path.join(basedir,'Lib/site-packages/numpy/core/libifcoremd.dll')),'libifcoremd.dll'))
    include_files.append((os.path.normpath(os.path.join(basedir,'Lib/site-packages/numpy/core/libmmd.dll')),'libmmd.dll'))
elif sys.platform == 'darwin':
    import site
    sites = site.getsitepackages()
##    basedir = sites[0]
##    userdir = '~/Documents'
    packages.append('OpenGL.platform.darwin')
    
    include_files.extend(glob.glob('/usr/local/Cellar/geos/3.4.2/lib/*.dylib'))
#    zip_includes.append(('/usr/local/lib/python3.4/site-packages/scipy/.dylibs/libgcc_s.1.dylib','scipy/.dylibs/libgcc_s.1.dylib'))
#    zip_includes.append(('/usr/local/lib/python3.4/site-packages/scipy/.dylibs/libgfortran.2.0.0.dylib','scipy/.dylibs/libgfortran.2.0.0.dylib'))
#    include_files.extend(glob.glob('/usr/local/gfortran/lib/*.dylib'))

include_files.append(('LICENSE.txt','LICENSE.txt'))
include_files.extend(include_entire_directory(popupcad.supportfiledir,'supportfiles'))
include_files.extend(include_entire_directory('licenses','licenses'))

#zip_includes = include_entire_directory(os.path.normpath(os.path.join(basedir,"Lib\\site-packages\\OpenGL")),"OpenGL")
#includes.append("zmq")
#includes.append("zmq.utils.garbage")
#includes.append("zmq.backend.cython")
     
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