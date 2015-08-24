# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 19:54:09 2015

@author: danaukes
"""

import popupcad
import sympy

sketch = popupcad.filetypes.sketch.Sketch.load_yaml('C:/Users/danaukes/Desktop/74837632.sketch')
def supply_vertices():
    return sketch.operationgeometry[0].vertices()
sys = sketch.constraintsystem
sys.link_vertex_builder(supply_vertices)
sys.cleanup()
sys.regenerate()
sys.update()

constraint = sys.constraints[-1]