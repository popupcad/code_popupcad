# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:23:52 2015

@author: danaukes
"""

import PySide.QtGui as qg
import PySide.QtCore as qc
import sys
import glob
import os
import shutil
import dev_tools.process_manager as pm

from popupcad.algorithms.checker import Checker,Checker2
            
class Widget(qg.QWidget):
    max_processes = 2
    def __init__(self,*args,**kwargs):
        super(Widget,self).__init__(*args,**kwargs)
        main_layout = qg.QVBoxLayout()
        
        self.directory_name = qg.QLineEdit()
        self.directory_button = qg.QPushButton('...')
        self.recursive = qg.QCheckBox('recursive')    

        sublayout1 = qg.QHBoxLayout()
        sublayout1.addWidget(self.directory_name)
        sublayout1.addWidget(self.recursive)
        sublayout1.addWidget(self.directory_button)

        self.file_list = qg.QListWidget()
        self.file_list.setSelectionBehavior(self.file_list.SelectionBehavior.SelectRows)
        self.file_list.setSelectionMode(self.file_list.SelectionMode.ExtendedSelection)
        
        self.file_list_result = qg.QTableWidget()
        self.file_list_result.setRowCount(0)
        self.file_list_result.setColumnCount(2)
        self.file_list_result.setShowGrid(False)
        self.file_list_result.setAlternatingRowColors(True)
        self.file_list_result.setHorizontalHeaderLabels(['file','result'])
        self.file_list_result.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_list_result.setSelectionBehavior(self.file_list_result.SelectionBehavior.SelectRows)
        self.file_list_result.setSelectionMode(self.file_list_result.SelectionMode.ExtendedSelection)
        self.file_list_result.horizontalHeader().setStretchLastSection(True)     

        sublayout2 = qg.QHBoxLayout()
        self.deprecated = qg.QCheckBox('deprecated')   
        self.upgrade = qg.QCheckBox('upgrade')   
        self.reprocess = qg.QCheckBox('test compile')    
        self.ignore_compile_fail = qg.QCheckBox('ignore compile fail')    
        
        self.check_button = qg.QPushButton('check files')
        sublayout2.addWidget(self.deprecated)
        sublayout2.addWidget(self.upgrade)
        sublayout2.addWidget(self.reprocess)
        sublayout2.addWidget(self.ignore_compile_fail)
        sublayout2.addStretch()
        sublayout2.addWidget(self.check_button)

        self.directory_name1 = qg.QLineEdit()
        self.directory_button1 = qg.QPushButton('...')
        self.move_dead_files_button= qg.QPushButton('move dead files')
        self.save_button= qg.QPushButton('save passed files')
        sublayout7 = qg.QHBoxLayout()
        sublayout7.addWidget(self.directory_name1)
        sublayout7.addWidget(self.directory_button1)
        sublayout7.addWidget(self.move_dead_files_button)
        sublayout7.addWidget(self.save_button)
        
        self.directory_name2 = qg.QLineEdit()
        self.directory_button2 = qg.QPushButton('...')
        self.build_docs_button= qg.QPushButton('build documentation')
        sublayout8 = qg.QHBoxLayout()
        sublayout8.addWidget(self.directory_name2)
        sublayout8.addWidget(self.directory_button2)
        sublayout8.addWidget(self.build_docs_button)

        main_layout.addLayout(sublayout1)
        main_layout.addWidget(self.file_list)
        main_layout.addLayout(sublayout2)
        main_layout.addWidget(self.file_list_result)
        main_layout.addLayout(sublayout7)
        main_layout.addLayout(sublayout8)
        
        self.setLayout(main_layout)
        
        self.directory_button.clicked.connect(self.select_directory)
        self.check_button.clicked.connect(self.check_files)  
        self.save_button.clicked.connect(self.save_files)  
        self.directory_button1.clicked.connect(self.select_directory1)
        self.move_dead_files_button.clicked.connect(self.move_dead_files)

        self.directory_button2.clicked.connect(self.select_directory2)
        self.build_docs_button.clicked.connect(self.build_docs)

        self.clear_results1()
        self.recursive.setChecked(True)
        self.deprecated.setChecked(True)
        self.upgrade.setChecked(True)
        self.reprocess.setChecked(True)
        self.ignore_compile_fail.setChecked(True)

        self.load_directory('C:\\Users\\danaukes\\popupCAD_files\\designs')
        self.load_directory1('C:\\users\\danaukes\\desktop\\failures')
        self.load_directory2('C:\\users\\danaukes\\desktop\\documentation')

    def sizeHint(self):
        return qc.QSize(800,600)
        
    def move_dead_files(self):
        path = self.directory_name1.text()
        if not os.path.exists(path):
            os.mkdir(path)
        for item in self.results1:
            try:
                item.d
            except AttributeError:
                shutil.move(item.filename,path)
    
    def select_directory(self):
        path = qg.QFileDialog.getExistingDirectory(self,'',self.directory_name.text())
        if path!='':
            self.load_directory(path)

    def load_directory(self,path):
        self.directory_name.setText(path)
        self.clear_results1()
        if not self.recursive.isChecked():
            searchpath = os.path.normpath(os.path.join(path,'*.cad'))
            files = glob.glob(searchpath)
        else:
            files = []
            for dirname, dirnames, filenames in os.walk(path):
                filenames2 = glob.glob(os.path.normpath(os.path.join(dirname,'*.cad')))
                files.extend(filenames2)
        files.sort()
        for item in files:
            self.file_list.addItem(qg.QListWidgetItem(item))
        self.results0 = files

    def select_directory1(self):
        path = qg.QFileDialog.getExistingDirectory(self,'',self.directory_name1.text())
        if path!='':
            self.load_directory1(path)

    def load_directory1(self,path):
        self.directory_name1.setText(path)
        
    def select_directory2(self):
        path = qg.QFileDialog.getExistingDirectory(self,'',self.directory_name2.text())
        if path!='':
            self.load_directory2(path)

    def load_directory2(self,path):
        self.directory_name2.setText(path)

    def check_files(self):
        self.show_results1()
        self.clear_results2()
        items = self.file_list.selectedItems()
        items = [item.data(qc.Qt.ItemDataRole.DisplayRole) for item in items]
        try_deprecated = self.deprecated.isChecked()
        try_reprocess = self.reprocess.isChecked()
        try_upgrade = self.upgrade.isChecked()
        ignore_compile_fail = self.ignore_compile_fail.isChecked()
        processes = [Checker(item,try_deprecated=try_deprecated,try_upgrade=try_upgrade) for item in items]
        process_manager = pm.ProcessManager(processes,max_processes=self.max_processes,debug = True)
        process_manager.run()

        processes2 = [Checker2(item,try_reprocess=try_reprocess,ignore_compile_fail = ignore_compile_fail) for item in process_manager.data]
        process_manager = pm.ProcessManager(processes2,max_processes=self.max_processes,debug = True)
        process_manager.run()
        
        self.clear_results2()
        f = lambda i:i.filename
        data = process_manager.data.copy()
        data.sort(key = f)
        self.results1 = data
        self.newresults(data)
        
    def newresults(self,items):
        for item in items:
            ii = self.file_list_result.rowCount()
            self.file_list_result.setRowCount(ii+1)
            a = (qg.QTableWidgetItem(os.path.split(item.filename)[1]))
            b = (qg.QTableWidgetItem(item.result))
            self.file_list_result.setItem(ii,0,a)
            self.file_list_result.setItem(ii,1,b)
            self.file_list_result.resizeColumnsToContents()
        
    def save_files(self):
        for item in self.results1:
            try:
                item.d.save_yaml(item.filename)
            except AttributeError:
                pass
                
    def clear_results1(self):
        self.file_list.clear()
        self.results0 = []
        self.clear_results2()

    def clear_results2(self):
        self.file_list_result.clear()
        for ii in range(self.file_list_result.rowCount()):
            self.file_list_result.removeRow(0)
        self.results1 = []
        
    def show_results1(self):
#        self.file_list_result.show()
        pass

    def build_docs(self):
        path = self.directory_name2.text()
        if not os.path.exists(path):
            os.mkdir(path)
        
        for item in self.results1:
            try:
                item.d.build_documentation(path)
            except AttributeError:
                pass
    
if __name__ == "__main__":
    app = qg.QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())