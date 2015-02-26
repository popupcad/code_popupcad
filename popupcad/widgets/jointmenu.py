# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 15:14:32 2015

@author: danaukes
"""

import sys
#from math import (cos, sin, pi)
#from PySide.QtGui import (QPainter, QPolygonF)
#from PySide.QtCore import (QPointF, QSize, Qt)
import PySide.QtGui as qg
import PySide.QtCore as qc
#from PySide.QtGui import (QItemDelegate, QStyledItemDelegate, QStyle)
#from PySide.QtGui import (QApplication, QTableWidget, QTableWidgetItem,QAbstractItemView)
#from PySide.QtGui import (QWidget, QPainter)
from PySide.QtCore import Signal

PAINTING_SCALE_FACTOR = 20

class Item(qg.QTableWidgetItem):
    pass


class Dummy(object):
    ii = 0
    def __init__(self):
        self.name = str(Dummy.ii)
        Dummy.ii+=1       
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)

class ListWidgetItem(qg.QListWidgetItem):
    def __init__(self,data):
        self.customdata = data
        super(ListWidgetItem,self).__init__(str(data))


layers = [Dummy(),Dummy(),Dummy(),Dummy(),Dummy()]

class ListWidget(qg.QListWidget):
    editingFinished = Signal()
    def __init__(self,list,*args,**kwargs):
        super(ListWidget,self).__init__(*args,**kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list]
        self.itemClicked.connect(self.fire_signal)
    def fire_signal(self):
        self.editingFinished.emit()

class ListWidget2(qg.QListWidget):
    editingFinished = Signal()
    def __init__(self,list,*args,**kwargs):
        super(ListWidget2,self).__init__(*args,**kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list]
        self.setSelectionMode(self.SelectionMode.MultiSelection)
    def selectRows(self,indeces):
        self.clearSelection()
        [self.item(ii).setSelected(True) for ii in indeces]


class CellWidget(qg.QWidget):
    def __init__(self,*args,**kwargs):
        super(CellWidget,self).__init__(*args,**kwargs)
        layout = qg.QHBoxLayout()
        layout.addWidget(qg.QLabel('asdfjas;dlfkj'))
        self.setLayout(layout)
        
class MainWidget(qg.QWidget):
    def __init__(self,*args,**kwargs):
        super(MainWidget,self).__init__(*args,**kwargs)

        self.table= qg.QTableWidget()
        self.table.setRowCount(1)
        self.table.setColumnCount(3)
        
        self.value = qg.QLineEdit()
        sublayout = qg.QHBoxLayout()
        sublayout.addWidget(qg.QLabel('Value'))
        sublayout.addWidget(self.value)
#        item = Item('asdfasdf')
#        self.table.
#        self.list_widget.addItem(item)
        layout = qg.QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(sublayout)
        self.setLayout(layout)
#        a=qg.QTableWidgetItem('asdf')
#        self.table.setItem(1,1,a)
        
#        row = 0
#        column = 0
#        newItem = qg.QTableWidgetItem(str("%s" % ((row+1)*(column+1))))
#        self.table.setItem(row, column, newItem)
        self.table.setHorizontalHeaderLabels(['joint sketch','joint layer','sublaminate layers'])
        self.table.resizeColumnsToContents()
        self.table.setItemDelegate(Delegate())
#        lw = ListWidget()
#        self.table.setCellWidget(1,2,qg.QLineEdit())
#        self.table.setCellWidget(1,1,CellWidget())

class Delegate(qg.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(Delegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        if index.column() == 1:
            editor = ListWidget(layers,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == 2:
            editor = ListWidget2(layers,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        else:
            return super(Delegate,self).createEditor(parent, option, index)
            
    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
#        self.closeEditor.emit(editor)
    
#    def sizeHint(self,option, index):
#        if index.column() == 0:
#            size = qc.QSize(800,400)
#            return size
##            return 400,400
#        else:
#            return super(Delegate, self).sizeHint(option, index)
        
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        
    def setEditorData(self, editor, index):
        if index.column() == 1:
            d = index.data(qc.Qt.ItemDataRole.UserRole)
            ii = layers.index(d)
            print(d)
            editor.setCurrentRow(ii)
        if index.column() == 2:
            d = index.data(qc.Qt.ItemDataRole.UserRole)
            iis = [layers.index(item) for item in d]
#            ii = layers.index(d)
            print(iis)
            editor.selectRows(iis)
        else:
            return super(Delegate,self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 1:
            value = editor.selectedItems()[0].customdata
            model.setData(index, str(value), qc.Qt.ItemDataRole.EditRole)        
            model.setData(index, value, qc.Qt.ItemDataRole.UserRole)        
        elif index.column() == 2:
            values = [item.customdata for item in editor.selectedItems()]
            model.setData(index, str(values), qc.Qt.ItemDataRole.EditRole)        
            model.setData(index, values, qc.Qt.ItemDataRole.UserRole)        
        else:
            return super(Delegate,self).setModelData(editor, model, index)
            
    def paint(self,painter, option, index):
        super(Delegate,self).paint(painter, option, index)
#        if index.column() == 0:
            
#            cell = CellWidget(None)
#            cell.paintEvent()
#            rect = cell.size
#            option.rect
##            progressBarOption = QStyleOptionProgressBar()
#            progressBarOption.rect = option.rect
#            progressBarOption.minimum = 0
#            progressBarOption.maximum = 100
#            progressBarOption.progress = progress
#            progressBarOption.text = QString::number(progress) + "%"
#            progressBarOption.textVisible = True
#            qg.QStyle.
#            qg.QApplication.style().drawControl(QStyle.CE_ProgressBar, CellWidget(), painter)
            
if __name__=='__main__':
    import sys
    app = qg.QApplication(sys.argv)
    widget = MainWidget()
#    widget = ListWidget(layers)
    widget.show()
#    sys.exit(app.exec_())

#    tableWidget.setItem(r, 0, QTableWidgetItem(data[r][0]))
#    tableWidget.setItem(r, 1, QTableWidgetItem(data[r][1]))
##    tableWidget.setItem(r, 2, QTableWidgetItem(data[r][2]))
#
    item = qg.QTableWidgetItem('test')
#    item.setData(qc.Qt.ItemDataRole.UserRole,layers[0])
#    item.setData(qc.Qt.ItemDataRole.DisplayRole,str(layers[0]))
    widget.table.setItem(0,0,item)
    
    item = qg.QTableWidgetItem()
    item.setData(qc.Qt.ItemDataRole.UserRole,layers[0])
    item.setData(qc.Qt.ItemDataRole.DisplayRole,str(layers[0]))
    widget.table.setItem(0,1,item)

    item = qg.QTableWidgetItem()
    item.setData(qc.Qt.ItemDataRole.UserRole,[layers[0]])
    item.setData(qc.Qt.ItemDataRole.DisplayRole,str([layers[0]]))
    widget.table.setItem(0,2,item)
    
#    item.setData(0, StarRating(data[r][3]).starCount)
#    tableWidget.setItem(r, 3, item)
        