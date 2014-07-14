# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import PySide.QtCore as qc
import PySide.QtGui as qg

def build_sketchlist(design):
    from popupcad.filetypes.sketch import Sketch
    from popupcad.guis.sketcher import Sketcher

    widget = ListManager(design.sketches)
    def edit_method(sketch):
        sketch.edit(None,design,selectops = True)
    def new_method(refresh_method):
        def accept_method2(sketch,*args):
            design.sketches[sketch.id] = sketch
            refresh_method(sketch)
        sketcher = Sketcher(None,Sketch(),design,accept_method = accept_method2,selectops = True)
        sketcher.show()
    
    widget.set_layout(edit_method = edit_method,new_method = new_method,load_method = Sketch.open,saveas = True,copy = True)
    return widget

def build_subdesignslist(design):
    from popupcad.filetypes.design import Design
    widget = ListManager(design.subdesigns)
    widget.set_layout(load_method = Design.open,saveas = True,copy = True)
    return widget


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
    def __init__(self,items,parent = None):
        super(ListManager,self).__init__(parent)
        
        self.items  = items
        
        self.itemlist = qg.QListWidget()
        self.refresh_list()
        
        layout = qg.QHBoxLayout()
        layout.addWidget(self.itemlist)
        self.layout2 = qg.QVBoxLayout()
        layout.addLayout(self.layout2)
        self.setLayout(layout)

        self.loadbutton = qg.QPushButton('Load...')
        self.newbutton = qg.QPushButton('New...')
        self.editbutton = qg.QPushButton('Edit...')
        self.insertbutton = qg.QPushButton('Insert..')
        self.delete_button = qg.QPushButton('Delete')
        self.save_button = qg.QPushButton('Save As...')
        self.cleanup_button = qg.QPushButton('Cleanup')
        self.copy_button = qg.QPushButton('Copy')
        
        self.delete_button.pressed.connect(self.remove_item)
        self.save_button.pressed.connect(self.save_item)
        self.copy_button.pressed.connect(self.copy_item)
        
        self.itemlist.setSelectionMode(self.itemlist.SelectionMode.SingleSelection)        
        self.itemlist.doubleClicked.connect(self.itemDoubleClicked)

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

if __name__=='__main__':
    import sys
    app = qg.QApplication(sys.argv)
    dict1 = {'asdf':Dummy(),'xxx':Dummy()}
    lm = ListManager(dict1)
#    lm.button_layout1()
    lm.show()

#    sys.exit(app.exec_())        