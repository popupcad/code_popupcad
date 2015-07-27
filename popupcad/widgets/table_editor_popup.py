# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 13:17:56 2015

@author: danb0b
"""

import PySide.QtGui as qg
import PySide.QtCore as qc
from popupcad.widgets.table_common import TableControl,Table
import popupcad
from popupcad.widgets.dragndroptree import DraggableTreeWidget

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

class Row(object):
    def __init__(self):
        self.elements = []

    def row_add(self, *args):
        list_widget_items=[]
        for item in args:
            lwi = UneditableItem()
            lwi.setData(qc.Qt.ItemDataRole.DisplayRole,str(item))
            lwi.setData(qc.Qt.ItemDataRole.UserRole,item)
            list_widget_items.append(lwi)
        return list_widget_items

    def row_add_empty(self):
        items = []

        for element in self.elements:
            items.append(element.ini)
        return self.row_add(*items)
        
    def cell_clicked(self,row,column,tablewidget):
        index = tablewidget.model().index(row,column)
        item = tablewidget.itemFromIndex(index)

        ini = item.data(qc.Qt.ItemDataRole.UserRole)

        d = self.elements[column].build_editor()
        d.set_data(ini)

        result = d.exec_()
        if result:
            results = d.results()
            item.setData(qc.Qt.ItemDataRole.DisplayRole,str(results))
            item.setData(qc.Qt.ItemDataRole.UserRole,results)

    @property
    def header_labels(self):
        return [element.name for element in self.elements]
    @property
    def column_count(self):
        return len(self.elements)

class TextDialog(qg.QDialog):
    def __init__(self):
        super(TextDialog,self).__init__()
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

    def set_data(self,val):   
        self.text_edit.setText(val)
        
    def results(self):
        return self.text_edit.text()

class FloatDialog(TextDialog):
    bottom = -1e6
    top = 1e6
    decimals = popupcad.geometry_round_value
    
    def __init__(self, *args,**kwargs):
        super(FloatDialog, self).__init__(*args, **kwargs)
        validator = qg.QDoubleValidator(self.bottom, self.top, self.decimals, self.text_edit)
        self.text_edit.setValidator(validator)

    def set_data(self,val):   
        self.text_edit.setText(str(val))
        
    def results(self):
        return float(self.text_edit.text())

class SingleListDialog(qg.QDialog):
    def __init__(self, list_in, *args, **kwargs):
        super(SingleListDialog, self).__init__(*args, **kwargs)
        self.listwidget = qg.QListWidget()

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')
        
        sub_layout1 = qg.QHBoxLayout()
        sub_layout1.addWidget(button_ok)
        sub_layout1.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addLayout(sub_layout1)

        self.setLayout(layout)
        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)

        for item in list_in:
            lwi = qg.QListWidgetItem()
            lwi.setData(qc.Qt.ItemDataRole.DisplayRole,str(item))
            lwi.setData(qc.Qt.ItemDataRole.UserRole,item)
            self.listwidget.addItem(lwi)

    def set_data(self,ini):
        for ii in range(self.listwidget.count()):
            lwi = self.listwidget.item(ii)
            lwi.setSelected(False)
            data = lwi.data(qc.Qt.ItemDataRole.UserRole)
            if data in ini:
                lwi.setSelected(True)
                
    def results(self):
        results = []
        for ii in range(self.listwidget.count()):
            lwi = self.listwidget.item(ii)
            if lwi.isSelected():
                data = lwi.data(qc.Qt.ItemDataRole.UserRole)
                results.append(data)
        return results

class SingleListDialog_old(SingleListDialog):
    def set_data(self,ini):
        for ii in range(self.listwidget.count()):
            lwi = self.listwidget.item(ii)
            lwi.setSelected(False)
            data = lwi.data(qc.Qt.ItemDataRole.UserRole)
            if data == ini:
                lwi.setSelected(True)
                
    def results(self):
        for ii in range(self.listwidget.count()):
            lwi = self.listwidget.item(ii)
            if lwi.isSelected():
                data = lwi.data(qc.Qt.ItemDataRole.UserRole)
                return data
        return None
        
class MultiListDialog(SingleListDialog):
    def __init__(self, *args,**kwargs):
        super(MultiListDialog, self).__init__(*args, **kwargs)
        self.listwidget.setSelectionMode(self.listwidget.SelectionMode.MultiSelection)

class DraggableTreeDialog(qg.QDialog):
    def __init__(self, list_in, *args, **kwargs):
        super(DraggableTreeDialog, self).__init__(*args, **kwargs)
        self.listwidget = DraggableTreeWidget()

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')
        
        sub_layout1 = qg.QHBoxLayout()
        sub_layout1.addWidget(button_ok)
        sub_layout1.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addLayout(sub_layout1)

        self.setLayout(layout)
        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)

        self.listwidget.linklist(list_in)

    def set_data(self,ini):
        self.listwidget.selectIndeces(ini)

    def results(self):
        return self.listwidget.currentIndeces2()
        
        

class TextElement(object):
    def __init__(self,name,ini=''):
        self.name = name
        self.ini = ini

    def build_editor(self):
        dialog = TextDialog()
        return dialog
        
class FloatElement(object):
    def __init__(self,name,ini=0.0):
        self.name = name
        self.ini = ini

    def build_editor(self):
        dialog = FloatDialog()
        return dialog

class SingleItemListElement_old(object):
    def __init__(self,name,list_getter,ini=None):
        self.name = name
        self.my_list = list_getter
        self.ini = ini

    def build_editor(self):
        dialog = SingleListDialog_old(self.my_list)
        return dialog

    @property
    def my_list(self):
        return self._get_list()

    @my_list.setter
    def my_list(self,val):
        self._get_list = val

class SingleItemListElement(object):
    def __init__(self,name,list_getter,ini=None):
        self.name = name
        self.my_list = list_getter
        if ini is not None:
            self.ini = ini
        else:
            self.ini = []

    def build_editor(self):
        dialog = SingleListDialog(self.my_list)
        return dialog

    @property
    def my_list(self):
        return self._get_list()

    @my_list.setter
    def my_list(self,val):
        self._get_list = val        
        
class MultiItemListElement(SingleItemListElement):
    def build_editor(self):
        dialog = MultiListDialog(self.my_list)
        return dialog

class DraggableTreeElement(SingleItemListElement):
    def build_editor(self):
        dialog = DraggableTreeDialog(self.my_list)
        return dialog

if __name__ =='__main__':
    import sys

    class JointRow(Row):
        def __init__(self, get_sketches, get_layers):
            elements = []
            elements.append(SingleItemListElement('joint sketch', get_sketches))
            elements.append(SingleItemListElement('joint layer', get_layers))
            elements.append(MultiItemListElement('sublaminate layers', get_layers))
            elements.append(FloatElement('hinge width'))
            elements.append(FloatElement('stiffness'))
            elements.append(FloatElement('damping'))
            elements.append(FloatElement('preload'))
            self.elements = elements

    app = qg.QApplication(sys.argv)
#    dialog = Dialog1()
#    result = dialog.exec_()
#    print(result)    
# 
    table = Table(JointRow(lambda:range(5),lambda:range(10)),Delegate)
    table.row_add_empty()
    table.row_add([1], [2], [5,6,7], 5.0, 0.0, 0.3, 0.0)
    widget = TableControl(table)
    widget.show()
    
    sys.exit(app.exec_())