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
from popupcad.widgets.table_editor import Table,SingleListWidget,MultiListWidget,Delegate

def set_float_data_init(ini = 0.0):
    def set_float_data(variable):
        item = qg.QTableWidgetItem()
        if variable!=None:
            item.setData(qc.Qt.ItemDataRole.DisplayRole,variable)
        else:
            item.setData(qc.Qt.ItemDataRole.DisplayRole,ini)
        return item
    return set_float_data

def set_single_item_list(variable):
    item = qg.QTableWidgetItem()
    if variable!=None:
        item.setData(qc.Qt.ItemDataRole.UserRole,variable)
        item.setData(qc.Qt.ItemDataRole.DisplayRole,str(variable))
    return item

def set_multi_item_list(variable):
    item = qg.QTableWidgetItem()
    if variable!=None:
        item.setData(qc.Qt.ItemDataRole.UserRole,variable)
        item.setData(qc.Qt.ItemDataRole.DisplayRole,str(variable))
    else:
        item.setData(qc.Qt.ItemDataRole.UserRole,[])
        item.setData(qc.Qt.ItemDataRole.DisplayRole,str([]))
    return item

def set_editor_data_user(index,editor):
    d = index.data(qc.Qt.ItemDataRole.UserRole)
    editor.setData(d)
    
def set_editor_data_plain(index,editor):
    d = index.data()
    editor.setText(str(d))
    
def expand_editor_rect_init(bottom = 0,left = 0,right = 0):
    def expand_editor_rect(editor,option):
        rect = option.rect
        rect.setBottom(rect.bottom()+bottom)
        rect.setLeft(rect.left()-left)
        rect.setRight(rect.right()+right)
        editor.setGeometry(rect)
    return expand_editor_rect

def set_model_data_single_list(editor,model,index,delegate):
    try:
        value = editor.selectedItems()[0].customdata
        model.setData(index, str(value), qc.Qt.ItemDataRole.EditRole)        
        model.setData(index, value, qc.Qt.ItemDataRole.UserRole)        
    except IndexError:
        pass
    
def set_model_data_multi_list(editor,model,index,delegate):
    values = [item.customdata for item in editor.selectedItems()]
    model.setData(index, str(values), qc.Qt.ItemDataRole.EditRole)        
    model.setData(index, values, qc.Qt.ItemDataRole.UserRole)        
    
def set_model_data_plain(editor,model,index,delegate):
    super(Delegate,delegate).setModelData(editor,model,index)


def get_main_widget(parent):
    main_widget = parent.parent().parent()
    return main_widget
    
def get_sketches(parent):
    main_widget = get_main_widget(parent)
    return main_widget.sketches

def get_layers(parent):
    main_widget = get_main_widget(parent)
    return main_widget.layers
    
def build_single_list_editor_init(get_list):
    def build_single_list_editor(parent,delegate):
        editor = SingleListWidget(get_list(parent),parent)
        editor.editingFinished.connect(delegate.commitAndCloseEditor)
        return editor
    return build_single_list_editor

def build_multi_list_editor_init(get_list):
    def build_multi_list_editor(parent,delegate):
        editor = MultiListWidget(get_list(parent),parent)
        editor.editingFinished.connect(delegate.commitAndCloseEditor)
        return editor
    return build_multi_list_editor

def build_float_editor_init(bottom = -1e-6,top=1e-6,decimals = 6):
    def build_float_editor(parent,delegate):
        editor = qg.QLineEdit(parent)
        val = qg.QDoubleValidator(bottom,top,decimals, editor)
        editor.setValidator(val)
        return editor
    return build_float_editor
    
class Element(object):
    pass

class SingleItemList(Element):
    def __init__(self,name,get_list):
        self.name = name
        self.get_list = get_list
    def set_data(self,*args,**kwargs):
        return set_single_item_list(*args,**kwargs)
    def set_editor_data(self,*args,**kwargs):
        return set_editor_data_user(*args,**kwargs)
    def set_editor_rect(self,*args,**kwargs):
        return (expand_editor_rect_init(bottom = 100))(*args,**kwargs)
    def set_model_data(self,*args,**kwargs):
        return set_model_data_single_list(*args,**kwargs)
    def build_editor(self,*args,**kwargs):
        return (build_single_list_editor_init(self.get_list))(*args,**kwargs)
        
class MultiItemList(Element):
    def __init__(self,name,get_list):
        self.name = name
        self.get_list = get_list
    def set_data(self,*args,**kwargs):
        return set_multi_item_list(*args,**kwargs)
    def set_editor_data(self,*args,**kwargs):
        return set_editor_data_user(*args,**kwargs)
    def set_editor_rect(self,*args,**kwargs):
        return (expand_editor_rect_init(bottom = 100))(*args,**kwargs)
    def set_model_data(self,*args,**kwargs):
        return set_model_data_multi_list(*args,**kwargs)
    def build_editor(self,*args,**kwargs):
        return (build_multi_list_editor_init(self.get_list))(*args,**kwargs)

class FloatElement(Element):
    def __init__(self,name):
        self.name = name
    def set_data(self,*args,**kwargs):
        return (set_float_data_init())(*args,**kwargs)
    def set_editor_data(self,*args,**kwargs):
        return set_editor_data_plain(*args,**kwargs)
    def set_editor_rect(self,*args,**kwargs):
        return (expand_editor_rect_init())(*args,**kwargs)
    def set_model_data(self,*args,**kwargs):
        return set_model_data_plain(*args,**kwargs)
    def build_editor(self,*args,**kwargs):
        return (build_float_editor_init())(*args,**kwargs)

class JointDef(object):
    column_count = 7
    elements = []
    elements.append(SingleItemList('joint sketch',get_sketches))
    elements.append(SingleItemList('joint layer',get_layers))
    elements.append(MultiItemList('sublaminate layers',get_layers))
    elements.append(FloatElement('hinge width'))
    elements.append(FloatElement('stiffness'))
    elements.append(FloatElement('damping'))
    elements.append(FloatElement('preload'))
    
#    header_labels = ['joint sketch','joint layer','sublaminate layers','hinge width','stiffness','damping','preload_angle']
#    set_data_fun = {}
#    set_data_fun['joint sketch'] = set_single_item_list
#    set_data_fun['joint layer'] = set_single_item_list
#    set_data_fun['sublaminate layers'] = set_multi_item_list
#    set_data_fun['hinge width'] = set_float_data_init()
#    set_data_fun['stiffness'] = set_float_data_init()
#    set_data_fun['damping'] = set_float_data_init()
#    set_data_fun['preload_angle'] = set_float_data_init()
#
#    set_editor_data_fun = {}
#    set_editor_data_fun['joint sketch'] = set_editor_data_user
#    set_editor_data_fun['joint layer'] = set_editor_data_user
#    set_editor_data_fun['sublaminate layers'] = set_editor_data_user
#    set_editor_data_fun['hinge width'] = set_editor_data_plain
#    set_editor_data_fun['stiffness'] = set_editor_data_plain
#    set_editor_data_fun['damping'] = set_editor_data_plain
#    set_editor_data_fun['preload_angle'] = set_editor_data_plain
#
#    set_editor_rect_fun = {}
#    set_editor_rect_fun['joint sketch'] = expand_editor_rect_init(bottom = 100)
#    set_editor_rect_fun['joint layer'] = expand_editor_rect_init(bottom = 100)
#    set_editor_rect_fun['sublaminate layers'] = expand_editor_rect_init(bottom = 100)
#    set_editor_rect_fun['hinge width'] = expand_editor_rect_init()
#    set_editor_rect_fun['stiffness'] = expand_editor_rect_init()
#    set_editor_rect_fun['damping'] = expand_editor_rect_init()
#    set_editor_rect_fun['preload_angle'] = expand_editor_rect_init()
#
#    set_model_data_fun = {}
#    set_model_data_fun['joint sketch'] = set_model_data_single_list
#    set_model_data_fun['joint layer'] = set_model_data_single_list
#    set_model_data_fun['sublaminate layers'] = set_model_data_multi_list
#    set_model_data_fun['hinge width'] = set_model_data_plain
#    set_model_data_fun['stiffness'] = set_model_data_plain
#    set_model_data_fun['damping'] = set_model_data_plain
#    set_model_data_fun['preload_angle'] = set_model_data_plain
#
#    build_editor_fun = {}
#    build_editor_fun['joint sketch'] = build_single_list_editor_init(get_sketches)
#    build_editor_fun['joint layer'] = build_single_list_editor_init(get_layers)
#    build_editor_fun['sublaminate layers'] = build_multi_list_editor_init(get_layers)
#    build_editor_fun['hinge width'] = build_float_editor_init()
#    build_editor_fun['stiffness'] = build_float_editor_init()
#    build_editor_fun['damping'] = build_float_editor_init()
#    build_editor_fun['preload_angle'] = build_float_editor_init()


    def __init__(self,sketch,joint_layer,sublaminate_layers,width,stiffness,damping,preload_angle):
        self.sketch = sketch
        self.joint_layer = joint_layer
        self.sublaminate_layers = sublaminate_layers
        self.width = width
        self.stiffness = stiffness
        self.damping = damping
        self.preload_angle = preload_angle

    @classmethod
    def row_add(cls,*args):
        items = []
        for element,value in zip(cls.elements,args):
            items.append(element.set_data(value))                
        return items

    @classmethod
    def row_add_empty(cls):
        items = []
        for element in cls.elements:
            items.append(element.set_data(None))                
        return items
        
    @classmethod
    def create_editor(cls,parent,option,index,delegate):
        ii = index.column()
        element = cls.elements[ii]
        return element.build_editor(parent,delegate)

    @classmethod
    def update_editor_geometry(cls,editor, option, index):
        ii = index.column()
        element = cls.elements[ii]
        return element.set_editor_rect(editor,option)
        
    @classmethod
    def set_editor_data(cls,editor, index,delegate):
        ii = index.column()
        element = cls.elements[ii]
        return element.set_editor_data(index,editor)        

    @classmethod
    def set_model_data(cls,editor, model, index,delegate):
        ii = index.column()
        element = cls.elements[ii]
        return element.set_model_data(editor,model,index,delegate)  
    @classmethod
    def header_labels(cls):
        return [element.name for element in cls.elements]    
        
class MainWidget(qg.QDialog):
    def __init__(self,design,sketches,layers,operations,jointop=None):
        super(MainWidget,self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations
        
        self.operation_list = DraggableTreeWidget()
        self.operation_list.linklist(self.operations)

        self.fixed = DraggableTreeWidget()
        self.fixed.linklist(self.operations)
        
        self.table= Table(JointDef)

        button_add = qg.QPushButton('Add')
        button_remove = qg.QPushButton('Remove')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.pressed.connect(self.table.row_add_empty)
        button_remove.pressed.connect(self.table.row_remove)
        button_up.pressed.connect(self.table.row_shift_up)
        button_down.pressed.connect(self.table.row_shift_down)

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
                self.table.row_add(sketch,joint_layer,sublaminate_layers,item.width,item.stiffness,item.damping,item.preload_angle)
        else:
            self.table.row_add_empty()
            
    def acceptdata(self):
        from popupcad.manufacturing.joint_operation2 import JointDef
        jointdefs = []
        for ii in range(self.table.rowCount()):
            sketch = self.table.item(ii,0).data(qc.Qt.ItemDataRole.UserRole)
            joint_layer = self.table.item(ii,1).data(qc.Qt.ItemDataRole.UserRole)
            sublaminate_layers = self.table.item(ii,2).data(qc.Qt.ItemDataRole.UserRole)
            width = float(self.table.item(ii,3).data(qc.Qt.ItemDataRole.DisplayRole))
            stiffness = float(self.table.item(ii,4).data(qc.Qt.ItemDataRole.DisplayRole))
            damping = float(self.table.item(ii,5).data(qc.Qt.ItemDataRole.DisplayRole))
            preload_angle = float(self.table.item(ii,6).data(qc.Qt.ItemDataRole.DisplayRole))
            jointdefs.append(JointDef(sketch.id,joint_layer.id,[item.id for item in sublaminate_layers],width,stiffness,damping,preload_angle))
        operation_links = {}
        operation_links['parent'] = self.operation_list.currentRefs()
        operation_links['fixed'] = self.fixed.currentRefs()
        return operation_links,jointdefs
        

class SubOperation(Operation2):
    resolution = 2
    name = 'Sub-Operation'
    def copy(self):
        new = type(self)(self.operation_links,self.joint_defs)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SubOperation,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,operation_links,joint_defs):  
        self.operation_links = operation_links
        self.joint_defs = joint_defs
        self.clear_output()

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        dialog = MainWidget(design,design.sketches.values(),design.return_layer_definition().layers,design.prioroperations(self),self)
        return dialog

    def operate(self,design):
        layerdef = design.return_layer_definition()
        return Laminate(layerdef)
