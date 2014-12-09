# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


import sys
import os

def clear_compiled():
    folder = './'
    folder = os.path.realpath(folder)
    folder = os.path.normpath(folder)
    
    a=os.walk(folder)
    for directory,subdirectories,files in a:
        for filename in files:
            if filename.rfind('.pyc')!=-1:
                os.remove(os.path.join(directory,filename))
    #            print(filename)

if __name__=='__main__':
    clear_compiled()