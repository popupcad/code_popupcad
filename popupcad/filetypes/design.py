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
import PySide.QtCore as qc
import PySide.QtGui as qg

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
        self._layerdef  = popupcad.filetypes.layerdef.LayerDef()
        self.id = id(self)
        self.sketches = {}
        self.subdesigns = {}
        self._basename = self.genbasename()
    
    def define_layers(self,layerdef):
        self._layerdef = layerdef
        
    def return_layer_definition(self):
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

    def replace_op_refs(self,oldref,newref):
        failed_ops=[]

        self.network()
        
        oldop = self.op_from_ref(oldref[0])
        newop = self.op_from_ref(newref[0])
        
        if oldop in newop.allchildren():
            m = qg.QMessageBox()
            m.setIcon(m.Information)
            m.setText(str(oldop)+' is a child of '+str(newop))
            m.exec_()
        elif newop in oldop.allchildren():
            m = qg.QMessageBox()
            m.setIcon(m.Information)
            m.setText(str(newop)+' is a child of '+str(oldop))
            m.exec_()
        else:
            for op in self.operations:
                try:
                    op.replace_op_refs(oldref,newref)
                except AttributeError:
                    failed_ops.append(op)
            if not not failed_ops:
                m = qg.QMessageBox()
                m.setIcon(m.Warning)
                m.setText('Some operations cannot be updated')
                m.setInformativeText('Please update manually.')
                s = 'This is due to the following operations:\n'
                for child in failed_ops[:-1]:
                    s+='{0},\n'.format(str(child))
                s+='{0}'.format(str(failed_ops[-1]))
                m.setDetailedText(s)
                m.exec_()

    def prioroperations(self,op):
        priorindex = self.operation_index(op.id)
        prioroperations = self.operations[:priorindex]
        return prioroperations

    def layer_index(self,layer_ref):
        indeces = dict([(layer.id,ii) for ii,layer in enumerate(self.return_layer_definition().layers)])
        return indeces[layer_ref]
        
    def copy(self,identical = True):
        new = Design()
        new.operations = [operation.copy() for operation in self.operations]
        new.define_layers(self.return_layer_definition())
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

    def subdesigns_are_reprocessed(self,setvalue = None):
        if setvalue==None:
            try:
                return self.subdesigns_reprocessed
            except AttributeError:
                self.subdesigns_reprocessed = False
                return self.subdesigns_reprocessed
        else:
            self.subdesigns_reprocessed = setvalue

    def reprocessoperations(self,operations = None):
        if not self.subdesigns_are_reprocessed():
            for subdesign in self.subdesigns.values():
                subdesign.reprocessoperations()
            self.subdesigns_are_reprocessed(True)
        
        if operations == None:
            operations = self.operations

        operations2 = self.network().sortedallchildrenofnodes(operations)
        for op in operations2:
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
        
