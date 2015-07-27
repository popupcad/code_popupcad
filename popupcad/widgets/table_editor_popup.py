# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 13:17:56 2015

@author: danb0b
"""

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.widgets.table_common import TableControl,Table

class UneditableItem(qg.QTableWidgetItem):
    def __init__(self,*args,**kwargs):
        super(UneditableItem,self).__init__(*args,**kwargs)
        
        flags = self.flags()
        flags = qc.Qt.ItemFlag.ItemIsEditable ^ flags
        self.setFlags(flags)
#        self.setFlags(qc.Qt.ItemFlag.NoItemFlags & qc.Qt.ItemFlag.ItemIsSelectable & qc.Qt.ItemFlag.ItemIsEnabled)
        
class Delegate(qg.QStyledItemDelegate):

    def __init__(self, data_class, parent=None):
        super(Delegate, self).__init__(parent)
        self.data_class = data_class

#    def createEditor(self, parent, option, index):
#        return self.data_class.create_editor(parent, option, index, self)
#
#    def commitAndCloseEditor(self):
#        editor = self.sender()
#        self.commitData.emit(editor)
#        self.closeEditor.emit(editor, qg.QAbstractItemDelegate.NoHint)
#
#    def updateEditorGeometry(self, editor, option, index):
#        return self.data_class.update_editor_geometry(editor, option, index)
#
#    def setEditorData(self, editor, index):
#        return self.data_class.set_editor_data(editor, index, self)
#
#    def setModelData(self, editor, model, index):
#        return self.data_class.set_model_data(editor, model, index, self)
                
class Dialog1(qg.QDialog):
    def __init__(self):
        super(Dialog1,self).__init__()
        self.text_edit = qg.QLineEdit()
        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')
        
        sub_layout1 = qg.QHBoxLayout()
        sub_layout1.addWidget(button_ok)
        sub_layout1.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addLayout(sub_layout1)

        self.setLayout(layout)
        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
        
    def results(self):
        return self.text_edit.text()

class DataRow(object):
    header_labels = ['a','b']
    column_count = len(header_labels)

    def __init__(self):
        self.elements = []

    def row_add(self, *args):
#        items = []
#        for element, value in zip(self.elements, args):
#            items.append(element.set_data(value))
#        return items
        items = ['','']
        items = [UneditableItem(item) for item in items]
        return items

    def row_add_empty(self):
#        items = []
#        for element in self.elements:
#            items.append(element.set_data(None))
#        return items
        items = ['','']
        items = [UneditableItem(item) for item in items]
        return items
        
    def cell_clicked(self,row,column,tablewidget):
        d = Dialog1()
        result = d.exec_()
        if result:
            results = d.results()
            index = tablewidget.model().index(row,column)
            item = tablewidget.itemFromIndex(index)
            item.setData(qc.Qt.ItemDataRole.DisplayRole,results)
    

if __name__ =='__main__':
    import sys
    app = qg.QApplication(sys.argv)
#    dialog = Dialog1()
#    result = dialog.exec_()
#    print(result)    
# 
    table = Table(DataRow(),Delegate)
    table.row_add_empty()
    widget = TableControl(table)
    widget.show()
    
    sys.exit(app.exec_())