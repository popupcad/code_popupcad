# -*- coding: utf-8 -*-

"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

from . import gazebo_controller

#import external modules
import PIL

import array
import lxml
import multiprocessing
import pygazebo
import trollius
import collada
import stl

from . import enhanced_grid
from . import gradient
from . import image
from . import perlin_noise

def initialize(program):
    projectactions =[]
    projectactions.append({'text': 'Run Simulation', 'kwargs': {'triggered': lambda:gazebo_controller.export(program)}})
    projectactions.append({'text': 'Export DAE', 'kwargs': {'triggered': lambda:export_dae(program)}})
    projectactions.append({'text': 'Export STL', 'kwargs': {'triggered': lambda:export_stl(program)}})
    program.editor.addMenu(projectactions, name='Gazebo')

def export_dae(program):
    editor = program.editor
    ii, jj = editor.operationeditor.currentIndeces2()[0]
    output = editor.design.operations[ii].output[jj]
    output.generic_laminate().toDAE()

def export_stl(program):
    editor = program.editor
    ii, jj = editor.operationeditor.currentIndeces2()[0]
    output = editor.design.operations[ii].output[jj]
    output.generic_laminate().toSTL()
