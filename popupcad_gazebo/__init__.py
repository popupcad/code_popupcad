# -*- coding: utf-8 -*-

"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

from . import gazebo_controller

#import external modules
import PIL
import PySide
import array
import lxml
import multiprocessing
import pygazebo
import trollius

from . import enhanced_grid
from . import gradient
from . import image
from . import perlin_noise

def initialize(program):
    projectactions =[]
    projectactions.append({'text': 'Run Simulation', 'kwargs': {'triggered': lambda:gazebo_controller.export(program)}})
    program.editor.addMenu(projectactions, name='Gazebo')

