# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 16:58:46 2015

@author: danaukes
"""


if __name__=='__main__':

    import sys
    
    import qt
    qc = qt.QtCore
    qg = qt.QtGui
    
    app = qg.QApplication([sys.argv[0]])
    import popupcad

    item1 = popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists([(0,0),(1,0),(0,1)],[])
    item2 = popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists([(0,0),(1,0),(0,1)],[])
    item2.shift((3,0))

    fixed_vertices =[item1.exterior[0]]

    constraint1 = popupcad.filetypes.constraints.fixed([item.id for item in fixed_vertices],[item.getpos() for item in fixed_vertices])
    constraint_sys = popupcad.filetypes.constraints.ConstraintSystem()
    constraint_sys.add_constraint(constraint1)
    
    sketch = popupcad.filetypes.sketch.Sketch.new()
    sketch.constraintsystem = constraint_sys
    sketcher = popupcad.guis.sketcher.Sketcher(None,sketch)
    sketch = sketcher.sketch
    
    graphics_item1 = item1.outputinteractive()
    graphics_item2 = item2.outputinteractive()
    
    sketcher.scene.addItem(graphics_item1)
    sketcher.scene.addItem(graphics_item2)
    
    for ii in range(1):
        graphics_item1.generic.constrained_shift((-.1,-.1),sketch.constraintsystem)
        graphics_item1.updateshape()

    for ii in range(1):
        graphics_item2.generic.constrained_shift((-.1,-.1),sketch.constraintsystem)
        graphics_item2.updateshape()

    sketcher.show()
#    sys.exit(app.exec_())