# -*- coding: utf-8 -*-
"""
Created on Mon May 11 19:20:36 2015

@author: danaukes
"""
import PySide.QtGui as qg
import PySide.QtCore as qc

class DataClass(object):
    column_count = 1
    header_labels = ['string data']
    @staticmethod
    def row_add(stringdata = None):
        items = []
        item = qg.QTableWidgetItem()
        if stringdata!=None:
            item.setData(qc.Qt.ItemDataRole.DisplayRole,stringdata)
        else:
            item.setData(qc.Qt.ItemDataRole.DisplayRole,'stringdata')
        items.append(item)

    @staticmethod
    def create_editor(parent,option,index,delegate):
        return super(Delegate,delegate).createEditor(parent, option, index)

    @staticmethod
    def update_editor_geometry(editor, option, index):
        editor.setGeometry(option.rect)
        
    @staticmethod
    def set_editor_data(editor, index,delegate):
        return super(Delegate,delegate).setEditorData(editor, index)

    @staticmethod
    def set_model_data(editor, model, index,delegate):
        return super(Delegate,delegate).setModelData(editor, model, index)
            

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
        self.setColumnCount(data_class.column_count)
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
