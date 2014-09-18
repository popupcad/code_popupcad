# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.genericfile import GenericFile,popupCADFile
import popupcad.algorithms.acyclicdirectedgraph
import os 
class NoOperation(Exception):
    def __init__(self):
        Exception.__init__(self,'No Parent Operation')
        
class Design(popupCADFile):
    filetypes = {'cad':'CAD Design'}
    defaultfiletype = 'cad'
    filters,filterstring,selectedfilter = GenericFile.buildfilters(filetypes,defaultfiletype)

    @classmethod
    def lastdir(cls):
        return popupcad.lastdesigndir

    @classmethod
    def setlastdir(cls,directory):
        popupcad.lastdesigndir = directory

    def __init__(self):
        super(Design,self).__init__()
        self.operations = []
        self._layerdef  = popupcad.materials.LayerDef()
        self.id = id(self)
        self.sketches = {}
        self.subdesigns = {}
        self._basename = self.genbasename()
    
    def define_layers(self,layerdef):
        self._layerdef = layerdef
        
    def layerdef(self):
        try:
            return self._layerdef
        except AttributeError:
            self._layerdef = self.__layerdef
            del self.__layerdef
            return self._layerdef
            
    def operation_index(self,operation_ref):
        try:
            indeces = dict([(op.id,ii) for ii,op in enumerate(self.operations)])
            return indeces[operation_ref]
        except KeyError:
            raise(NoOperation)

    def op_from_ref(self,ref):
        return self.operations[self.operation_index(ref)]

    def prioroperations(self,op):
        priorindex = self.operation_index(op.id)
        prioroperations = self.operations[:priorindex]
        return prioroperations

    def layer_index(self,layer_ref):
        indeces = dict([(layer.id,ii) for ii,layer in enumerate(self.layerdef().layers)])
        return indeces[layer_ref]
        
    def copy(self,identical = True):
        new = Design()
        new.operations = [operation.copy() for operation in self.operations]
        new.define_layers(self.layerdef())
        if identical:
            new.id=self.id
        new.sketches = {}

        for key,value in self.sketches.items():
            new.sketches[key]=value.copy(identical = True)
        new.subdesigns = {}
        
        for key,value in self.subdesigns.items():
            new.subdesigns[key]=value.copy(identical = True)

        self.copy_file_params(new,identical)

        return new    
        
#    @classmethod
#    def open(cls,reprocess,parent = None):
#        return super(Design,cls).open(parent,reprocess=reprocess)
    def addoperation(self,operation):
        if not not self.operations:
            if operation in self.operations:
                pass
            else:
                self.operations.append(operation)
        else:
            self.operations.append(operation)

    def findlocateline(self):
        for op in self.operations[::-1]:
            try:
                return self.sketches[op.locationgeometry()].operationgeometry[0]
            except AttributeError:
                pass
                
    def findlastdesignop(self):
        from popupcad.manufacturing import LocateOperation
        for op in self.operations[::-1]:
            if not isinstance(op,LocateOperation):
                return op
                
    def geomrefs(self):
        refs = []
        for op in self.operations:
            try:
                for output in op.output:
                    for layer,geoms in output.generic_geometry_2d().items():
                        for geom in geoms:
                            refs.append((geom.id,geom))
            except AttributeError:
                pass
        return dict(refs)

    def reprocessoperations(self,operations = None):

        if operations == None:
            operations = self.operations

        operations = self.network().sortedallchildrenofnodes(operations)
        for op in operations:
            op.generate(self)

    def network(self):
        nodes = [op for op in self.operations]
        connections = []
        for child in self.operations:
            for parentref in child.parentrefs():
                parent = self.op_from_ref(parentref)
                connections.append((parent,child))
        network = popupcad.algorithms.acyclicdirectedgraph.AcyclicDirectedGraph(nodes,connections)
        return network

    def cleanup_subdesigns(self):
        subdesignrefs  = []
        for op in self.operations:
            subdesignrefs.extend(op.subdesignrefs())
        unused = set(self.subdesigns.keys()) - set(subdesignrefs)
        for key in unused:
            self.subdesigns.pop(key)

    def cleanup_sketches(self):
        sketchrefs  = []
        for op in self.operations:
            sketchrefs.extend(op.sketchrefs())
        unused = set(self.sketches.keys()) - set(sketchrefs)
        for key in unused:
            self.sketches.pop(key)
        
    def loadcontrolpoints(self,opindex,output_key):
#        from popupcad.graphics2d.interactivevertex import InteractiveVertex
        vs = []
        try:
            controlpoints = self.operations[opindex].output[output_key].controlpoints()
            vs = [point.gen_interactive() for point in controlpoints]
#            for point in controlpoints:
#                v = InteractiveVertex(point)
#                v.updatefromsymbolic()
#                vs.append(v)
        except IndexError:
            pass
        except AttributeError:
            pass     
        return vs

    def loadcontrollines(self,opindex,output_key):
#        from popupcad.graphics2d.interactivevertex import InteractiveVertex
        from popupcad.graphics2d.interactiveedge import InteractiveEdge
        
        l = []
        try:
            controllines = self.operations[opindex].output[output_key].controllines()
            for line in controllines:
#                v1 = InteractiveVertex(line.vertex1)
#                v2 = InteractiveVertex(line.vertex2)
#                v1.updatefromsymbolic()
#                v2.updatefromsymbolic()
                v = InteractiveEdge(line.vertex1.gen_interactive(),line.vertex2.gen_interactive())
                v.handleupdate()
                l.append(v)
        except IndexError:
            pass
        except AttributeError:
            pass        
        return l
