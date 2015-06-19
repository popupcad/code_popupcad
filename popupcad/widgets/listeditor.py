# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.listwidgetitem import ListWidgetItem


class ListBase(qg.QListWidget):

    def __init__(self, *args, **kwargs):
        super(ListBase, self).__init__(*args, **kwargs)
        self.setMinimumWidth(200)
        self.list = []
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)

    def linklist(self, listin):
        self.list = listin
        self.refresh()

    def add_item(self, item):
        self.list.append(item)
        self.refresh()

    def refresh(self):
        self.clear()
        widgetitems = []
        for item in self.list:
            widgetitem = ListWidgetItem(item, self)
            widgetitems.append(widgetitem)
        return widgetitems

    def removeitem(self, index):
        self.list.pop(index)
        items = self.refresh()
        if len(items) > 0:
            if index == len(items):
                self.setCurrentItem(items[index - 1])
            else:
                self.setCurrentItem(items[index])

    def itemDoubleClicked_method(self, item):
        self.signal_edit.emit(item.customdata)

    def selectItems(self, items):
        for item in items:
            ii = self.list.index(item)
            self.item(ii).setSelected(True)

    def selectedData(self):
        return [item.customdata for item in self.selectedItems()]

    def customadditems(self, items):
        itemlist = []
        heights = []
        for ii, item in enumerate(items):
            listwidgetitem = ListWidgetItem(item, self)
            h = self.sizeHintForRow(ii)
            heights.append(h)
            itemlist.append(listwidgetitem)
        return itemlist


class ListEditor(ListBase):
    signal_edit = qc.Signal(object)
    itemdeleted = qc.Signal(object)

    def __init__(self, *args, **kwargs):
        super(ListEditor, self).__init__(*args, **kwargs)
        self.setSelectionMode(qg.QAbstractItemView.SingleSelection)
        self.itemDoubleClicked.connect(self.itemDoubleClicked_method)

    def keyPressEvent(self, event):
        if event.key() == qc.Qt.Key_Delete:
            for item in self.selectedItems():
                self.removeitem(self.row(item))
                self.itemdeleted.emit(item.customdata)


class ListSelector(ListBase):

    def __init__(self, *args, **kwargs):
        super(ListSelector, self).__init__(*args, **kwargs)
        self.setSelectionMode(self.MultiSelection)

if __name__ == "__main__":
    import sys
    app = qg.QApplication(sys.argv)
    a = ListEditor()
    b = a.model()
