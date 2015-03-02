# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.popupcad_file import popupCADFile
from dev_tools.acyclicdirectedgraph import AcyclicDirectedGraph
import PySide.QtGui as qg

class NoOperation(Exception):
    def __init__(self):
        Exception.__init__(self,'No Parent Operation')
        
class Design(popupCADFile):
    filetypes = {'cad':'CAD Design'}
    defaultfiletype = 'cad'
    filters,filterstring,selectedfilter = popupCADFile.buildfilters(filetypes,defaultfiletype)

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
        ii = self.operations.index(newop)
        jjs = [self.operations.index(item) for item in oldop.allchildren()]
        jj = min(jjs)        
        
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
        elif ii>jj:
            m = qg.QMessageBox()
            m.setIcon(m.Information)
            m.setText(str(newop)+' is below a child of '+str(oldop)+'. Please move up.')
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

    def upgrade(self,identical = True):
        new = Design()
        new.operations = [operation.upgrade() for operation in self.operations]
        new.define_layers(self.return_layer_definition())
        if identical:
            new.id=self.id
        new.sketches = {}
        for key,value in self.sketches.items():
            new.sketches[key]=value.upgrade(identical = True)
        new.subdesigns = {}
        for key,value in self.subdesigns.items():
            new.subdesigns[key]=value.upgrade(identical = True)
        self.copy_file_params(new,identical)
        new.upgrade_higher_level()
        return new    

    def upgrade_higher_level(self):
        from popupcad.manufacturing.sketchoperation2 import SketchOperation2
        from popupcad.manufacturing.simplesketchoperation import SimpleSketchOp
        from popupcad.manufacturing.laminateoperation2 import LaminateOperation2
        newoperations = []        
        ops_to_remove = []
        replacements = []
        for op0 in self.operations:
            if isinstance(op0,SketchOperation2) and op0.operation_link1!=None:
                sketch_links = {'sketch':[op0.sketchid]}
                op1 = SimpleSketchOp(sketch_links,op0.layer_links)
                a = (op0.operation_link1,op0.outputref)
                b = (op1.id,0)
                if op0.function in LaminateOperation2.unaryoperationtypes:
                    unary_links = [a,b]
                    binary_links = []
                else:
                    unary_links = [a]
                    binary_links = [b]
                operation_links = {'unary':unary_links,'binary':binary_links}
                op2 = LaminateOperation2(operation_links,op0.function)
                newoperations.append(op0)
                newoperations.append(op1)
                newoperations.append(op2)
                replacements.append(((op0.id,0),(op2.id,0)))
                ops_to_remove.append(op0)
            else:
                newoperations.append(op0)

        self.operations.clear()
        self.operations.extend(newoperations)

        for old,new in replacements:
            self.replace_op_refs(old,new)
        for op in ops_to_remove:
            self.operations.pop(self.operations.index(op))

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
                
#    def geomrefs(self):
#        refs = []
#        for op in self.operations:
#            try:
#                for output in op.output:
#                    for layer,geoms in output.generic_geometry_2d().items():
#                        for geom in geoms:
#                            refs.append((geom.id,geom))
#            except AttributeError:
#                pass
#        return dict(refs)

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

#        operations2 = self.network().sortedallchildrenofnodes(operations)
#        for op in operations2:
        for op in self.operations:
            print(self._basename,op,self.operations.index(op))
            op.generate(self)

    def network(self):
        nodes = [op for op in self.operations]
        connections = []
        for child in self.operations:
            for parentref in child.parentrefs():
                parent = self.op_from_ref(parentref)
                connections.append((parent,child))
        network = AcyclicDirectedGraph(nodes,connections)
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
        

    def save_joint_def(self):
        import yaml
        import os
        for op in self.operations:
            try:
                filename = os.path.normpath(os.path.join(self.filename()+'.joints',))
                with open(filename,'w') as f:
                    yaml.dump((op.connections,op.fixed_bodies),f)
            except AttributeError:
                pass
