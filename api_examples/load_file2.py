# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import sys
import popupcad
import time

import qt.QtCore as qc
import qt.QtGui as qg

if __name__=='__main__':
    
    t0 = time.time()
    
    app = qg.QApplication(sys.argv)
#    directory = 'C:/Users/danaukes/Desktop'
#    filename = 'slow_file.cad'
    #filename = 'SLL01.cad'
#    full_filename = os.path.normpath(os.path.join(directory,filename))
#    d = popupcad.filetypes.design.Design.load_yaml(full_filename)
    d = popupcad.filetypes.design.Design.open()
    t1 = time.time()
    print('loaded file:',t1-t0)
    d.reprocessoperations(debugprint=True)
    t2 = time.time()
    print('processed file:',t2-t1)
    d.reprocessoperations([d.operations[-1]],debugprint=True)
    t3 = time.time()
    print('processed operation:',t3-t2)
    #a=d.operations[0].output[0]
    #b=a.generic_laminate()
    #v,m,com,I = b.mass_properties()
    #all_sketches = [sketch for id,sketch in d.sketches.items()]
    #first_sketch = all_sketches[0]
    #first_shape = first_sketch.operationgeometry[0]
    #vertex_list = first_shape.exteriorpoints()
    
    #g1 = d.operations[0].output[0].generic_laminate()
    #g2 = d.operations[1].output[0].generic_laminate()
    #all_sketches = [sketch for id,sketch in d.sketches.items()]
    #first_sketch = all_sketches[0]
    #first_shape = first_sketch.operationgeometry[0]
    
    sys.exit(app.exec_())