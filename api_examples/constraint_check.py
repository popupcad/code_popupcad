# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
#import sympy
def supply_vertices():
    return sketch.operationgeometry[0].vertices()

if __name__=='__main__':
    
    sketch = popupcad.filetypes.sketch.Sketch.load_yaml('C:/Users/danaukes/Desktop/74837632.sketch')
    sys = sketch.constraintsystem
    sys.link_vertex_builder(supply_vertices)
    sys.cleanup()
    del sys.generator
    sys.update()
    
    constraint = sys.constraints[-1]