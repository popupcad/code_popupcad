# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg

class ListItem(qg.QListWidgetItem):
    def __init__(self,value):
        super(ListItem,self).__init__(str(value))
        self.value = value
        self.setFlags(self.flags()|qc.Qt.ItemFlag.ItemIsEditable)
        
    def data(self,role):
        if role == qc.Qt.ItemDataRole.DisplayRole:
            return str(self.value)
        elif role == qc.Qt.ItemDataRole.EditRole:
            return self.value.get_basename()
        elif role == qc.Qt.ItemDataRole.UserRole:
            return self.value
        else:
            return

    def setData(self,role,value):
        if role == qc.Qt.ItemDataRole.EditRole:
            self.value.set_basename(value)
            return True
        elif role == qc.Qt.ItemDataRole.UserRole:
            self.value = value
            return True
        else:
            return False        

class ListManager(qg.QWidget):
    def __init__(self,items,parent = None,name = None):
        super(ListManager,self).__init__(parent)
        
        self.items  = items
        
        self.itemlist = qg.QListWidget()
        self.refresh_list()
        
        layout = qg.QHBoxLayout()
            
        layout.addWidget(self.itemlist)
        self.layout2 = qg.QVBoxLayout()
        layout.addLayout(self.layout2)

        layout3 = qg.QVBoxLayout()
        layout3.setContentsMargins(0,0,0,0)
        if name!=None:
            layout3.addWidget(qg.QLabel(name))
        layout3.addLayout(layout)

#        self.setLayout(layout3)
#
#        self.loadbutton = qg.QPushButton('Load...')
#        self.newbutton = qg.QPushButton('New...')
#        self.editbutton = qg.QPushButton('Edit...')
##        self.insertbutton = qg.QPushButton('Insert..')
#        self.delete_button = qg.QPushButton('Delete')
#        self.save_button = qg.QPushButton('Save As...')
#        self.cleanup_button = qg.QPushButton('Cleanup')
#        self.copy_button = qg.QPushButton('Copy')
#        
#        self.delete_button.pressed.connect(self.remove_item)
#        self.save_button.pressed.connect(self.save_item)
#        self.copy_button.pressed.connect(self.copy_item)

        for widget in self.widgets():
            self.layout2.addWidget(widget)
        self.itemlist.setSelectionMode(self.itemlist.SelectionMode.SingleSelection)        
        self.itemlist.doubleClicked.connect(self.itemDoubleClicked)

    def buildButtonItem(self,name,method):
        button= qg.QPushButton('name')
        button.pressed.connect(method)
        return button

    def widgets(self):
        actions = []
        actions.append(('Save As...',self.save_item))
        actions.append(('Copy',self.copy_item))
#        actions.append(('Delete',self.remove_item))
        widgets = [self.buildButtonItem(*action) for action in actions] 
        return widgets
        
    def itemDoubleClicked(self,index):
#        userdata = self.model().data(index,qc.Qt.ItemDataRole.UserRole)
#        self.signal_edit.emit(userdata)        
        try: 
            self.edit_item()        
        except AttributeError:
            pass
        
    def remove_item(self):
        for item in self.itemlist.selectedItems():
            self.items.pop(item.value.id)
        self.refresh_list()

    def save_item(self):
        for item in self.itemlist.selectedItems():
            item.value.saveAs()
#        self.refresh_list()

    def copy_item(self):
        newitems = []
        for item in self.itemlist.selectedItems():
            newitem = item.value.copy(identical = False)
            newitem.regen_id()
            self.items[newitem.id] = newitem
        self.refresh_list(newitem)

    def refresh_list(self,lastselected = None):            
        self.itemlist.clear()
        [self.itemlist.addItem(ListItem(value)) for key,value in self.items.items()]
        for ii in range(self.itemlist.count()):
            item = self.itemlist.item(ii)
            item.setSelected(item.value == lastselected)
            
    def set_layout(self,cleanup_method = None,edit_method = None,new_method = None,load_method = None,copy = False, delete = False, saveas = False):
        if cleanup_method != None:
            def cleanup():
                cleanup_method()
                self.refresh_list()
            self.cleanup = cleanup

            self.cleanup_button.pressed.connect(cleanup)
            self.layout2.addWidget(self.cleanup_button)

        if new_method!=None:
            def new_item(*args,**kwargs):
                new_method(self.refresh_list)
            self.new_item = new_item
            
            self.newbutton.pressed.connect(new_item)
            self.layout2.addWidget(self.newbutton)

        if edit_method!=None:
            def edit_item(*args,**kwargs):
                for item in self.itemlist.selectedItems():
                    edit_method(item.value)
            self.edit_item  = edit_item

            self.editbutton.pressed.connect(edit_item)
            self.layout2.addWidget(self.editbutton)

        if load_method!=None:
            def load_item(*args,**kwargs):
                newitem = load_method()
                self.items[newitem.id] = newitem
                self.refresh_list(newitem)

            self.loadbutton.pressed.connect(load_item)
            self.layout2.addWidget(self.loadbutton)
            
        if saveas:
            self.layout2.addWidget(self.save_button)
        if copy:
            self.layout2.addWidget(self.copy_button)
        if delete:        
            self.layout2.addWidget(self.delete_button)
        self.layout2.addStretch()

class Dummy(object):
    pass

class SketchListManager(ListManager):
    def __init__(self,design,name='Sketch',**kwargs):
        self.design = design
        super(SketchListManager,self).__init__(design.sketches,name=name)
        
#        self.set_layout(edit_method = edit_method,new_method = new_method,load_method = Sketch.open,saveas = True,copy = True,**kwargs)

    def edit_method(sketch):
        for item in self.itemlist.selectedItems():
            item.value.edit(None,self.design,selectops = True)
        
    def new_method(refresh_method):
        def accept_method(sketch,*args):
            self.design.sketches[sketch.id] = sketch
            self.refresh_list(sketch)
        sketcher = Sketcher(None,Sketch(),self.design,accept_method = accept_method,selectops = True)
        sketcher.show()

    def widgets(self):
        actions = []
        actions.append(('New...',self.new_method))
        actions.append(('Edit...',self.edit_method))
        actions.append(('Load...',Sketch.open))
        widgets = [self.buildButtonItem(*action) for action in actions] 
        widgets.extend(super(SketchListManager,self).widgets())
        return widgets

class AdvancedSketchListManager(SketchListManager):
    def __init__(self,design):
#        super(AdvancedSketchListManager,self).__init__(design,name=None,cleanup_method = design.cleanup_sketches,delete = True)

    def widgets(self):
        actions = []
        actions.append(('Cleanup',self.design.cleanup_sketches))
        actions.append(('Delete',self.remove_item))
        widgets = [self.buildButtonItem(*action) for action in actions] 
        widgets.extend(super(AdvancedSketchListManager,self).widgets())
        return widgets
        
class DesignListManager(ListManager):
    def __init__(self,design,name='Sketch',**kwargs):
        from popupcad.filetypes.design import Design

        super(DesignListManager,self).__init__(design.subdesigns,name=name)
        self.set_layout(load_method = Design.open,saveas = True,copy = True,**kwargs)

class AdvancedDesignListManager(DesignListManager):
    def __init__(self,design):
        super(AdvancedDesignListManager,self).__init__(design,name=None,cleanup_method = design.cleanup_subdesigns,delete = True)

if __name__=='__main__':
    import sys
    app = qg.QApplication(sys.argv)
    dict1 = {'asdf':Dummy(),'xxx':Dummy()}
    lm = ListManager(dict1)
#    lm.button_layout1()
    lm.show()

#    sys.exit(app.exec_())        