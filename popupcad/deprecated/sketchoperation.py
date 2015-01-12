# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import shapely.ops as ops
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.sketch import Sketch
import popupcad.widgets
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.design import NoOperation
import popupcad.geometry.customshapely as customshapely

class SketchOperation(Operation):
    name = 'SketchOperation'
    operationtypes = ['union','intersection','difference','symmetric_difference']  

#    attr_init = 'sketch','operation_link1','layer_links','function'
#    attr_init_k = tuple()
#    attr_copy = 'id','customname'
    
    def copy(self):
        new = type(self)(self.sketchid,self.operation_link1,self.layer_links,self.function,self.outputref)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SketchOperation,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,sketchid,operation_link1,layer_links,function,outputref):        
        super(SketchOperation,self).editdata()
        self.sketchid = sketchid
        self.operation_link1 = operation_link1
        self.layer_links = layer_links
        self.function = function       
        self.outputref = outputref
        self.name = 'sketch '+function

    def getoutputref(self):
        return self.outputref

    def operate(self,design):
        operationgeom = design.sketches[self.sketchid].output_csg()
        layers = [design.return_layer_definition().getlayer(item) for item in self.layer_links]        

        try:
            laminate1 = design.op_from_ref(self.operation_link1).output[self.getoutputref()].csg
        except NoOperation:
            laminate1 = Laminate(design.return_layer_definition())
        
        laminate2 = Laminate(design.return_layer_definition())
        for layer in layers:
            laminate2.replacelayergeoms(layer,[operationgeom])

        lsout = laminate1.binaryoperation(laminate2,self.function)
        return lsout

    def parentrefs(self):
        if self.operation_link1==None:
            return []
        else:
            return [self.operation_link1]
    def sketchrefs(self):
        return [self.sketchid]

    @classmethod
    def new(cls,parent,design,currentop,newsignal):
        from popupcad.guis.sketcher import Sketcher
        prioroperations = design.operations
        sketch = Sketch()
        try:
            seededrefop = prioroperations[-1].id
        except IndexError:
            seededrefop = None
        f = lambda *args:cls.addedsketch(design,newsignal,*args)
        dialog = Sketcher(parent,sketch,design,isOperation=True,selectops = True,accept_method=f)
#        dialog = popupcad.guis.sketcher.SketcherMainWindow(parent,sketch,design.return_layer_definition().layers,design.return_layer_definition().layers,prioroperations,seededrefop,cls.operationtypes,0,design,True)
#        dialog.sketchaccepted.connect(f)
        dialog.show()
        dialog.activateWindow()
        dialog.raise_()
        
    @classmethod
    def addedsketch(cls,design,newsignal,sketch,ii,jj,layer_links,kk):
        design.sketches[sketch.id]=sketch
        if ii>=0:
            ref = design.operations[ii].id
        else:
            ref = None
        function = cls.operationtypes[kk]
        operation = cls(sketch.id,ref,layer_links,function,jj)
        newsignal.emit(operation)
            
    def edit(self,parent,design,editedsignal):
        from popupcad.guis.sketcher import Sketcher
        prioroperations = design.prioroperations(self)

        layers = [design.return_layer_definition().getlayer(ref) for ref in self.layer_links]
        opindex = self.operationtypes.index(self.function)
        sketch  = design.sketches[self.sketchid]
        
        try:
            ii = design.operation_index(self.operation_link1)
        except popupcad.filetypes.design.NoOperation:
            ii = None
            
        f = lambda *args:self.editedsketch(design,editedsignal,*args)
        kk = self.operationtypes.index(self.function)
        dialog = Sketcher(parent,sketch,design,ii = ii,jj = self.outputref,kk = kk,isOperation = True,selectops = True,accept_method = f,selectedlayers= layers)
#        dialog= popupcad.guis.sketcher.SketcherMainWindow(parent,sketch,design.return_layer_definition().layers,layers,prioroperations,self.operation_link1,self.operationtypes,opindex,design,True)
#        dialog.sketchaccepted.connect(f)
        dialog.show()
        dialog.activateWindow()
        dialog.raise_()

    def editedsketch(self,design,editedsignal,sketch,ii,jj,layer_links,kk):
        design.sketches[sketch.id]=sketch
        if ii>=0:
            ref = design.operations[ii].id
        else:
            ref = None
        function = self.operationtypes[kk]
        self.editdata(sketch.id,ref,layer_links,function,jj)
        editedsignal.emit(self)
