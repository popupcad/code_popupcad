#-*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


import qt.QtCore as qc
import qt.QtGui as qg
from popupcad.filetypes.userdata import UserData
from dev_tools.acyclicdirectedgraph import AcyclicDirectedGraph, Node


class NotValid(Exception):
    pass

class TreeItem(qg.QTreeWidgetItem):

    def data(self, column, role):
        if role == qc.Qt.DisplayRole:
            return str(self.userdata)
        elif role == qc.Qt.EditRole:
            return self.userdata.getcustomname()
        elif role == qc.Qt.UserRole:
            return self.userdata
        else:
            return

    def setData(self, column, role, value):
        if role == qc.Qt.EditRole:
            self.userdata.setcustomname(value)
        elif role == qc.Qt.UserRole:
            self.userdata = value
        else:
            return

class ParentItem(TreeItem):

    def __init__(self, parent, data):
        self.userdata = data
        super(ParentItem, self).__init__(parent, [str(data)])

        flags = qc.Qt.NoItemFlags
        flags |= qc.Qt.ItemIsEnabled
        flags |= qc.Qt.ItemIsDragEnabled
        flags |= qc.Qt.ItemIsSelectable
        flags |= qc.Qt.ItemIsEditable
        self.setFlags(flags)

        try:
            outputs = self.userdata.output[:]

            try:
                outputs.pop(0)
            except IndexError:
                pass

            for output in outputs:
                self.addChild(ChildItem(self, output))

        except AttributeError:
            pass


class ChildItem(TreeItem):

    def __init__(self, parent, data):
        self.userdata = data
        super(ChildItem, self).__init__(parent, [str(data)])

        flags = qc.Qt.NoItemFlags
        flags |= qc.Qt.ItemIsEnabled
        flags |= qc.Qt.ItemIsSelectable
        flags |= qc.Qt.ItemIsEditable
        self.setFlags(flags)


class DraggableTreeWidget(qg.QTreeWidget):
    signal_edit = qc.Signal(object)
    currentRowChanged = qc.Signal(int, int)

    def parent_index(self, index):
        if index.parent().isValid():
            return index.parent()
        else:
            return index

    def delete_index(self, index):
        self.model().removeRow(index.row())
        self.refreshmaster()

    def __init__(self, *args, **kwargs):

        super(DraggableTreeWidget, self).__init__(*args, **kwargs)
        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.currentItemChanged.connect(self.myItemChanged)
        self.doubleClicked.connect(self.itemDoubleClicked)
        self.disable()

        m = self.model()
        m.rowsInserted.connect(self.myRowsInserted)
        self.emit_item_change = True
        self.master_refreshing = False
        self.refreshing = False

    def currentOperationOutputIndex(self):
        index = self.currentValidIndex(ii=-1)
        if index.parent().isValid():
            return index.row() + 1
        else:
            return 0

    def currentValidIndex(self, ii=0):
        index = self.currentIndex()
        return index
#This was removed because it is causing problems in mac, and it doesn't seem to be necessary        
#        if index.isValid():
#            return index
#        else:
#            m = self.model()
#            n = m.rowCount()
#            if n == 0:
#                jj = 0
#            else:
#                jj = ii % n
#            index = m.createIndex(jj, 0)
#            return index

    def currentIndeces(self, ii=-1):
        ii = self.currentRow(ii=ii)
        jj = self.currentOperationOutputIndex()
        return ii, jj

    def myItemChanged(self, current, previous):
        if not (self.refreshing or self.master_refreshing):
            self.currentRowChanged.emit(*self.currentIndeces())

    def currentRow(self, ii=-1):
        index = self.currentValidIndex(ii=ii)
        return self.parent_index(index).row()

    def linklist(self, masterlist):
        self.masterlist = masterlist
        self.refresh()

    def refresh(self):
        self.refreshing = True

        selected_items = self.selectedItems()
        selected_ids = []
        for item in selected_items:
            ii = self.indexFromItem(item)
            if isinstance(item, ChildItem):
                selected_ids.append((item.parent().userdata.id, ii.row() + 1))
            else:
                selected_ids.append((item.userdata.id, 0))
#        for item in
#        selected_id = self.model().data(index,qc.Qt.UserRole).id
        new_indeces = []
        new_ids = [item.id for item in self.masterlist]
        for a, b in selected_ids:
            try:
                new_indeces.append((new_ids.index(a), b))
            except IndexError:
                pass
            except ValueError:
                pass

        self.emit_item_change = False
        self.clear()
        self.emit_item_change = True
        items = [ParentItem(None, item) for item in self.masterlist]
        self.addTopLevelItems(items)
        self.collapseAll()

#        self.selectIndeces(new_indeces)

        self.refreshing = False

    def allData(self):
        m = self.model()
        num_rows = m.rowCount()

        role = qc.Qt.UserRole

        items = []
        for ii in range(num_rows):
            index = m.index(ii, 0, qc.QModelIndex())
            item = m.data(index, role)
            items.append(item)
        return items

    def refreshmaster(self):

        self.master_refreshing = True
        newmasterlist = [item for item in self.allData()]

#        self.clear()

        while len(self.masterlist) > 0:
            self.masterlist.pop()

        [self.masterlist.append(item) for item in newmasterlist]

#        items = [ParentItem(None,item) for item in self.masterlist]
#        self.addTopLevelItems(items)
#        self.expandAll()

#        return self.masterlist
        self.master_refreshing = False

    def keyPressEvent(self, event):
        if not (self.refreshing or self.master_refreshing):
            if event.key() == qc.Qt.Key_Delete:
                self.deleteCurrent()
            if event.key() == qc.Qt.Key_Enter or event.key(
            ) == qc.Qt.Key_Return:
                index = self.currentValidIndex(ii=-1)
                userdata = self.model().data(index,qc.Qt.UserRole)
                item = self.itemFromIndex(index)
                if isinstance(item, ParentItem):
                    self.signal_edit.emit(userdata)
            else:
                super(DraggableTreeWidget, self).keyPressEvent(event)

    def deleteCurrent(self):
        if self.enabled:
            if not (self.refreshing or self.master_refreshing):
                row = self.currentRow(ii=-1)
                self.model().removeRow(row, qc.QModelIndex())
                self.refreshmaster()

    def itemDoubleClicked(self, index):
        if not (self.refreshing or self.master_refreshing):
            userdata = self.model().data(index, qc.Qt.UserRole)
            item = self.itemFromIndex(index)
            if isinstance(item, ParentItem):
                self.signal_edit.emit(userdata)

    def disable(self):
        self.enabled = False
        self.setDragEnabled(False)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.NoDragDrop)
        
        edit_trigger = self.EditTrigger()
        self.setEditTriggers(edit_trigger)

    def enable(self):
        self.enabled = True
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.InternalMove)

        edit_trigger = self.EditTrigger(self.EditKeyPressed)
        self.setEditTriggers(edit_trigger)

#    def set_tree_generator(self,generator):
#        pass

    def myRowsInserted(self, *args, **kwargs):
        if not (self.refreshing or self.master_refreshing):
            self.refreshmaster()

    def currentIndeces2(self):
        indeces = []
        for item in self.selectedItems():
            ii = self.indexFromItem(item)
            if isinstance(item, ChildItem):
                indeces.append((ii.parent().row(), ii.row() + 1))
            else:
                indeces.append((ii.row(), 0))
        return indeces

    def selectIndeces(self, indeces, clear=True):
        if clear:
            self.clearSelection()
        for ii, jj in indeces:
            m = self.model()
            n = m.rowCount()
            if n > 0:
                ii = ii % n

                if jj == 0:
                    item = self.topLevelItem(ii)
                else:
                    item = self.topLevelItem(ii).child(jj - 1)
#                self.setItemSelected(item, True)
                item.setSelected(True)

    def currentRefs(self):
        '''This only works with OperationList, but I haven't made a new subclass'''
        indeces = []
        for item in self.selectedItems():
            ii = self.indexFromItem(item)
            if isinstance(item, ChildItem):
                indeces.append((item.parent().userdata.id, ii.row() + 1))
            else:
                indeces.append((item.userdata.id, 0))
        return indeces


class DirectedDraggableTreeWidget(DraggableTreeWidget):

    def __init__(self, *args, **kwargs):
        super(DirectedDraggableTreeWidget, self).__init__(*args, **kwargs)
        self.setContextMenuPolicy(qc.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenu)

    def onCustomContextMenu(self, point):
        index = self.indexAt(point)
        item = self.itemAt(point)
        if isinstance(item, ParentItem):
            #            if index.isValid():
            menu = qg.QMenu()
            menu.addAction(qg.QAction('edit...',menu,triggered=lambda: self.signal_edit.emit(item.userdata)))
            menu.addAction(qg.QAction('rename...',menu,triggered=lambda: self.edit(index)))
            menu.addAction(qg.QAction('delete',menu,triggered=lambda: self.delete_indeces([index])))
            menu.addAction(qg.QAction('parents',menu,triggered=lambda: self.show_parents(item)))
            menu.addAction(qg.QAction('children',menu,triggered=lambda: self.show_children(item)))
            menu.addAction(qg.QAction('edit description...',menu,triggered=item.userdata.edit_description))
            menu.addAction(qg.QAction('set main image',menu,triggered=lambda: self.set_main_image(item)))
            menu.addAction(qg.QAction('mass properties...',menu,triggered=lambda: self.get_mass_props(item.userdata.output[0])))
            menu.exec_(self.mapToGlobal(point))
        else:
            menu = qg.QMenu()
            menu.addAction(qg.QAction('mass properties...',menu,triggered=lambda: self.get_mass_props(item.userdata)))
            menu.exec_(self.mapToGlobal(point))

    def set_main_image(self, item):
#        self.design = self.get_design()
#        if isinstance(item, ParentItem):
#            self.design.set_main_operation(self.currentRefs()[0])
        pass

    def get_mass_props(self,output):
        gl = output.generic_laminate()
        volume_total,mass_total,center_of_mass,I = gl.mass_properties()
        string = 'volume: '+str(volume_total)+'\nmass = '+str(mass_total)+'\ncenter of mass: \n'+str(center_of_mass)+'\nInertia = \n'+str(I)
        import popupcad.widgets.textwindow as tw
        dialog = qg.QDialog()
        
        widget = tw.TextWindow()
        widget.appendText(string)
        layout = qg.QVBoxLayout()
        layout.addWidget(widget)
        dialog.setLayout(layout)
        widget.close_button.clicked.connect(dialog.close)
        dialog.exec_()
#        widget.show()
        

    def show_parents(self, item):
        self.tree_generator()
        m = qg.QMessageBox()
        m.setText(str(item.userdata.ancestors()))
        m.exec_()

    def show_children(self, item):
        self.tree_generator()
        m = qg.QMessageBox()
        m.setText(str(item.userdata.decendents()))
        m.exec_()

    def set_tree_generator(self, generator):
        self.tree_generator = generator

    def set_get_design(self, get_design):
        self.get_design = get_design

    def myRowsInserted(self, *args, **kwargs):
        if not (self.refreshing or self.master_refreshing):
            tree = self.tree_generator()
            if not tree.sequence_complete_valid(self.allData()):
#                self.refresh()
                raise NotValid()
            else:
                self.refreshmaster()

    def linklist(self, masterlist):
#        tree = self.tree_generator()
#        if tree.sequence_complete_valid(masterlist):
#            super(DirectedDraggableTreeWidget,self).linklist(masterlist)
#        else:
#            raise(Exception('invalid sequence of operations'))
        super(DirectedDraggableTreeWidget, self).linklist(masterlist)

    def deleteCurrent(self):
        self.delete_indeces(self.selectedIndexes())

    def delete_indeces(self, indeces):
        if self.enabled:
            rows = []
            for ii in indeces:
                if not ii.parent().isValid():
                    rows.append(ii.row())
            rows.sort()
            rows.reverse()

            self.tree_generator()
            for ii in rows:
                children = self.masterlist[ii].decendents()
                if not children:
                    del self.masterlist[ii]
                else:
                    m = qg.QMessageBox()
                    m.setIcon(m.Information)
                    m.setText(str(self.masterlist[ii]) + ' cannot be deleted.')
                    m.setInformativeText('Delete all dependent operations?')
                    s = 'This is due to the following dependent operations:\n'
                    for child in children[:-1]:
                        s += '{0},\n'.format(str(child))
                    s += '{0}'.format(str(children[-1]))
                    m.setDetailedText(s)
                    m.addButton(m.YesToAll)
                    m.addButton(m.Cancel)
                    result = m.exec_()
                    if result == m.YesToAll:
                        alltodelete = [
                            self.masterlist.index(item) for item in children]
                        alltodelete.append(ii)
                        alltodelete = sorted(alltodelete)[::-1]
                        [self.masterlist.pop(jj) for jj in alltodelete]
                    else:
                        pass
            self.refresh()

    def disable(self):
        super(DirectedDraggableTreeWidget, self).disable()
        self.blockSignals(True)

    def enable(self):
        super(DirectedDraggableTreeWidget, self).enable()
        self.blockSignals(False)

if __name__ == '__main__':
    def edituserdata(userdata):
        userdata.edit()

    class DummyClass(UserData, Node):
        def __init__(self,*args,**kwargs):
            super(DummyClass,self).__init__(*args,**kwargs)
            self.id=id(self)

    import sys

    list1 = [DummyClass(str(ii)) for ii in range(5)]

    for item in list1:
        outputs = [UserData(str(ii)) for ii in range(2)]
        item.output = outputs

    app = qg.QApplication(sys.argv)
    tw = DirectedDraggableTreeWidget()
    nodes = list1
    connections = list(zip(nodes[:-1], nodes[1:]))
    tree_generator = lambda: AcyclicDirectedGraph(nodes, connections[0:3])
    tw.set_tree_generator(tree_generator)
    tw.linklist(list1)
    tw.signal_edit.connect(edituserdata)
    tw.show()
    tw.setSelectionMode(tw.ExtendedSelection)
    print(tw.currentIndex())
    sys.exit(app.exec_())
