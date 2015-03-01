# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 14:41:02 2014

@author: danaukes
"""
from popupcad.widgets.dragndroptree import DraggableTreeWidget

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.filetypes.genericlaminate import GenericLaminate
from popupcad.filetypes.operation2 import Operation2
import popupcad
from popupcad.filetypes.laminate import Laminate
import popupcad_manufacturing_plugins

class JointDef(object):
    def __init__(self,sketch,joint_layer,sublaminate_layers,width):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width

class ListWidgetItem(qg.QListWidgetItem):
    def __init__(self,data):
        self.customdata = data
        super(ListWidgetItem,self).__init__(str(data))

class SingleiListWidget(qg.QListWidget):
    editingFinished = qc.Signal()
    def __init__(self,list1,*args,**kwargs):
        super(SingleiListWidget,self).__init__(*args,**kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list1]
        self.itemClicked.connect(self.fire_signal)
    def fire_signal(self):
        self.editingFinished.emit()
    def setData(self,data):
        self.clearSelection()
        for ii in range(self.model().rowCount()):
            item = self.item(ii)
            if item.customdata == data:
                item.setSelected(True)

class MultiListWidget(qg.QListWidget):
    editingFinished = qc.Signal()
    def __init__(self,list1,*args,**kwargs):
        super(MultiListWidget,self).__init__(*args,**kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list1]
        self.setSelectionMode(self.SelectionMode.MultiSelection)
    def setData(self,data):
        self.clearSelection()
        for ii in range(self.model().rowCount()):
            item = self.item(ii)
            if item.customdata in data:
                item.setSelected(True)
            
class Table(qg.QTableWidget):
    def calc_table_width(self):
        w = sum([self.columnWidth(ii) for ii in range(self.columnCount())])
        w2 = self.frameWidth()*2
        return w+w2        
    def calc_table_width2(self):
        width = 0
        width += self.verticalHeader().width()
        width += sum([self.columnWidth(ii) for ii in range(self.columnCount())])
        width += self.style().pixelMetric(qg.QStyle.PM_ScrollBarExtent)
        width += self.frameWidth() * 2      
        return width
    def reset_min_width(self):
        self.horizontalHeader().setStretchLastSection(False)        
        self.setMinimumWidth(self.calc_table_width2())
        self.horizontalHeader().setStretchLastSection(True)        
        
class MainWidget(qg.QDialog):
    def __init__(self,design,sketches,layers,operations,jointop=None,*args,**kwargs):
        super(MainWidget,self).__init__(*args,**kwargs)
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations
        
        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.fixed = DraggableTreeWidget()
        self.fixed.linklist(self.operations)
        
        self.table= Table()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(['joint sketch','joint layer','sublaminate layers','hinge width'])
        self.table.resizeColumnsToContents()
        self.table.reset_min_width()
        self.table.setItemDelegate(Delegate())
        self.table.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        button_add = qg.QPushButton('Add')
        button_remove = qg.QPushButton('Remove')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.pressed.connect(self.row_add)
        button_remove.pressed.connect(self.row_remove)
        button_up.pressed.connect(self.row_shift_up)
        button_down.pressed.connect(self.row_shift_down)

        sublayout1 = qg.QHBoxLayout()
        sublayout1.addWidget(button_add)
        sublayout1.addWidget(button_remove)
        sublayout1.addStretch()
        sublayout1.addWidget(button_up)
        sublayout1.addWidget(button_down)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.pressed.connect(self.accept)        
        button_cancel.pressed.connect(self.reject)        

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.operation_list)
        layout.addWidget(qg.QLabel('Fixed Region'))
        layout.addWidget(self.fixed)
        layout.addWidget(self.table)
        layout.addLayout(sublayout1)
        layout.addLayout(sublayout2)
        self.setLayout(layout)

        if jointop!=None:
            try:
                op_ref,output_ii = jointop.operation_links['parent'][0]
                op_ii = design.operation_index(op_ref)
                self.operation_list.selectIndeces([(op_ii,output_ii)])
            except(IndexError,KeyError):
                pass

            try:
                fixed_ref,fixed_output_ii = jointop.operation_links['fixed'][0]
                fixed_ii = design.operation_index(fixed_ref)
                self.fixed.selectIndeces([(fixed_ii,fixed_output_ii)])
            except(IndexError,KeyError):
                pass

            for item in jointop.joint_defs:
                sketch = self.design.sketches[item.sketch]
                joint_layer = self.design.return_layer_definition().getlayer(item.joint_layer)
                sublaminate_layers = [self.design.return_layer_definition().getlayer(item2) for item2 in item.sublaminate_layers]
                self.row_add(sketch,joint_layer,sublaminate_layers,item.width)

    def row_add(self,sketch = None,joint_layer = None,sublaminate_layers = None,width = None):
        ii = self.table.rowCount()
        self.table.setRowCount(ii+1)
        item = qg.QTableWidgetItem()
        if sketch!=None:
            item.setData(qc.Qt.ItemDataRole.UserRole,sketch)
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str(sketch))
        self.table.setItem(ii,0,item)
        
        item = qg.QTableWidgetItem()
        if joint_layer!=None:
            item.setData(qc.Qt.ItemDataRole.UserRole,joint_layer)
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str(joint_layer))
        self.table.setItem(ii,1,item)
    
        item = qg.QTableWidgetItem()
        if sublaminate_layers!=None:
            item.setData(qc.Qt.ItemDataRole.UserRole,sublaminate_layers)
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str(sublaminate_layers))
        else:
            item.setData(qc.Qt.ItemDataRole.UserRole,[])
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str([]))
        self.table.setItem(ii,2,item)

        item = qg.QTableWidgetItem()
        if width!=None:
            item.setData(qc.Qt.ItemDataRole.DisplayRole,width)
        else:
            item.setData(qc.Qt.ItemDataRole.DisplayRole,0.0)
        self.table.setItem(ii,3,item)
        self.table.reset_min_width()
    def row_remove(self):
        ii = self.table.currentRow()
        kk = self.table.currentColumn()
        self.table.removeRow(ii)
        self.table.setCurrentCell(ii,kk)
    def row_shift_up(self):
        ii = self.table.currentRow()
        kk = self.table.currentColumn()
        if ii>0:
            cols = self.table.columnCount()
            items_below = [self.table.takeItem(ii,jj) for jj in range(cols)]
            items_above = [self.table.takeItem(ii-1,jj) for jj in range(cols)]
            [self.table.setItem(ii,jj,item) for item,jj in zip(items_above,range(cols))]
            [self.table.setItem(ii-1,jj,item) for item,jj in zip(items_below,range(cols))]
        self.table.setCurrentCell(ii-1,kk)
    def row_shift_down(self):
        ii = self.table.currentRow()
        kk = self.table.currentColumn()
        if ii<self.table.rowCount()-1:
            cols = self.table.columnCount()
            items_below = [self.table.takeItem(ii+1,jj) for jj in range(cols)]
            items_above = [self.table.takeItem(ii,jj) for jj in range(cols)]
            [self.table.setItem(ii+1,jj,item) for item,jj in zip(items_above,range(cols))]
            [self.table.setItem(ii,jj,item) for item,jj in zip(items_below,range(cols))]
        self.table.setCurrentCell(ii+1,kk)
    def acceptdata(self):
        from popupcad.manufacturing.joint_operation2 import JointDef
        jointdefs = []
        for ii in range(self.table.rowCount()):
            sketch = self.table.item(ii,0).data(qc.Qt.ItemDataRole.UserRole)
            joint_layer = self.table.item(ii,1).data(qc.Qt.ItemDataRole.UserRole)
            sublaminate_layers = self.table.item(ii,2).data(qc.Qt.ItemDataRole.UserRole)
            width = float(self.table.item(ii,3).data(qc.Qt.ItemDataRole.DisplayRole))
            jointdefs.append(JointDef(sketch.id,joint_layer.id,[item.id for item in sublaminate_layers],width))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        operation_links['fixed'] = self.fixed.currentRefs()
        return operation_links,jointdefs
        

class Delegate(qg.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(Delegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = SingleiListWidget(parent.parent().parent().sketches,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == 1:
            editor = SingleiListWidget(parent.parent().parent().layers,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == 2:
            editor = MultiListWidget(parent.parent().parent().layers,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == 3:
            editor = qg.QLineEdit(parent)
            val = qg.QDoubleValidator(0, 1e6, 6, editor)
            editor.setValidator(val)
            return editor
        else:
            return super(Delegate,self).createEditor(parent, option, index)
            
    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, qg.QAbstractItemDelegate.NoHint)        
    
    def updateEditorGeometry(self, editor, option, index):
        if index.column() in [0,1,2]:
            rect = option.rect
            rect.setBottom(rect.bottom()+100)
            editor.setGeometry(rect)
        else:
            editor.setGeometry(option.rect)
        
    def setEditorData(self, editor, index):
        if index.column() == 0:
            d = index.data(qc.Qt.ItemDataRole.UserRole)
            editor.setData(d)
        elif index.column() == 1:
            d = index.data(qc.Qt.ItemDataRole.UserRole)
            editor.setData(d)
        elif index.column() == 2:
            d = index.data(qc.Qt.ItemDataRole.UserRole)
            editor.setData(d)
        elif index.column() == 3:
            d = index.data()
            editor.setText(str(d))
        else:
            return super(Delegate,self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 0:
            try:
                value = editor.selectedItems()[0].customdata
                model.setData(index, str(value), qc.Qt.ItemDataRole.EditRole)        
                model.setData(index, value, qc.Qt.ItemDataRole.UserRole)        
            except IndexError:
                pass
        elif index.column() == 1:
            try:
                value = editor.selectedItems()[0].customdata
                model.setData(index, str(value), qc.Qt.ItemDataRole.EditRole)        
                model.setData(index, value, qc.Qt.ItemDataRole.UserRole)        
            except IndexError:
                pass
        elif index.column() == 2:
            values = [item.customdata for item in editor.selectedItems()]
            model.setData(index, str(values), qc.Qt.ItemDataRole.EditRole)        
            model.setData(index, values, qc.Qt.ItemDataRole.UserRole)        
        else:
            return super(Delegate,self).setModelData(editor, model, index)

class JointOperation2(Operation2):
    name = 'Joint Definition'
    resolution = 2
    
    name = 'Joint Operation'
    def copy(self):
        new = type(self)(self.operation_links,self.joint_defs)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(JointOperation2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,operation_links,joint_defs):  
        self.operation_links = operation_links
        self.joint_defs = joint_defs
        self.clear_output()

    def operate(self,design):
        joint_def = self.joint_defs[0]
        operationgeom = design.sketches[joint_def.sketch].output_csg()
        layers = [design.return_layer_definition().getlayer(joint_def.joint_layer)]
        laminate = Laminate(design.return_layer_definition())
        for layer in layers:
            laminate.replacelayergeoms(layer,operationgeom)
        return laminate


    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.prioroperations(self),self)
        return dialog

    def sketchrefs(self):
        return [item.sketch for item in self.joint_defs]
    
    def subdesignrefs(self):
        return []
    
    def generate(self,design):
        layerdef = design.return_layer_definition()
        sublaminate_layers = layerdef.layers
        sketch_result = self.operate(design)


        for joint_def in self.joint_defs:
        
            hinge_gap = joint_def.width*popupcad.internal_argument_scaling
            safe_buffer1 = .5*hinge_gap
            safe_buffer2 = .5*hinge_gap
            safe_buffer3 = .5*hinge_gap
            split_buffer = .1*hinge_gap
            
            
            hingelayer = layerdef.getlayer(joint_def.joint_layer)        
            hingelines = sketch_result.genericfromls()[hingelayer]
            hingelayer_ii = layerdef.getlayer_ii(joint_def.joint_layer)
    
            safe_sections = []
            allgeoms2 = [geom.outputshapely() for geom in hingelines]
            allgeoms3 = [Laminate(layerdef) for item in allgeoms2]
            allgeoms4 = []
            for laminate,geom in zip(allgeoms3,allgeoms2):
                laminate[hingelayer_ii] = [geom]
                allgeoms4.append(laminate.buffer(hinge_gap,resolution = self.resolution))
                
            for ii,lam in enumerate(allgeoms4):
                unsafe = Laminate.unaryoperation(allgeoms4[:ii]+allgeoms4[ii+1:],'union')
                safe_sections.append(lam.difference(unsafe.buffer(safe_buffer1,resolution = self.resolution)))
            safe = Laminate.unaryoperation(safe_sections,'union')
            unsafe = Laminate.unaryoperation(allgeoms4,'union').difference(safe.buffer(safe_buffer2,resolution = self.resolution))
            unsafe2 = unsafe.unarylayeroperation('union',[hingelayer],sublaminate_layers).buffer(safe_buffer3,resolution = self.resolution)
    
            
            buffered2 = sketch_result.buffer(split_buffer,resolution = self.resolution)
            parent_id,parent_output_index = self.operation_links['parent'][0]
            parent_index = design.operation_index(parent_id)
            last = design.operations[parent_index].output[parent_output_index].csg
            
            split1 = last.difference(unsafe2)
            split2 = split1.difference(buffered2)
            bodies= popupcad_manufacturing_plugins.algorithms.bodydetection.find(split2.genericfromls(),layerdef)
            
            bodies_generic = [item.genericfromls() for item in bodies]
            bodies_generic = [GenericLaminate(layerdef,item) for item in bodies_generic]
            
            connections = {}
            connections2 = {}
            for line,geom in zip(hingelines,safe_sections):
                connections[line]=[]
                connections2[line]=[]
                for body,body_generic in zip(bodies,bodies_generic):
                    if not geom.intersection(body).isEmpty():
                        connections[line].append(body_generic)
                        connections2[line].append(body)
            for line,geoms in connections2.items():
                connections2[line]=Laminate.unaryoperation(geoms,'union')
        
        self.connections = [(key,connections[key]) for key in hingelines]
        
        laminates = [sketch_result,safe,unsafe2,split1,split2]+bodies+list(connections2.values())
        self.output = []
        for ii,item in enumerate(laminates):
            self.output.append(OperationOutput(item,'Body {0:d}'.format(ii),self))
        self.output.insert(0,self.output[0])

