# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 09:13:58 2014

@author: danaukes
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
    #            print filename