# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import glob, os
import sys
from cx_Freeze import setup, Executable

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


def include_OpenGL():
    path_base = basedir+"Lib\\site-packages\\OpenGL"
    skip_count = len(path_base)
    zip_includes = [(path_base, "OpenGL")]
    for root, sub_folders, files in os.walk(path_base):
        for file_in_root in files:
            zip_includes.append(
                    ("{}".format(os.path.join(root, file_in_root)),
                     "{}".format(os.path.join("OpenGL", root[skip_count+1:], file_in_root))
                    )
            )
    return zip_includes
     
base = None
toinclude = []
includes = []
packages = []
files = []
excludes = []
toinclude = []
zipinclude2 = []
if sys.platform == "win32":
    basedir = 'C:/Python27/'
    userdir = 'C:/Users/danaukes/Documents/code projects/'

    toinclude.append((basedir+'Lib/site-packages/shapely/geos_c.dll','geos_c.dll'))
    toinclude.append((basedir+'Lib/site-packages/numpy/core/libifcoremd.dll','libifcoremd.dll'))
    toinclude.append((basedir+'Lib/site-packages/numpy/core/libmmd.dll','libmmd.dll'))
    zipinclude2 = include_OpenGL()
    includes.append("zmq")
    includes.append("zmq.utils.garbage")
    includes.append("zmq.backend.cython")
    
    packages.append("scipy.integrate.vode")
    packages.append("scipy.integrate.lsoda")
    packages.append("scipy.sparse.csgraph._validation")
    packages.append("OpenGL.platform.win32")
#    packages.append("matplotlib.backends")
    packages.append("sympy.assumptions.handlers")
    packages.append("numpy")
    packages.append("scipy")    
elif sys.platform == 'darwin':
    import site
    sites = site.getsitepackages()
    basedir = sites[0]
    userdir = '~/Documents'


explore_dirs = [
    userdir+'popupcad/popupcad/supportfiles/',
]

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "DTI Playlist",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]playlist.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]
msi_data = {}
    
for d in explore_dirs:
    files.extend(glob.glob(os.path.normpath(os.path.join(d,'*'))))
    
for f in files:
    toinclude.append((f,os.path.normpath(os.path.join('supportfiles',os.path.basename(f)))))

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "DTI Playlist",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]playlist.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

build_exe_options = {"include_msvcr":True,"include_files":toinclude,"zip_includes": zipinclude2,'packages':packages,'includes':includes,'excludes':excludes}
bdist_msi_options = {
#    'upgrade_code': '{66620F3A-DC3A-11E2-B341-002219E9B01E}',
#    'add_to_path': False,
#    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
#    'data': msi_data    
#	"Shortcut": shortcut_table,
    }
bdist_dmg_options = {}
base = None
if sys.platform == "win32":
    base = "Win32GUI"
#elif sys.platform = 'darwin'
#    base = 
#    pass

setup(  name = "popupCAD",
        author = "Daniel M. Aukes",
        author_email = "danaukes@seas.harvard.edu",
        version = "0.0.1",
        description = "popupCAD Editor",
        executables = [Executable("popupcad.py", base=base,shortcutName="popupCAD",shortcutDir="ProgramMenuFolder")],
        options={'build_exe': build_exe_options,'bdist_msi': bdist_msi_options,'bdist_dmg':bdist_dmg_options}
          )     