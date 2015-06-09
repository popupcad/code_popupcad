# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from dev_tools.genericfile import GenericFile,FileMissing
import PySide.QtGui as qg

class popupCADFile(GenericFile):
    @classmethod
    def get_parent_program_name(self):
        return popupcad.program_name
    @classmethod
    def get_parent_program_version(self):
        return popupcad.version
    @classmethod
    def load_safe(cls,filepathin,suggestions = None,openmethod = None,**openmethodkwargs):
        import os
        pathin,filenamein = os.path.split(filepathin)

        if suggestions == None:
            suggestions = []

        suggestions.append(pathin)        
        suggestions.append('.')
        suggestions.append(cls.lastdir())
        suggestions.append(popupcad.designdir)
        
        for path in suggestions:
            try:
                filepath = os.path.normpath(os.path.join(path,filenamein))
                if openmethod==None:
                    design = cls.load_yaml(filepath)
                else:
                    design = openmethod(filepath,**openmethodkwargs)
                return filepath, design
            except IOError:
                pass
                
        msgbox = qg.QMessageBox()
        msgbox.setText('Cannot Find File')
        msgbox.setInformativeText('Select a new File?')
        msgbox.setDetailedText(filenamein)
        msgbox.setIcon(msgbox.Icon.Warning)
        msgbox.setStandardButtons(msgbox.StandardButton.Cancel | msgbox.StandardButton.Open)
        msgbox.setDefaultButton(msgbox.StandardButton.Open)
        ret = msgbox.exec_()

        if ret == msgbox.Cancel:
            raise(FileMissing(filenamein))
        if ret == msgbox.Open:
            return cls.open_filename()    