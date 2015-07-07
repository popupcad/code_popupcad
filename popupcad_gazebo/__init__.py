# -*- coding: utf-8 -*-
from . import gazebo_controller


def initialize(program):
    projectactions =[]
    projectactions.append(
            {'text': 'Run Simulation', 'kwargs': {'triggered': lambda:gazebo_controller.export(program)}})
    program.editor.addMenu(projectactions, name='Gazebo')

