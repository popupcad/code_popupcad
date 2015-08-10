# -*- coding: utf-8 -*-
from . import gazebo_controller

#import external modules
import PIL
import PySide
import array
from . import enhanced_grid
from . import gradient
from . import image
import lxml
import multiprocessing
from . import perlin_noise
import pygazebo
import trollius

def initialize(program):
    projectactions =[]
    projectactions.append(
            {'text': 'Run Simulation', 'kwargs': {'triggered': lambda:gazebo_controller.export(program)}})
    program.editor.addMenu(projectactions, name='Gazebo')

