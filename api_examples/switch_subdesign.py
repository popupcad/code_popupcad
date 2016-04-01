# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import sys
import popupcad

import qt.QtCore as qc
import qt.QtGui as qg
if __name__=='__main__':
    
    app = qg.QApplication(sys.argv[0])
    
    filename_from = 'C:/Users/danaukes/Dropbox/zhis sentinal 11 files/modified/sentinal 11 manufacturing_R08.cad'
    filename_to = 'C:/Users/danaukes/Dropbox/zhis sentinal 11 files/modified/sentinal 11 manufacturing_R09.cad'
    
    d = popupcad.filetypes.design.Design.load_yaml(filename_from)
    
    widget = qg.QDialog()
    layout = qg.QVBoxLayout()
    layout1 = qg.QHBoxLayout()
    layout2 = qg.QHBoxLayout()
    list1 = qg.QListWidget()
    list2 = qg.QListWidget()
    button_ok = qg.QPushButton('Ok')
    button_cancel = qg.QPushButton('Cancel')
    
    subdesign_list = list(d.subdesigns.values())
    
    for item in subdesign_list:
        list1.addItem(str(item))
        list2.addItem(str(item))
        
    layout1.addWidget(list1)
    layout1.addWidget(list2)
    layout2.addWidget(button_ok)
    layout2.addWidget(button_cancel)
    layout.addLayout(layout1)
    layout.addLayout(layout2)
    widget.setLayout(layout)
    button_ok.pressed.connect(widget.accept)
    button_cancel.pressed.connect(widget.reject)
    
    if widget.exec_():
        if len(list1.selectedIndexes())==1 and len(list2.selectedIndexes())==1:
            ii_from = list1.selectedIndexes()[0].row()    
            ii_to = list2.selectedIndexes()[0].row()    
            print(ii_from,ii_to)
            
            d.replace_subdesign_refs(subdesign_list[ii_from].id,subdesign_list[ii_to].id)
            d.subdesigns.pop(subdesign_list[ii_from].id)
            d.save_yaml(filename_to)
        
    sys.exit(app.exec_())