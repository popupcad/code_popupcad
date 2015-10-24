# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import os
import popupcad
import time
import glob
import shutil
#import PySide.QtGui as qg

#app = qg.QApplication(sys.argv)
top_directory = 'C:/Users/danaukes/Desktop'
failures_directory = 'C:/Users/danaukes/Desktop/failures'
filenames = []
for directory,subdirectory,files in os.walk(top_directory):
    filenames.extend(glob.glob(directory+'/*.cad'))
print(filenames)

failed = []
passed = []

for filename in filenames:
    print(filename)
    full_filename = os.path.normpath(os.path.join(directory,filename))
    try:
        d = popupcad.filetypes.design.Design.load_yaml(full_filename)
#        d.reprocessoperations()
#        d.save_yaml(full_filename)
        passed.append(full_filename)
    except:
        failed.append(full_filename)

if not os.path.exists(failures_directory):
    os.mkdir(failures_directory)

for filename in failed:
    basename = os.path.split(filename)[1]
    newfilename = os.path.join(failures_directory,basename)
    shutil.move(filename,newfilename)
