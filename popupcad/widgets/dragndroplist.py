# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtCore as qc
import PySide.QtGui as qg
import sys

from popupcad.filetypes.userdata import UserData
from dev_tools.acyclicdirectedgraph import AcyclicDirectedGraph,Node


class DraggableItem(qg.QListWidgetItem):
    def __init__(self,data,*args,**kwargs):

        super(DraggableItem,self).__init__(str(data),*args,**kwargs)
        self.userdata = data
        self.setFlags(self.flags()|qc.Qt.ItemFlag.ItemIsEditable)
        
    def data(self,role):
        if role == qc.Qt.ItemDataRole.DisplayRole:
            return str(self.userdata)
        elif role == qc.Qt.ItemDataRole.EditRole:
            return self.userdata.getcustomname()
        elif role == qc.Qt.ItemDataRole.UserRole:
            return self.userdata
        else:
            return

    def setData(self,role,value):
        if role == qc.Qt.ItemDataRole.EditRole:
            self.userdata.setcustomname(value)
            return True
        elif role == qc.Qt.ItemDataRole.UserRole:
            self.userdata = value
            return True
        else:
            return False   
    def clone(self,*args,**kwargs):
#        return type(self)(self.userdata)
#        print('cloned')
        return super(DraggableItem,self).clone(*args,**kwargs)
        
    def write(self,*args,**kwargs):
#        return type(self)(self.userdata)
#        print('written')
        return super(DraggableItem,self).write(*args,**kwargs)
        
class DraggableDirectedItem(DraggableItem,Node):
    pass        

class DraggableListWidget(qg.QListWidget):
    signal_edit = qc.Signal(object)
    def __init__(self):
        super(DraggableListWidget,self).__init__()
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setEditTriggers(self.EditTrigger.EditKeyPressed)
        self.doubleClicked.connect(self.itemDoubleClicked)
        self.masterlist = []
        self.refresh()

    def linklist(self,masterlist):
        self.masterlist = masterlist
        self.refresh()
        
    def addData(self,item):    
#        self.masterlist.append(item)
#        self.refresh()
        super(DraggableListWidget,self).addItem(DraggableDirectedItem(item))
        self.refreshmaster()
        
    def allItems(self):    
        items = [self.item(ii) for ii in range(self.count())]
        return items

    def allData(self):
        return [item.userdata for item in self.allItems()]
        
    def refreshmaster(self):
        while len(self.masterlist)>0:
            self.masterlist.pop()
        [self.masterlist.append(item.userdata) for item in self.allItems()]
        return self.masterlist
            
    def refresh(self):
        self.clear()
        [DraggableDirectedItem(item,self) for item in self.masterlist]

    def itemDoubleClicked(self,index):
        userdata = self.model().data(index,qc.Qt.ItemDataRole.UserRole)
        self.signal_edit.emit(userdata)        

    def keyPressEvent(self,event):
        if event.key()==qc.Qt.Key_Delete:
            rows = []
            for ii in self.selectedIndexes():
                rows.append(ii.row())
                rows.sort()
                rows.reverse()
            for ii in rows:
                self.model().removeRows(ii,1,qc.QModelIndex())
            self.refreshmaster()
        else:
            super(DraggableListWidget,self).keyPressEvent(event)
            
class DirectedDraggableListWidget(DraggableListWidget):
    def __init__(self):
        super(DirectedDraggableListWidget,self).__init__()
        m = self.model()
        m.rowsMoved.connect(self.rowsMovedCheck)

    def set_tree_generator(self,generator):
        self.tree_generator = generator

    def rowsMovedCheck(self,sourceindex,rowstart,rowend,destindex,deststart):
#        print(sourceindex, rowstart,rowend,destindex,deststart)
#        items = [self.item(ii) for ii in range(self.model().rowCount())]
#        print(self.tree.sequence_complete_valid(self.allItems()))
        tree = self.tree_generator()
        if not tree.sequence_complete_valid(self.allData()):
            if rowstart<deststart:
                item = self.takeItem(deststart-1)
                self.insertItem(rowstart,item)
                self.currentRowChanged.emit(rowstart)
            elif rowstart>deststart:
                pass
                item = self.takeItem(deststart)
                self.insertItem(rowstart,item)
                self.currentRowChanged.emit(rowstart)
        self.refreshmaster()

def edituserdata(userdata):
    userdata.edit()
def rowchange(data):
    print(data)

if __name__=='__main__':
    app = qg.QApplication(sys.argv)
    
    list1 = range(10)  
    list1 = [UserData(str(item)) for item in list1]

    lw = DirectedDraggableListWidget()
    lw.linklist(list1)
    nodes = lw.allItems()
    connections = list(zip(nodes[:-1],nodes[1:]))
    tree = lambda:AcyclicDirectedGraph(nodes,connections[0:5])
    lw.set_tree_generator(tree)
    lw.signal_edit.connect(edituserdata)
    lw.currentRowChanged.connect(rowchange)
#
    lw.show()    
    m = lw.model()
