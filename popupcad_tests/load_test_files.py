# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import sys
import os
import popupcad
import time
import glob
import time
#import qt.QtCore as qc
#import qt.QtGui as qg


if __name__=='__main__':
#    app = qg.QApplication([sys.argv[0]])
    t_0 = time.time()
    top_directory = popupcad.test_file_dir
    filenames = []
    for directory,subdirectory,files in os.walk(top_directory):
        filenames.extend(glob.glob(directory+'/*.cad'))
    print(filenames)
    
    failed = []
    passed = []
    
    for filename in filenames:
#        print(filename)
        full_filename = os.path.normpath(os.path.join(directory,filename))
        try:
            print(full_filename)
            d = popupcad.filetypes.design.Design.load_yaml(full_filename)
            d.reprocessoperations()
            passed.append(full_filename)
        except:
            failed.append(full_filename)
    
    t_final = time.time()
    t_total = t_final - t_0

    print('passed: '+str(passed))
    print('failed: '+str(failed))

    if len(failed)>0:
        raise(Exception('some files failed to load.'))
