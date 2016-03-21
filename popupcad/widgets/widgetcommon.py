# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


import qt.QtCore as qc
import qt.QtGui as qg
import popupcad

class WidgetBasic(object):
    def sizeHint(self):
        buffer_x = 14
        buffer_y = 36
        return qc.QSize(popupcad.nominal_width - buffer_x, popupcad.nominal_height - buffer_y)    
            
    def set_nominal_size(self):
        #        buffer_x=14
        #        buffer_y=36
        #        self.resize(popupcad.nominal_width-buffer_x,popupcad.nominal_height-buffer_y)
        pass

    def move_center(self):
        screen_width = qg.QApplication.desktop().screen().width()
        screen_height = qg.QApplication.desktop().screen().height()
      
        new_pos_x = (screen_width - self.width())/2
        new_pos_y = (screen_height - self.height())/2

        self.move(new_pos_x,new_pos_y)            

    @staticmethod
    def builddialog(widget):
        layout = qg.QVBoxLayout()
        layout.addWidget(widget)

        dialog = qg.QDialog()
        dialog.setLayout(layout)
        dialog.setModal(True)
        return dialog

    def action_uncheck(self, action_to_uncheck):
        action_to_uncheck.setChecked(False)
        
class MainGui(WidgetBasic):        
    def create_menu_system(self,filename):
        import yaml
        with open(filename) as f:
            self.menu_system = yaml.load(f)
        self.setMenuBar(qg.QMenuBar())    
        self.loaded_menu_systems=[]
        self.load_menu_system(self.menu_system)
        
    def load_menu_system(self,menu_system):
        self.loaded_menu_systems.append(menu_system)
        menu_system.build(self)
        menu_bar = self.menuBar()
        [menu_bar.addMenu(item) for item in menu_system.main_menu]
        [self.addToolBar(qc.Qt.ToolBarArea.TopToolBarArea, toolbar) for toolbar in menu_system.toolbars]


