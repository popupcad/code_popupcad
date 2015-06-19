# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


import sys
import os
import shutil


def clear_compiled():
    folder = './'
    folder = os.path.realpath(folder)
    folder = os.path.normpath(folder)

    a = os.walk(folder)
    for directory, subdirectories, files in a:
        for filename in files:
            if filename.rfind('.pyc') != -1:
                os.remove(os.path.join(directory, filename))
    #            print(filename)
        for subdir in subdirectories:
            if subdir == '__pycache__':
                shutil.rmtree(os.path.join(directory, subdir))

if __name__ == '__main__':
    clear_compiled()
