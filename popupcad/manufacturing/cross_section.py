# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtGui as qg
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.listmanager import SketchListManager
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.filetypes.laminate import Laminate

class Dialog(qg.QDialog):
    def __init__(self,design,operations):
        super(Dialog,self).__init__()
        SketchListManager(design)
        self.optree = DraggableTreeWidget()
        self.optree.linklist(operations)
        self.sketchwidget = SketchListManager(design)

        button1 = qg.QPushButton('Ok')
        button1.pressed.connect(self.accept)
        button2 = qg.QPushButton('Cancel')
        button2.pressed.connect(self.reject)
        layout2 = qg.QHBoxLayout()
        layout2.addWidget(button1)
        layout2.addWidget(button2)


        layout=qg.QVBoxLayout()
        layout.addWidget(self.optree)        
        layout.addWidget(self.sketchwidget)        
        layout.addLayout(layout2)

        self.setLayout(layout)

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        operation_links = {}
        operation_links['source'] = [self.optree.currentRefs()[0]]
        

        sketch_links= {}
        try:
            sketch_links['cross_section'] = [self.sketchwidget.itemlist.selectedItems()[0].value.id]
        except IndexError:
            pass
        
        return operation_links,sketch_links,100

class CrossSection(Operation2):
    name='Cross-Section'
    def __init__(self,*args,**kwargs):
        super(CrossSection,self).__init__()
        self.id = id(self)
        self.editdata(*args,**kwargs)

    def copy(self,identical = True):
        new = type(self)(self.operation_links,self.sketch_links,self.scale_value)
        if identical:        
            new.id = self.id
        new.customname = self.customname
        return new

    def editdata(self,operation_links,sketch_links,scale_value):
        super(CrossSection,self).editdata(operation_links,sketch_links,{})
        self.scale_value = scale_value
        
    def operate(self,design):
        from popupcad.filetypes.genericshapes import GenericLine
        import shapely.affinity as aff
        import popupcad.algorithms.points as points
        import popupcad
        import shapely.geometry as sg
        
        parent_ref,parent_index  = self.operation_links['source'][0]
        parent = design.op_from_ref(parent_ref).output[parent_index].csg
        
        sketch = design.sketches[self.sketch_links['cross_section'][0]]
        
        layerdef = design.return_layer_definition()
        laminate = Laminate(layerdef)
        for item in sketch.operationgeometry:
            if isinstance(item,GenericLine):
                line = item
                a = points.calctransformfrom2lines(line.exteriorpoints(),[(0,0),(1,0)],scale_x=1,scale_y=1)            
#                aff.affine_transform()
                sketch_csg = sketch.output_csg()
                
                for layer in layerdef.layers:
                    laminate.replacelayergeoms(layer,sketch_csg)
                result = parent.intersection(laminate)
                laminate2 = Laminate(layerdef)
                for ii,layerid in enumerate(layerdef.layers):
#                for ii,layer in enumerate(result):
                    yshift = layerdef.zvalue[layerid] * self.scale_value
                    layer = result.layer_sequence[layerid]
                    thickness = layerid.thickness*popupcad.internal_argument_scaling*self.scale_value
                    newgeoms = [item for item in layer.geoms]
                    newgeoms = [aff.affine_transform(item,a) for item in newgeoms]
#                    newgeoms = [item.buffer(bufferval) for item in newgeoms]
                    newgeoms2 = []
                    for geom in newgeoms:
                        newgeom = sg.box(geom.coords[0][0],geom.coords[0][1],geom.coords[-1][0],geom.coords[-1][1]+thickness)
                        newgeoms2.append(newgeom)
                    newgeoms = newgeoms2
                    newgeoms = [aff.translate(item,yoff = yshift) for item in newgeoms]
                    newgeoms = popupcad.geometry.customshapely.multiinit(*newgeoms)
                    laminate2[ii] = newgeoms
                return laminate2

#        return laminate
            
    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(design,design.operations)
        return dialog
    def buildeditdialog(self,design):
#        sketch = design.sketches[self.sketch_links['place'][0]]
#        subdesign = design.subdesigns[self.design_links['subdesign'][0]]
        dialog = Dialog(design,design.prioroperations(self))
        return dialog
