# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt
qc = qt.QtCore
qg = qt.QtGui

class ListItem(qg.QListWidgetItem):

    def __init__(self, value):
        super(ListItem, self).__init__(str(value))
        self.value = value
        self.setFlags(self.flags() | qc.Qt.ItemFlag.ItemIsEditable)

    def data(self, role):
        if role == qc.Qt.ItemDataRole.DisplayRole:
            return str(self.value)
        elif role == qc.Qt.ItemDataRole.EditRole:
            return self.value.get_basename()
        elif role == qc.Qt.ItemDataRole.UserRole:
            return self.value
        else:
            return

    def setData(self, role, value):
        if role == qc.Qt.ItemDataRole.EditRole:
            self.value.set_basename(value)
            return True
        elif role == qc.Qt.ItemDataRole.UserRole:
            self.value = value
            return True
        else:
            return False


class ListManager(qg.QWidget):
    items_updated = qc.Signal()
    
    def __init__(self, items, parent=None, name=None):
        super(ListManager, self).__init__(parent)

        self.items = items

        self.itemlist = qg.QListWidget()
        self.refresh_list()

        layout = qg.QHBoxLayout()

        layout.addWidget(self.itemlist)
        self.layout2 = qg.QVBoxLayout()
        layout.addLayout(self.layout2)

        layout3 = qg.QVBoxLayout()
        layout3.setContentsMargins(0, 0, 0, 0)
        if name is not None:
            layout3.addWidget(qg.QLabel(name))
        layout3.addLayout(layout)

        self.setLayout(layout3)

        for widget in self.widgets():
            self.layout2.addWidget(widget)
        self.itemlist.setSelectionMode(self.itemlist.SelectionMode.SingleSelection)
        self.itemlist.doubleClicked.connect(self.itemDoubleClicked)
        self.layout2.addStretch()

#        self.itemlist.itemChanged.connect(self.items_updated)
        
    def buildButtonItem(self, name, method):
        button = qg.QPushButton(name)
        button.clicked.connect(method)
        return button

    def widgets(self):
        actions = []
        actions.append(('Save As...', self.save_item))
        actions.append(('Copy', self.copy_item))
        widgets = [self.buildButtonItem(*action) for action in actions]
        return widgets

    def itemDoubleClicked(self, index):
        try:
            self.edit_item()
        except AttributeError:
            pass

    def remove_item(self):
        for item in self.itemlist.selectedItems():
            self.items.pop(item.value.id)
        self.refresh_list()
        self.items_updated.emit()

    def save_item(self):
        for item in self.itemlist.selectedItems():
            item.value.saveAs()

    def copy_item(self):
        for item in self.itemlist.selectedItems():
            newitem = item.value.copy(identical=False)
            newitem.regen_id()
            self.items[newitem.id] = newitem
        self.refresh_list(newitem)
        self.items_updated.emit()

    def update_list(self,new_items):
        self.items = new_items
        self.refresh_list()
        
    def selected_items(self):
        selected_items = []
        for ii in range(self.itemlist.count()):
            item = self.itemlist.item(ii)
            if item.isSelected():
                selected_items.append(item.value)
        return selected_items
        
    def refresh_list(self, selected_item=None,retain_selection = False):
        if retain_selection:
            selected_items = self.selected_items()
            if len(selected_items)>0:
                selected_item = selected_items[0]
        self.itemlist.clear()
        [self.itemlist.addItem(ListItem(value))
         for key, value in self.items.items()]
        for ii in range(self.itemlist.count()):
            item = self.itemlist.item(ii)
            item.setSelected(item.value == selected_item)

    def clear_selected(self):
        for ii in range(self.itemlist.count()):
            self.itemlist.item(ii).setSelected(False)

class Dummy(object):
    pass


class SketchListManager(ListManager):

    def __init__(self, design, name='Sketch', **kwargs):
        self.design = design
        super(SketchListManager, self).__init__(design.sketches, name=name)
        self.itemlist.doubleClicked.connect(self.edit_method)

    def edit_method(self):
        for item in self.itemlist.selectedItems():
            item.value.edit(None, self.design, selectops=True)

    def new_method(self):
        from popupcad.guis.sketcher import Sketcher
        from popupcad.filetypes.sketch import Sketch

        def accept_method(sketch):
            self.design.sketches[sketch.id] = sketch
            self.refresh_list(sketch)
            self.items_updated.emit()

        sketcher = Sketcher(
            None,
            Sketch(),
            self.design,
            accept_method=accept_method,
            selectops=True)
        sketcher.show()
        sketcher.graphicsview.zoomToFit()

    def load_item(self):
        from popupcad.filetypes.sketch import Sketch
        newitem = Sketch.open()
        self.items[newitem.id] = newitem
        self.refresh_list(newitem)
        self.items_updated.emit()

    def widgets(self):
        actions = []
        actions.append(('New...', self.new_method))
        actions.append(('Edit...', self.edit_method))
        actions.append(('Load...', self.load_item))
        widgets = [self.buildButtonItem(*action) for action in actions]
        widgets.extend(super(SketchListManager, self).widgets())
        return widgets


class AdvancedSketchListManager(SketchListManager):

    def __init__(self, design):
        super(AdvancedSketchListManager, self).__init__(design, name=None)

    def cleanup(self):
        self.design.cleanup_sketches()
        self.refresh_list()
        self.items_updated.emit()

    def widgets(self):
        widgets = []
        widgets.append(self.buildButtonItem('Cleanup', self.cleanup))
        widgets.extend(super(AdvancedSketchListManager, self).widgets())
        widgets.append(self.buildButtonItem('Delete', self.remove_item))
        return widgets

class DesignListManager(ListManager):

    def __init__(self, design, name='Sketch', **kwargs):
        self.design = design
        super(DesignListManager, self).__init__(design.subdesigns, name=name)
#        self.itemlist.doubleClicked.connect(self.edit_method)

#    def edit_method(self):
#        for item in self.itemlist.selectedItems():
#            item.value.edit(None,self.design,selectops = True)

    def load_item(self):
        from popupcad.filetypes.design import Design
        newitem = Design.open()
        newitem.reprocessoperations()
        self.items[newitem.id] = newitem
        self.refresh_list(newitem)
        self.items_updated.emit()

    def widgets(self):
        actions = []
        actions.append(('Load...', self.load_item))
        widgets = [self.buildButtonItem(*action) for action in actions]
        widgets.extend(super(DesignListManager, self).widgets())
        return widgets


class AdvancedDesignListManager(DesignListManager):

    def __init__(self, design):
        super(AdvancedDesignListManager, self).__init__(design, name=None)

    def cleanup(self):
        self.design.cleanup_subdesigns()
        self.refresh_list()
        self.items_updated.emit()

    def widgets(self):
        widgets = []
        widgets.append(self.buildButtonItem('Cleanup', self.cleanup))
        widgets.extend(super(AdvancedDesignListManager, self).widgets())
        widgets.append(self.buildButtonItem('Delete', self.remove_item))
        return widgets

if __name__ == '__main__':
    import sys
    app = qg.QApplication(sys.argv)
    dict1 = {'asdf': Dummy(), 'xxx': Dummy()}
    lm = ListManager(dict1)
    lm.show()
