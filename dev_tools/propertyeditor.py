# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg

class Child(object):
    #    display = ['a','b','c','d','e']
    editable = ['a', 'b', 'c']
    new_attr = {'<new_string>': '', '<new_float>': 0.0}
    deletable = ['*']
    attr_names_editable = True

    def __init__(self):
        self.a = range(5)
        self.b = 'text'
        self.c = 4.5
        self.d = False
        self.e = 5


class Depth(object):
    #    hidden = ['depth']

    depth = -1

    def __init__(self):
        if Depth.depth < 10:
            Depth.depth += 1
            self.a = Depth()


class Parent(object):
    #    display = ['child','tuple1','list1','x','a','dict1']
    editable = ['child', 'tuple1', 'list1', 'x', 'a', 'dict1']
    deletable = ['*']
    attr_names_editable = True

    def __init__(self):
        self.child = Child()
        self.tuple1 = (234.5, 1, Child())
        self.list1 = [234.5, 1, Child()]
        self.x = 123.4
        self.a = 5
        self.dict1 = {'a': 5, 'b': 6.6}
        self.recursiveclass = Depth()

class ParentItem(object):
    valuekeys = [int, float, bool, str]
    listkeys = [tuple, list]

    def __init__(self, value, treewidgetparent):
        self.structureparent = treewidgetparent
        self.value = value
        self.valuetype = type(value)
        self.children = []
        self.level = 1
        self.generatechildren(self.structureparent)

    def addChild(self, item):
        self.children.append(item)
        self.structureparent.addTopLevelItem(item)

    def removeattr(self, key):
        try:
            delattr(self.value, key)
        except AttributeError:
            pass

    def removeAllChildren(self):
        for ii in range(len(self.children))[::-1]:
            self.structureparent.takeTopLevelItem(ii)

    def setchild(self, key, value):
        if self.valuetype in self.valuekeys:
            raise Exception
        elif self.valuetype == list:
            index = int(key[1:-1])
            self.value[index] = value
#            self.updateparent()
        elif self.valuetype == tuple:
            index = int(key[1:-1])
            oldtuple = list(self.value)
            oldtuple[index] = value
            self.value = tuple(oldtuple)
            self.updateparent()
        elif self.valuetype == dict:
            self.value[key] = value
        else:
            setattr(self.value, key, value)

    def updateparent(self):
        pass

    def parent(self):
        return self.structureparent

    def sortChildren(self, *args, **kwargs):
        self.structureparent.sortItems(*args, **kwargs)

    def generatechildren(self, parent):
        if self.valuetype in self.valuekeys:
            pass
        elif (self.valuetype == tuple) or (self.valuetype == list):
            for ii, item in enumerate(self.value):
                self.addChild(TreeItem(parent,self,'[{index:0d}]'.format(index=ii),item,self.level + 1))
        elif self.valuetype == dict:
            for key, value in self.value.items():
                self.addChild(TreeItem(parent,self,key,value,self.level + 1))
        else:
            keys = dir(self.value)

            class dummy(object):
                pass
            commonkeys = dir(dummy())
            keys = list(set(keys) - set(commonkeys))

            try:
                keys = list(set(keys) - set(self.value.hidden))
            except AttributeError:
                pass

            keys2 = []
            for key in keys:
                try:
                    if key[0] != '_':
                        keys2.append(key)
                except IndexError:
                    keys2.append(key)
            keys = keys2

            try:
                keys = list(set(keys).intersection(self.value.display))
            except AttributeError:
                pass

            keys = list(set(keys) - set(['hidden','editable','deletable','new_attr','attr_names_editable']))

            classkeys = []
            for key in keys:
                value = getattr(self.value, key)
                if hasattr(value, '__call__'):
                    pass
                else:
                    classkeys.append(key)

            classkeys.sort()
            for key in classkeys:
                value = getattr(self.value, key)
                self.addChild(TreeItem(parent,self,key,value,self.level +1))

            try:
                for key, value in self.value.new_attr.items():
                    self.addChild(InsertNewWidgetItem(parent,self,self.level + 1,key,value))
            except AttributeError:
                pass
            self.sortChildren(0, qc.Qt.AscendingOrder)

    def refresh(self):
        self.removeAllChildren()
        self.generatechildren(self.structureparent)

    def is_editable(self, column):
        return False

class Item(object):
    valuekeys = [int, float, bool, str]
    listkeys = [tuple, list]

    def addChild(self, item):
        self.children.append(item)
        self.structureparent.addTopLevelItem(item)

    def removeattr(self, key):
        try:
            delattr(self.value, key)
        except AttributeError:
            pass

    def setchild(self, key, value):
        if self.valuetype in self.valuekeys:
            raise Exception
        elif self.valuetype == list:
            index = int(key[1:-1])
            self.value[index] = value
#            self.updateparent()
        elif self.valuetype == tuple:
            index = int(key[1:-1])
            oldtuple = list(self.value)
            oldtuple[index] = value
            self.value = tuple(oldtuple)
            self.updateparent()
        elif self.valuetype == dict:
            self.value[key] = value
        else:
            setattr(self.value, key, value)

    def updateparent(self):
        pass

    def parent(self):
        return self.structureparent

    def sortChildren(self, *args, **kwargs):
        self.structureparent.sortItems(*args, **kwargs)

    def generatechildren(self, parent):
        if self.valuetype in self.valuekeys:
            pass
        elif (self.valuetype == tuple) or (self.valuetype == list):
            for ii, item in enumerate(self.value):
                self.addChild(TreeItem(parent,self,'[{index:0d}]'.format(index=ii),item,self.level + 1))
        elif self.valuetype == dict:
            for key, value in self.value.items():
                self.addChild(TreeItem(parent,self,key,value,self.level + 1))
        else:
            keys = dir(self.value)

            class dummy(object):
                pass
            commonkeys = dir(dummy())
            keys = list(set(keys) - set(commonkeys))

            try:
                keys = list(set(keys) - set(self.value.hidden))
            except AttributeError:
                pass

            keys2 = []
            for key in keys:
                try:
                    if key[0] != '_':
                        keys2.append(key)
                except IndexError:
                    keys2.append(key)
            keys = keys2

            try:
                keys = list(set(keys).intersection(self.value.display))
            except AttributeError:
                pass

            keys = list(set(keys) - set(['hidden','editable','deletable','new_attr','attr_names_editable']))

            classkeys = []
            for key in keys:
                value = getattr(self.value, key)
                if hasattr(value, '__call__'):
                    pass
                else:
                    classkeys.append(key)

            classkeys.sort()
            for key in classkeys:
                value = getattr(self.value, key)
                self.addChild(TreeItem(parent,self,key,value,self.level +1))

            try:
                for key, value in self.value.new_attr.items():
                    self.addChild(InsertNewWidgetItem(parent,self,self.level + 1,key,value))
            except AttributeError:
                pass
            self.sortChildren(0, qc.Qt.AscendingOrder)

    def refresh(self):
        self.removeAllChildren()
        self.generatechildren(self.structureparent)

    def is_editable(self, column):
        return False    

class TreeItem(qg.QTreeWidgetItem, Item):
    depthlimit = 5

    def __init__(self, parent, dataparent, key, value, level):
        self.structureparent = self
        self.dataparent = dataparent
        self.key = key
        self.value = value
        self.valuetype = type(value)
        self.level = level

        qg.QTreeWidgetItem.__init__(self, parent)
        self.setFlags(qc.Qt.ItemIsEditable | qc.Qt.ItemIsEnabled | qc.Qt.ItemIsSelectable)

        if self.level < self.depthlimit:
            self.generatechildren(self)

    def updateparent(self):
        self.dataparent.setchild(self.key, self.value)

    def parent(self):
        return qg.QTreeWidgetItem.parent(self)

    def removeAllChildren(self):
        for ii in range(self.childCount())[::-1]:
            self.removeChild(self.child(ii))

    def is_editable(self, column):
        if column == 1:
            try:
                result = (
                    self.key in self.dataparent.value.editable) or (
                    '*' in self.dataparent.value.editable)
                return result
            except AttributeError:
                if self.dataparent.valuetype in self.dataparent.listkeys:
                    return self.dataparent.is_editable(column)
                return False
        if column == 0:
            try:
                return self.dataparent.value.attr_names_editable
            except AttributeError:
                return False
        else:
            return False

    def is_deletable(self):
        try:
            return self.key in self.dataparent.value.deletable or '*'in self.dataparent.value.deletable
        except AttributeError:
            if self.dataparent.valuetype in self.dataparent.listkeys:
                return False
            return False

    def setData(self, column, role, value):
        if role == qc.Qt.EditRole:
            if self.is_editable(column):
                if column == 1:
                    if self.valuetype == bool:
                        value = value.lower()
                        if (value == 'false') or (
                                value == '0') or (value == 'f'):
                            self.value = False
                        elif (value == 'true') or (value == '1') or (value == 't'):
                            self.value = True
                        self.updateparent()
                    elif self.valuetype in self.valuekeys:
                        self.value = self.valuetype(value)
                        self.updateparent()
                if column == 0:
                    if not hasattr(self.dataparent.value, value):
                        self.dataparent.removeattr(value)
                        self.dataparent.removeattr(self.key)
                        self.key = value
                        self.updateparent()
                    self.dataparent.refresh()

    def data(self, column, role):
        if column == 0:
            if role == qc.Qt.DisplayRole:
                return self.key
            if role == qc.Qt.EditRole:
                return self.key
        elif column == 1:
            if role == qc.Qt.DisplayRole:
                return str(self.value)
            if role == qc.Qt.EditRole:
                return str(self.value)


class InsertNewWidgetItem(TreeItem):

    def __init__(self,parent,dataparent,level,key='<new string>',value=''):
        self.dataparent = dataparent
        self.key = key
        self.value = value
        self.valuetype = type(value)
        self.level = level

        qg.QTreeWidgetItem.__init__(self, parent, [key, str(value)])
        self.setFlags(qc.Qt.ItemIsEditable | qc.Qt.ItemIsEnabled | qc.Qt.ItemIsSelectable)

        if self.level < self.depthlimit:
            self.generatechildren(self)

    def setData(self, column, role, value):
        if column == 0:
            if role == qc.Qt.EditRole:
                if isinstance(self.value, list):
                    newvalue = self.value[:]
                elif isinstance(self.value, tuple):
                    newvalue = self.value[:]
                elif type(self.value) in ParentItem.valuekeys:
                    newvalue = self.value
                else:
                    newvalue = self.value.copy()
                newtwi = TreeItem(self.parent(),self.dataparent,value,newvalue,self.dataparent.level +1)
                self.dataparent.addChild(newtwi)
                try:
                    self.dataparent.value.editable.append(value)
                except AttributeError:
                    pass
                newtwi.updateparent()
                self.dataparent.sortChildren(0, qc.Qt.AscendingOrder)

class PropertyEditor(qg.QTreeWidget):

    def __init__(self, data, *args, **kwargs):
        qg.QTreeWidget.__init__(self,*args,**kwargs)
#        super(PropertyEditor, self).__init__(*args, **kwargs)
        self.setHeaderLabels(['key', 'value'])
        self.parent = ParentItem(data, self)
        self.setAlternatingRowColors(True)

    def keyPressEvent(self, event):
        if event.key() == qc.Qt.Key_Delete:
            item = self.selectedItems()[0]

            if item.is_deletable():
                item.dataparent.removeattr(item.key)
                item.dataparent.refresh()

if __name__ == '__main__':
    import sys
    app = qg.QApplication(sys.argv)

    parent = Parent()
    pv = PropertyEditor(parent)

    pv.show()
#    sys.exit(app.exec_())
