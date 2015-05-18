# -*- coding: utf-8 -*-
"""
Created on Mon May 11 19:20:36 2015

@author: danaukes
"""
import PySide.QtGui as qg
import PySide.QtCore as qc

class ListWidgetItem(qg.QListWidgetItem):
    def __init__(self,data):
        self.customdata = data
        super(ListWidgetItem,self).__init__(str(data))

class SingleListWidget(qg.QListWidget):
    editingFinished = qc.Signal()
    def __init__(self,list1,*args,**kwargs):
        super(SingleListWidget,self).__init__(*args,**kwargs)
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
    def __init__(self,data_class):
        super(Table,self).__init__()
        self.setRowCount(0)
        self.setColumnCount(data_class.column_count())
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setHorizontalHeaderLabels(data_class.header_labels())
        self.resizeColumnsToContents()
        self.reset_min_width()
        self.setItemDelegate(Delegate(data_class))
        self.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.data_class = data_class
        
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
    def row_add(self,*args,**kwargs):
        ii = self.rowCount()
        self.setRowCount(ii+1)
        items = self.data_class.row_add(*args,**kwargs)
        for jj,item in enumerate(items):
            self.setItem(ii,jj,item)
        self.reset_min_width()
    def row_add_empty(self,*args,**kwargs):
        ii = self.rowCount()
        self.setRowCount(ii+1)
        items = self.data_class.row_add_empty(*args,**kwargs)
        for jj,item in enumerate(items):
            self.setItem(ii,jj,item)
        self.reset_min_width()
    def row_remove(self):
        ii = self.currentRow()
        kk = self.currentColumn()
        self.removeRow(ii)
        self.setCurrentCell(ii,kk)
    def row_shift_up(self):
        ii = self.currentRow()
        kk = self.currentColumn()
        if ii>0:
            cols = self.columnCount()
            items_below = [self.takeItem(ii,jj) for jj in range(cols)]
            items_above = [self.takeItem(ii-1,jj) for jj in range(cols)]
            [self.setItem(ii,jj,item) for item,jj in zip(items_above,range(cols))]
            [self.setItem(ii-1,jj,item) for item,jj in zip(items_below,range(cols))]
        self.setCurrentCell(ii-1,kk)
    def row_shift_down(self):
        ii = self.currentRow()
        kk = self.currentColumn()
        if ii<self.rowCount()-1:
            cols = self.columnCount()
            items_below = [self.takeItem(ii+1,jj) for jj in range(cols)]
            items_above = [self.takeItem(ii,jj) for jj in range(cols)]
            [self.setItem(ii+1,jj,item) for item,jj in zip(items_above,range(cols))]
            [self.setItem(ii,jj,item) for item,jj in zip(items_below,range(cols))]
        self.setCurrentCell(ii+1,kk)
    def reset(self):
        for ii in range(self.rowCount()):
            self.removeRow(0)
    def export_data(self):
        return [[self.item(ii,jj).data(qc.Qt.ItemDataRole.UserRole) for jj in range(self.data_class.column_count())] for ii in range(self.rowCount()) ]

class Delegate(qg.QStyledItemDelegate):
    def __init__(self, data_class,parent=None):
        super(Delegate, self).__init__(parent)
        self.data_class = data_class
        
    def createEditor(self, parent, option, index):
        return self.data_class.create_editor(parent,option,index,self)
            
    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, qg.QAbstractItemDelegate.NoHint)        
    
    def updateEditorGeometry(self, editor, option, index):
        return self.data_class.update_editor_geometry(editor,option,index)        
        
    def setEditorData(self, editor, index):
        return self.data_class.set_editor_data(editor,index,self)
        
    def setModelData(self, editor, model, index):
        return self.data_class.set_model_data(editor,model,index,self)

class Row(object):
    def __init__(self):
        self.elements = []

    def column_count(self):
        return len(self.elements)
        
    def row_add(self,*args):
        items = []
        for element,value in zip(self.elements,args):
            items.append(element.set_data(value))                
        return items

    def row_add_empty(self):
        items = []
        for element in self.elements:
            items.append(element.set_data(None))                
        return items
        
    def create_editor(self,parent,option,index,delegate):
        ii = index.column()
        element = self.elements[ii]
        return element.build_editor(parent,delegate)

    def update_editor_geometry(self,editor, option, index):
        ii = index.column()
        element = self.elements[ii]
        return element.set_editor_rect(editor,option)
        
    def set_editor_data(self,editor, index,delegate):
        ii = index.column()
        element = self.elements[ii]
        return element.set_editor_data(index,editor)        

    def set_model_data(self,editor, model, index,delegate):
        ii = index.column()
        element = self.elements[ii]
        return element.set_model_data(editor,model,index,delegate)  
    def header_labels(self):
        return [element.name for element in self.elements]    

class Element(object):
    def __init__(self):
        self.expand_bottom = 0
        self.expand_top = 0
        self.expand_left = 0
        self.expand_right = 0

    def set_editor_rect(self,editor,option):
        rect = option.rect
        rect.setTop(rect.top()-self.expand_top)
        rect.setBottom(rect.bottom()+self.expand_bottom)
        rect.setLeft(rect.left()-self.expand_left)
        rect.setRight(rect.right()+self.expand_right)
        editor.setGeometry(rect)
        
    def set_model_data(self,editor,model,index,delegate):
        super(Delegate,delegate).setModelData(editor,model,index)

    def set_data(self,variable):
        item = qg.QTableWidgetItem()
        if variable!=None:
            item.setData(qc.Qt.ItemDataRole.UserRole,variable)
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str(variable))
        else:
            item.setData(qc.Qt.ItemDataRole.UserRole,self.ini)
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str(self.ini))
        return item
        

class SingleItemListElement(Element):
    def __init__(self,name,get_list,ini = None):
        super(SingleItemListElement,self).__init__()
        self.name = name
        self.get_list = get_list
        self.expand_bottom = 100
        self.ini = ini
    def set_editor_data(self,index,editor):
        d = index.data(qc.Qt.ItemDataRole.UserRole)
        editor.setData(d)
    def set_model_data(self,editor,model,index,delegate):
        try:
            value = editor.selectedItems()[0].customdata
            model.setData(index, str(value), qc.Qt.ItemDataRole.EditRole)        
            model.setData(index, value, qc.Qt.ItemDataRole.UserRole)        
        except IndexError:
            pass
    def build_editor(self,parent,delegate):
            editor = SingleListWidget(self.get_list(),parent)
            editor.editingFinished.connect(delegate.commitAndCloseEditor)
            return editor
        
class MultiItemListElement(Element):
    def __init__(self,name,get_list,ini = None):
        super(MultiItemListElement,self).__init__()
        self.name = name
        self.get_list = get_list
        self.expand_bottom = 100
        if ini != None:
            self.ini = ini
        else:
            self.ini = []
    def set_editor_data(self,index,editor):
        d = index.data(qc.Qt.ItemDataRole.UserRole)
        editor.setData(d)
    def set_model_data(self,editor,model,index,delegate):
        values = [item.customdata for item in editor.selectedItems()]
        model.setData(index, str(values), qc.Qt.ItemDataRole.EditRole)        
        model.setData(index, values, qc.Qt.ItemDataRole.UserRole)        
    def build_editor(self,parent,delegate):
        editor = MultiListWidget(self.get_list(),parent)
        editor.editingFinished.connect(delegate.commitAndCloseEditor)
        return editor

class FloatElement(Element):
    def __init__(self,name,ini = 0.,bottom = -1e-6,top=1e-6,decimals = 6):
        super(FloatElement,self).__init__()
        self.name = name
        self.ini = ini
        self.bottom = bottom
        self.top = top
        self.decimals = decimals
    def set_editor_data(self,index,editor):
        d = index.data(qc.Qt.ItemDataRole.UserRole)
        editor.setText(str(d))
    def set_model_data(self,editor,model,index,delegate):
        value = editor.text()
        model.setData(index, value, qc.Qt.ItemDataRole.EditRole)        
        model.setData(index, float(value), qc.Qt.ItemDataRole.UserRole)        
    def build_editor(self,parent,delegate):
        editor = qg.QLineEdit(parent)
        val = qg.QDoubleValidator(self.bottom,self.top,self.decimals,editor)
        editor.setValidator(val)
        return editor
        
class TableControl(qg.QWidget):
    def __init__(self,table,*args,**kwargs):
        super(TableControl,self).__init__(*args,**kwargs)
        main_layout = qg.QHBoxLayout()

        button_add = qg.QPushButton('+')
        button_remove = qg.QPushButton('-')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.pressed.connect(table.row_add_empty)
        button_remove.pressed.connect(table.row_remove)
        button_up.pressed.connect(table.row_shift_up)
        button_down.pressed.connect(table.row_shift_down)

        sublayout1 = qg.QVBoxLayout()
        sublayout1.addWidget(button_add)
        sublayout1.addWidget(button_remove)
        sublayout1.addStretch()
        sublayout1.addWidget(button_up)
        sublayout1.addWidget(button_down)

        main_layout.addWidget(table)
        main_layout.addLayout(sublayout1)
        self.setLayout(main_layout)
        
        