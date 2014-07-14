# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg
from popupcad.filetypes.userdata import UserData
from popupcad.algorithms.acyclicdirectedgraph import AcyclicDirectedGraph,Node

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
    currentRowChanged = qc.Signal(int)

    def __init__(self,*args,**kwargs):
        super(DraggableTreeWidget,self).__init__(*args,**kwargs)
        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.currentItemChanged.connect(self.myItemChanged)
        self.doubleClicked.connect(self.itemDoubleClicked)
        self.disable()

        m = self.model()
        m.rowsInserted.connect(self.myRowsInserted)
        
        
#    def currentOperation(self):
#        index = self.currentValidIndex(ii=-1)
#        m = self.model()
#        if index.parent().isValid():
#            op = m.data(index.parent(),qc.Qt.ItemDataRole.UserRole)
#            return op
#        else:
#            op = m.data(index,qc.Qt.ItemDataRole.UserRole)
#            return op

    def setCurrentIndeces(self,ii,jj=0):
        m = self.model()
        parentindex = m.index(ii,0,qc.QModelIndex())
        if jj==0:
            self.setCurrentIndex(parentindex)
        else:            
            childindex = m.index(jj,0,parentindex)
            self.setCurrentIndex(childindex)
        
    def currentOperationOutputIndex(self):
        index = self.currentValidIndex(ii=-1)
        m = self.model()
        if index.parent().isValid():
            return index.row()+1
        else:
            return 0
            
    def currentValidIndex(self,ii = 0):
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

#    def currentOperationOutput(self):
#        op = self.currentOperation()
#        ii = self.currentOperationOutputIndex()
#        return op.output[ii]

#    def currentRefs(self):
#        op = self.currentOperation()
#        ii = self.currentOperationOutputIndex()
#        return op.id,ii    

    def currentIndeces(self,ii=-1):
        ii = self.currentRow(ii=ii)
        jj = self.currentOperationOutputIndex()
        return ii,jj
        
    def myItemChanged(self,current,previous):
        print current, previous
        self.currentRowChanged.emit(self.currentRow(ii=-1))
        
    def currentRow(self,ii=-1):
        index = self.currentValidIndex(ii=ii)
        if index.parent().isValid():
            return index.parent().row()
        else:
            return index.row()
        
    def linklist(self,masterlist):
        self.masterlist = masterlist
        self.refresh()

    def refresh(self):
        self.clear()
        items = [ParentItem(None,item) for item in self.masterlist]
        self.addTopLevelItems(items)
        self.expandAll()
        
    def allData(self):    
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
        while len(self.masterlist)>0:
            self.masterlist.pop()
        [self.masterlist.append(item) for item in self.allData()]
        return self.masterlist


    def keyPressEvent(self,event):
        if event.key()==qc.Qt.Key_Delete:
            self.deleteCurrent()            
        if event.key()==qc.Qt.Key_Enter or event.key()==qc.Qt.Key_Return:
            index = self.currentValidIndex(ii=-1)
            userdata = self.model().data(index,qc.Qt.ItemDataRole.UserRole)
            self.signal_edit.emit(userdata)   
        else:
            super(DraggableTreeWidget,self).keyPressEvent(event)

    def deleteCurrent(self):
        if self.enabled:
            row = self.currentRow(ii=-1)
            self.model().removeRow(row,qc.QModelIndex())
            self.refreshmaster()
        
    def itemDoubleClicked(self,index):
        userdata = self.model().data(index,qc.Qt.ItemDataRole.UserRole)
        self.signal_edit.emit(userdata)   
        
    def disable(self):
        self.enabled=False
        self.setDragEnabled(False)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.NoDragDrop)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
#        self.doubleClicked.disconnect(self.itemDoubleClicked)

    def enable(self):
        self.enabled=True
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setEditTriggers(self.EditTrigger.EditKeyPressed)
#        self.doubleClicked.connect(self.itemDoubleClicked)
    
    def setnetworkgenerator(self,generator):
        pass

    def myRowsInserted(self,*args,**kwargs):
        self.refreshmaster()
    def currentIndeces2(self):
        indeces = []
        for item in self.selectedItems():
            ii = self.indexFromItem(item)
            if isinstance(item,ChildItem):
                indeces.append((ii.parent().row(),ii.row()))
            else:
                indeces.append((ii.row(),0))
        return indeces
    def selectIndeces(self,indeces,clear = True):
        if clear:
            self.clearSelection()
        for ii,jj in indeces:
            if jj==0:
                item = self.topLevelItem(ii)
            else:
                item = self.topLevelItem(ii).child(jj-1)
            self.setItemSelected(item,True)
                

    def currentRefs(draggabletreewidget):
        '''This only works with OperationList, but I haven't made a new subclass'''
        indeces = []
        for item in draggabletreewidget.selectedItems():
            ii = draggabletreewidget.indexFromItem(item)
            if isinstance(item,ChildItem):
                indeces.append((item.parent().userdata.id,ii.row()+1))
            else:
                indeces.append((item.userdata.id,0))
        return indeces    
    
class DirectedDraggableTreeWidget(DraggableTreeWidget):
    def __init__(self):
        super(DirectedDraggableTreeWidget,self).__init__()
        m = self.model()
        m.rowsInserted.connect(self.myRowsInserted)
        self.block_check = False
        
    def setnetworkgenerator(self,generator):
        self.networkgenerator = generator

    def myRowsInserted(self,*args,**kwargs):
        if not self.block_check:
            network = self.networkgenerator()
            if not network.subsequencecomplete(self.allData()):
                print 'invalid'
                self.refresh()
            else:
                print 'valid'
                self.refreshmaster()

    def linklist(self,masterlist):
        network = self.networkgenerator()
        if network.subsequencecomplete(masterlist):
            super(DirectedDraggableTreeWidget,self).linklist(masterlist)

    def refresh(self):
        print 'refreshing'
        self.block_check = True
        super(DirectedDraggableTreeWidget,self).refresh()
        self.block_check=False

    def deleteCurrent(self):
        rows = []
        for ii in self.selectedIndexes():
            if not ii.parent().isValid():
                rows.append(ii.row())
                rows.sort()
                rows.reverse()

        testlist = self.masterlist[:]
        for ii in rows:
            del testlist[ii]
        network = self.networkgenerator()
        valid = network.subsequencecomplete(testlist)
        print valid
        if valid:
            for ii in rows:
                del self.masterlist[ii]
#                self.model().removeRow(ii,qc.QModelIndex())
        self.refresh()
    def disable(self):
        super(DirectedDraggableTreeWidget,self).disable()
        self.blockSignals(True)
        
    def enable(self):
        super(DirectedDraggableTreeWidget,self).enable()
        self.blockSignals(False)
        

def edituserdata(userdata):
    userdata.edit()

class DummyClass(UserData,Node):
    pass

if __name__=='__main__':
    import sys

    list1 = [DummyClass(str(ii)) for ii in range(5)]
    
    for item in list1:
        outputs = [UserData(str(ii)) for ii in range(2)]
        item.output = outputs

    app = qg.QApplication(sys.argv)
    tw = DirectedDraggableTreeWidget()
    nodes = list1
    connections = zip(nodes[:-1],nodes[1:])
    networkgenerator = lambda:AcyclicDirectedGraph(nodes,connections[0:3])
    tw.setnetworkgenerator(networkgenerator)
    tw.linklist(list1)
    tw.signal_edit.connect(edituserdata)
    tw.show()
    tw.setSelectionMode(tw.SelectionMode.ExtendedSelection)
