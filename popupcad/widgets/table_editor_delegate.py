# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.widgets.table_common import TableControl,Table,Delegate
import popupcad

from popupcad.filetypes.validators import StrictDoubleValidator

class ListWidgetItem(qg.QListWidgetItem):

    def __init__(self, data):
        self.customdata = data
        super(ListWidgetItem, self).__init__(str(data))


class SingleListWidget(qg.QListWidget):
    editingFinished = qc.Signal()

    def __init__(self, list1, *args, **kwargs):
        super(SingleListWidget, self).__init__(*args, **kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list1]
        self.itemClicked.connect(self.fire_signal)

    def fire_signal(self):
        self.editingFinished.emit()

    def setData(self, data):
        self.clearSelection()
        for ii in range(self.model().rowCount()):
            item = self.item(ii)
            if item.customdata == data:
                item.setSelected(True)


class MultiListWidget(qg.QListWidget):
    editingFinished = qc.Signal()

    def __init__(self, list1, *args, **kwargs):
        super(MultiListWidget, self).__init__(*args, **kwargs)
        [self.addItem(ListWidgetItem(item)) for item in list1]
        self.setSelectionMode(self.SelectionMode.MultiSelection)

    def setData(self, data):
        self.clearSelection()
        for ii in range(self.model().rowCount()):
            item = self.item(ii)
            if item.customdata in data:
                item.setSelected(True)

class Row(object):

    def __init__(self):
        self.elements = []

    @property
    def column_count(self):
        return len(self.elements)

    def row_add(self, *args):
        items = []
        for element, value in zip(self.elements, args):
            items.append(element.set_data(value))
        return items

    def row_add_empty(self):
        items = []
        for element in self.elements:
            items.append(element.set_data(None))
        return items

    def create_editor(self, parent, option, index, delegate):
        ii = index.column()
        element = self.elements[ii]
        return element.build_editor(parent, delegate)

    def update_editor_geometry(self, editor, option, index):
        ii = index.column()
        element = self.elements[ii]
        return element.set_editor_rect(editor, option)

    def set_editor_data(self, editor, index, delegate):
        ii = index.column()
        element = self.elements[ii]
        return element.set_editor_data(index, editor)

    def set_model_data(self, editor, model, index, delegate):
        ii = index.column()
        element = self.elements[ii]
        return element.set_model_data(editor, model, index, delegate)

    @property
    def header_labels(self):
        return [element.name for element in self.elements]

    def cell_clicked(self,*args,**kwargs):
        pass


class Element(object):

    def __init__(self):
        self.expand_bottom = 0
        self.expand_top = 0
        self.expand_left = 0
        self.expand_right = 0

    def set_editor_rect(self, editor, option):
        rect = option.rect
        rect.setTop(rect.top() - self.expand_top)
        rect.setBottom(rect.bottom() + self.expand_bottom)
        rect.setLeft(rect.left() - self.expand_left)
        rect.setRight(rect.right() + self.expand_right)
        editor.setGeometry(rect)

    def set_model_data(self, editor, model, index, delegate):
        super(Delegate, delegate).setModelData(editor, model, index)

    def set_data(self, variable):
        item = qg.QTableWidgetItem()
        if variable is not None:
            item.setData(qc.Qt.UserRole, variable)
            item.setData(qc.Qt.DisplayRole, str(variable))
        else:
            item.setData(qc.Qt.UserRole, self.ini)
            item.setData(qc.Qt.DisplayRole, str(self.ini))
        return item


class SingleItemListElement(Element):

    def __init__(self, name, get_list, ini=None):
        super(SingleItemListElement, self).__init__()
        self.name = name
        self.get_list = get_list
        self.expand_bottom = 100
        self.ini = ini

    def set_editor_data(self, index, editor):
        d = index.data(qc.Qt.UserRole)
        editor.setData(d)

    def set_model_data(self, editor, model, index, delegate):
        try:
            value = editor.selectedItems()[0].customdata
            model.setData(index, str(value), qc.Qt.EditRole)
            model.setData(index, value, qc.Qt.UserRole)
        except IndexError:
            pass

    def build_editor(self, parent, delegate):
        editor = SingleListWidget(self.get_list(), parent)
        editor.editingFinished.connect(delegate.commitAndCloseEditor)
        return editor


class MultiItemListElement(Element):

    def __init__(self, name, get_list, ini=None):
        super(MultiItemListElement, self).__init__()
        self.name = name
        self.get_list = get_list
        self.expand_bottom = 100
        if ini is not None:
            self.ini = ini
        else:
            self.ini = []

    def set_editor_data(self, index, editor):
        d = index.data(qc.Qt.UserRole)
        editor.setData(d)

    def set_model_data(self, editor, model, index, delegate):
        values = [item.customdata for item in editor.selectedItems()]
        model.setData(index, str(values), qc.Qt.EditRole)
        model.setData(index, values, qc.Qt.UserRole)

    def build_editor(self, parent, delegate):
        editor = MultiListWidget(self.get_list(), parent)
        editor.editingFinished.connect(delegate.commitAndCloseEditor)
        return editor


class DraggableTreeElement(Element):

    def __init__(self, name, get_list, ini=None):
        super(DraggableTreeElement, self).__init__()
        self.name = name
        self.get_list = get_list
        self.expand_bottom = 100
        if ini is not None:
            self.ini = ini
        else:
            self.ini = []

    def set_editor_data(self, index, editor):
        d = index.data(qc.Qt.UserRole)
        editor.selectIndeces(d)

    def set_model_data(self, editor, model, index, delegate):
        try:
            value = editor.currentIndeces2()
            model.setData(index, str(value), qc.Qt.EditRole)
            model.setData(index, value, qc.Qt.UserRole)
        except IndexError:
            pass

    def build_editor(self, parent, delegate):
        editor = DraggableTreeWidget(parent)
        editor.linklist(self.get_list())
#            editor.editingFinished.connect(delegate.commitAndCloseEditor)
        return editor


class FloatElement(Element):

    def __init__(self, name, ini=0., bottom=popupcad.gui_negative_infinity, top=popupcad.gui_positive_infinity, decimals=popupcad.gui_default_decimals):
        super(FloatElement, self).__init__()
        self.name = name
        self.ini = ini
        self.bottom = bottom
        self.top = top
        self.decimals = decimals

    def set_editor_data(self, index, editor):
        d = index.data(qc.Qt.UserRole)
        editor.setText(str(d))

    def set_model_data(self, editor, model, index, delegate):
        value = editor.text()
        model.setData(index, value, qc.Qt.EditRole)
        model.setData(index, float(value), qc.Qt.UserRole)

    def build_editor(self, parent, delegate):
        editor = qg.QLineEdit(parent)
        val = StrictDoubleValidator(self.bottom, self.top, self.decimals, editor)
        editor.setValidator(val)
        return editor


if __name__ =='__main__':
    import sys
    app = qg.QApplication(sys.argv)
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
    table = Table(JointRow(lambda:range(10),lambda:range(5)),Delegate)
    tc = TableControl(table)
    tc.show()
    sys.exit(app.exec_)