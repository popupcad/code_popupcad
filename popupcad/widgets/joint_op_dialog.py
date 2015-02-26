# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 15:14:32 2015

@author: danaukes
"""

from popupcad.widgets.dragndroptree import DraggableTreeWidget
#import sys
import PySide.QtGui as qg
import PySide.QtCore as qc

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

class ListWidget(qg.QListWidget):
    editingFinished = qc.Signal()
    def __init__(self,list1,*args,**kwargs):
        super(ListWidget,self).__init__(*args,**kwargs)
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

class ListWidget2(qg.QListWidget):
    editingFinished = qc.Signal()
    def __init__(self,list1,*args,**kwargs):
        super(ListWidget2,self).__init__(*args,**kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list1]
        self.setSelectionMode(self.SelectionMode.MultiSelection)
    def setData(self,data):
        self.clearSelection()
        for ii in range(self.model().rowCount()):
            item = self.item(ii)
            if item.customdata in data:
                item.setSelected(True)
            
class CellWidget(qg.QWidget):
    def __init__(self,*args,**kwargs):
        super(CellWidget,self).__init__(*args,**kwargs)
        layout = qg.QHBoxLayout()
        layout.addWidget(qg.QLabel('asdfjas;dlfkj'))
        self.setLayout(layout)

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
        
        self.table= Table()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(['joint sketch','joint layer','sublaminate layers','hinge width'])
        self.table.resizeColumnsToContents()
        self.table.reset_min_width()
        self.table.setItemDelegate(Delegate())
#        self.table.horizontalHeader().setStretchLastSection(True)        
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

#        self.value = qg.QLineEdit()
#        sublayout = qg.QHBoxLayout()
#        sublayout.addWidget(qg.QLabel('Value'))
#        sublayout.addWidget(self.value)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.pressed.connect(self.accept)        
        button_cancel.pressed.connect(self.reject)        

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)

#        item = Item('asdfasdf')
#        self.table.
#        self.list_widget.addItem(item)
        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Device'))
        layout.addWidget(self.operation_list)
        layout.addWidget(self.table)
        layout.addLayout(sublayout1)
#        layout.addLayout(sublayout)
        layout.addLayout(sublayout2)
        self.setLayout(layout)
#        a=qg.QTableWidgetItem('asdf')
#        self.table.setItem(1,1,a)
        
#        row = 0
#        column = 0
#        newItem = qg.QTableWidgetItem(str("%s" % ((row+1)*(column+1))))
#        self.table.setItem(row, column, newItem)
#        self.resize()
#        lw = ListWidget()
#        self.table.setCellWidget(1,2,qg.QLineEdit())
#        self.table.setCellWidget(1,1,CellWidget())
        if jointop!=None:
            op_ref,output_ii = jointop.operation_links['parent'][0]
            op_ii = design.operation_index(op_ref)
            
            self.operation_list.selectIndeces([(op_ii,output_ii)])
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
        return operation_links,jointdefs
        

class Delegate(qg.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(Delegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = ListWidget(parent.parent().parent().sketches,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == 1:
            editor = ListWidget(parent.parent().parent().layers,parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == 2:
            editor = ListWidget2(parent.parent().parent().layers,parent)
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
#        self.closeEditor.emit(editor)
        self.closeEditor.emit(editor, qg.QAbstractItemDelegate.NoHint)        
    
#    def sizeHint(self,option, index):
#        if index.column() == 0:
#            size = qc.QSize(800,400)
#            return size
##            return 400,400
#        else:
#            return super(Delegate, self).sizeHint(option, index)
        
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
    layers1 = [Dummy(),Dummy(),Dummy(),Dummy(),Dummy()]
    sketches1 = [Dummy(),Dummy(),Dummy(),Dummy(),Dummy()]
    widget = MainWidget(sketches1,layers1,[],Dummy)
    widget.show()
    sys.exit(app.exec_())

#    tableWidget.setItem(r, 0, QTableWidgetItem(data[r][0]))
#    tableWidget.setItem(r, 1, QTableWidgetItem(data[r][1]))
##    tableWidget.setItem(r, 2, QTableWidgetItem(data[r][2]))
#

    
#    item.setData(0, StarRating(data[r][3]).starCount)
#    tableWidget.setItem(r, 3, item)
        