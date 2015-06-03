#-*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.userdata import UserData
from dev_tools.acyclicdirectedgraph import AcyclicDirectedGraph,Node

def debugprint(*args,**kwargs):
    pass

class TreeItem(qg.QTreeWidgetItem):
    def data(self,column,role):
        if role == qc.Qt.ItemDataRole.DisplayRole:
            return str(self.userdata)
        elif role == qc.Qt.ItemDataRole.EditRole:
            return self.userdata.getcustomname()
        elif role == qc.Qt.ItemDataRole.UserRole:
            return self.userdata
        else:
            return

    def setData(self,column,role,value):
        if role == qc.Qt.ItemDataRole.EditRole:
            self.userdata.setcustomname(value)
            return True
        elif role == qc.Qt.ItemDataRole.UserRole:
            self.userdata = value
            return True
        else:
            return False        

class ParentItem(TreeItem):
    def __init__(self,parent,data):
        self.userdata = data
        super(ParentItem,self).__init__(parent,[str(data)])

        flags = qc.Qt.ItemFlag.NoItemFlags
        flags |= qc.Qt.ItemFlag.ItemIsEnabled
        flags |= qc.Qt.ItemFlag.ItemIsDragEnabled
        flags |= qc.Qt.ItemFlag.ItemIsSelectable
        flags |= qc.Qt.ItemFlag.ItemIsEditable
        self.setFlags(flags)

        try:
            outputs = self.userdata.output[:]
        
            try:
                outputs.pop(0)
            except IndexError:
                pass
        
            for output in outputs:
                self.addChild(ChildItem(self,output))

        except AttributeError:
            pass
        
class ChildItem(TreeItem):
    def __init__(self,parent,data):
        self.userdata = data
        super(ChildItem,self).__init__(parent,[str(data)])

        flags = qc.Qt.ItemFlag.NoItemFlags
        flags |= qc.Qt.ItemFlag.ItemIsEnabled
        flags |= qc.Qt.ItemFlag.ItemIsSelectable
        flags |= qc.Qt.ItemFlag.ItemIsEditable
        self.setFlags(flags)

class DraggableTreeWidget(qg.QTreeWidget):
    signal_edit = qc.Signal(object)
    currentRowChanged = qc.Signal(int,int)

    def __init__(self,*args,**kwargs):
        debugprint('innit')
        
        super(DraggableTreeWidget,self).__init__(*args,**kwargs)
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
#        self.setContextMenuPolicy(qc.Qt.CustomContextMenu)
#        self.customContextMenuRequested.connect(self.onCustomContextMenu)

    def onCustomContextMenu(self,point):
        index = self.indexAt(point)
        if index.isValid():
            menu = qg.QMenu()
            action1 =qg.QAction('asdf',menu)
            menu.addAction(action1)
            menu.exec_(self.mapToGlobal(point))

    def currentOperationOutputIndex(self):
        debugprint('currentOperationOutputIndex')
        index = self.currentValidIndex(ii=-1)
        if index.parent().isValid():
            return index.row()+1
        else:
            return 0
            
    def currentValidIndex(self,ii = 0):
        debugprint('currentValidIndex')
        index = self.currentIndex()
        if index.isValid():
            return index
        else:
            m = self.model()
            n = m.rowCount()
            if n==0:
                jj = 0
            else:
                jj = ii%n
            index = m.createIndex(jj,0) 
            return index

    def currentIndeces(self,ii=-1):
        debugprint('currentIndeces')
        ii = self.currentRow(ii=ii)
        jj = self.currentOperationOutputIndex()
        return ii,jj
        
    def myItemChanged(self,current,previous):
        if not (self.refreshing or self.master_refreshing):
            debugprint('myItemChanged')
            self.currentRowChanged.emit(*self.currentIndeces())
        
    def currentRow(self,ii=-1):
        debugprint('currentRow')
        index = self.currentValidIndex(ii=ii)
        if index.parent().isValid():
            return index.parent().row()
        else:
            return index.row()
        
    def linklist(self,masterlist):
        debugprint('linklist')
        self.masterlist = masterlist
        self.refresh()

    def refresh(self):
        debugprint('refresh')
        self.refreshing = True
        
#        index = self.currentValidIndex(-1)
        selected_items = self.selectedItems()
        selected_ids = []
        for item in selected_items:
            ii = self.indexFromItem(item)
            if isinstance(item,ChildItem):
                selected_ids.append((item.parent().userdata.id,ii.row()+1))
            else:
                selected_ids.append((item.userdata.id,0))
#        for item in 
#        selected_id = self.model().data(index,qc.Qt.ItemDataRole.UserRole).id
        new_indeces = []
        new_ids = [item.id for item in self.masterlist]
        for a,b in selected_ids:
            try:
                new_indeces.append((new_ids.index(a),b))
            except IndexError:
                pass
            except ValueError:
                pass
            
                
        self.emit_item_change = False
        self.clear()
        self.emit_item_change = True
        items = [ParentItem(None,item) for item in self.masterlist]
        self.addTopLevelItems(items)
        self.expandAll()

#        self.selectIndeces(new_indeces)
        
        self.refreshing = False
    def allData(self):    
        debugprint('allData')
        m = self.model()
        num_rows = m.rowCount()        
        
        role = qc.Qt.ItemDataRole.UserRole        
        
        items = []
        for ii in range(num_rows):
            index = m.index(ii,0,qc.QModelIndex())
            item = m.data(index,role)
            items.append(item)
        return items

    def refreshmaster(self):
        debugprint('refreshmaster')
        
        self.master_refreshing = True
        newmasterlist = [item for item in self.allData()]
        debugprint('new master list')

#        self.clear()
#        debugprint('cleared')

        while len(self.masterlist)>0:
            self.masterlist.pop()
        debugprint('clearing old master list')
        
        [self.masterlist.append(item) for item in newmasterlist]
        debugprint('added new items')

#        items = [ParentItem(None,item) for item in self.masterlist]
#        debugprint('new parent items')
#        self.addTopLevelItems(items)
#        debugprint('new top level items')
#        self.expandAll()
#        debugprint('expanded all')

#        return self.masterlist
        self.master_refreshing = False


    def keyPressEvent(self,event):
        debugprint('keyPressEvent')
        if not (self.refreshing or self.master_refreshing):
            if event.key()==qc.Qt.Key_Delete:
                self.deleteCurrent()            
            if event.key()==qc.Qt.Key_Enter or event.key()==qc.Qt.Key_Return:
                index = self.currentValidIndex(ii=-1)
                userdata = self.model().data(index,qc.Qt.ItemDataRole.UserRole)
                self.signal_edit.emit(userdata)   
            else:
                super(DraggableTreeWidget,self).keyPressEvent(event)

    def deleteCurrent(self):
        debugprint('deleteCurrent')
        if self.enabled:
            if not (self.refreshing or self.master_refreshing):
                row = self.currentRow(ii=-1)
                self.model().removeRow(row,qc.QModelIndex())
                self.refreshmaster()
        
    def itemDoubleClicked(self,index):
        debugprint('itemDoubleClicked')
        if not (self.refreshing or self.master_refreshing):
            userdata = self.model().data(index,qc.Qt.ItemDataRole.UserRole)
            self.signal_edit.emit(userdata)   
        
    def disable(self):
        debugprint('disable')
        self.enabled=False
        self.setDragEnabled(False)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.NoDragDrop)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)

    def enable(self):
        debugprint('enable')
        self.enabled=True
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setEditTriggers(self.EditTrigger.EditKeyPressed)
    
#    def setnetworkgenerator(self,generator):
#        debugprint('setnetworkgenerator')
#        pass

    def myRowsInserted(self,*args,**kwargs):
        debugprint('myRowsInserted')
        if not (self.refreshing or self.master_refreshing):
            self.refreshmaster()

    def currentIndeces2(self):
        debugprint('currentIndeces2')
        indeces = []
        for item in self.selectedItems():
            ii = self.indexFromItem(item)
            if isinstance(item,ChildItem):
                indeces.append((ii.parent().row(),ii.row()+1))
            else:
                indeces.append((ii.row(),0))
        return indeces

    def selectIndeces(self,indeces,clear = True):
        debugprint('selectIndeces')
        if clear:
            self.clearSelection()
        for ii,jj in indeces:
            m = self.model()
            n = m.rowCount()
            if n>0:
                ii = ii%n
            
                if jj==0:
                    item = self.topLevelItem(ii)
                else:
                    item = self.topLevelItem(ii).child(jj-1)
                self.setItemSelected(item,True)

    def currentRefs(self):
        debugprint('currentrefs')
        '''This only works with OperationList, but I haven't made a new subclass'''
        indeces = []
        for item in self.selectedItems():
            ii = self.indexFromItem(item)
            if isinstance(item,ChildItem):
                indeces.append((item.parent().userdata.id,ii.row()+1))
            else:
                indeces.append((item.userdata.id,0))
        return indeces    
        
class DirectedDraggableTreeWidget(DraggableTreeWidget):
    def setnetworkgenerator(self,generator):
        debugprint('setnetworkgenerator_p')
        self.networkgenerator = generator

    def myRowsInserted(self,*args,**kwargs):
        if not (self.refreshing or self.master_refreshing):
            debugprint('myrowsinserted_p')
            network = self.networkgenerator()
            if not network.sequence_complete_valid(self.allData()):
                self.refresh()
                raise(Exception('Item cannot be moved. This would move a parent operation below a child.'))
            else:
                self.refreshmaster()

    def linklist(self,masterlist):
        debugprint('linklist_p')
#        network = self.networkgenerator()
#        if network.sequence_complete_valid(masterlist):
#            super(DirectedDraggableTreeWidget,self).linklist(masterlist)
#        else:
#            raise(Exception('invalid sequence of operations'))
        super(DirectedDraggableTreeWidget,self).linklist(masterlist)

    def deleteCurrent(self):
        debugprint('deletecurrent_p')
        if self.enabled:
            rows = []
            for ii in self.selectedIndexes():
                if not ii.parent().isValid():
                    rows.append(ii.row())
                    rows.sort()
                    rows.reverse()
            
            self.networkgenerator()
            for ii in rows:    
                children = self.masterlist[ii].allchildren()
                if not children:
                    del self.masterlist[ii]
                else:
                    m = qg.QMessageBox()
                    m.setIcon(m.Information)
                    m.setText(str(self.masterlist[ii])+' cannot be deleted.')
                    m.setInformativeText('Delete all dependent operations?')
                    s = 'This is due to the following dependent operations:\n'
                    for child in children[:-1]:
                        s+='{0},\n'.format(str(child))
                    s+='{0}'.format(str(children[-1]))
                    m.setDetailedText(s)
                    m.addButton(m.YesToAll)
                    m.addButton(m.Cancel)
                    result = m.exec_()
                    if result == m.YesToAll:
                        alltodelete = [self.masterlist.index(item) for item in children]
                        alltodelete.append(ii)
                        alltodelete = sorted(alltodelete)[::-1]
                        [self.masterlist.pop(jj) for jj in alltodelete]
                    else:
                        pass
            self.refresh()

    def disable(self):
        debugprint('disable_p')
        super(DirectedDraggableTreeWidget,self).disable()
        self.blockSignals(True)
        
    def enable(self):
        debugprint('enable_p')
        super(DirectedDraggableTreeWidget,self).enable()
        self.blockSignals(False)
    
if __name__=='__main__':
    def edituserdata(userdata):
        userdata.edit()
    class DummyClass(UserData,Node):
        pass
    import sys

    list1 = [DummyClass(str(ii)) for ii in range(5)]
    
    for item in list1:
        outputs = [UserData(str(ii)) for ii in range(2)]
        item.output = outputs

    app = qg.QApplication(sys.argv)
    tw = DirectedDraggableTreeWidget()
    nodes = list1
    connections = list(zip(nodes[:-1],nodes[1:]))
    networkgenerator = lambda:AcyclicDirectedGraph(nodes,connections[0:3])
    tw.setnetworkgenerator(networkgenerator)
    tw.linklist(list1)
    tw.signal_edit.connect(edituserdata)
    tw.show()
    tw.setSelectionMode(tw.SelectionMode.ExtendedSelection)
