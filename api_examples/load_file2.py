# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 09:17:14 2015

@author: danaukes
"""

import os
import sys
import popupcad
import popupcad_deprecated

popupcad.deprecated = popupcad_deprecated
sys.modules['popupcad.deprecated'] = popupcad_deprecated

#import PySide.QtGui as qg

#app = qg.QApplication(sys.argv)
directory = 'C:/Users/danaukes/Desktop'
filename = 'inertia_test.cad'
#filename = 'SLL01.cad'
full_filename = os.path.normpath(os.path.join(directory,filename))

d = popupcad.filetypes.design.Design.load_yaml(full_filename)
d.reprocessoperations()
a=d.operations[0].output[0]
b=a.generic_laminate()
v,m,com,I = b.mass_properties()
#all_sketches = [sketch for id,sketch in d.sketches.items()]
#first_sketch = all_sketches[0]
#first_shape = first_sketch.operationgeometry[0]
#vertex_list = first_shape.exteriorpoints()

#g1 = d.operations[0].output[0].generic_laminate()
#g2 = d.operations[1].output[0].generic_laminate()
#all_sketches = [sketch for id,sketch in d.sketches.items()]
#first_sketch = all_sketches[0]
#first_shape = first_sketch.operationgeometry[0]

#sys.exit(app.exec_())