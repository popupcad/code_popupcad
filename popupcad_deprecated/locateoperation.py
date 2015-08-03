# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.manufacturing.sketchoperation2 import SketchOperation2

class LocateOperation(SketchOperation2):
    name = 'LocateOperation'
    operationtypes = ['locate']

    def operate(self, design):
        sketch = design.sketches[self.sketchid]
        operationgeom = popupcad.algorithms.csg_shapely.unary_union_safe(
            [item.outputshapely() for item in sketch.operationgeometry])
        lsout = Laminate(design.return_layer_definition())
        for layer in design.return_layer_definition().layers:
            lsout.replacelayergeoms(
                layer,
                popupcad.algorithms.csg_shapely.condition_shapely_entities(operationgeom))
        return lsout

    def locationgeometry(self):
        return self.sketchid

    def upgrade(self, *args, **kwargs):
        from popupcad.manufacturing.locateoperation3 import LocateOperation3
        sketch_links = {'sketch': [self.sketchid]}
        new = LocateOperation3(sketch_links)
        new.id = self.id
        return new
