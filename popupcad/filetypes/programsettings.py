# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 13:46:27 2014

@author: danaukes
"""

from popupcad.filetypes.genericfile import GenericFile,popupCADFile

class ProgramSettings(popupCADFile):
    filetypes = {'popupcad':'CAD Design'}
    defaultfiletype = 'popupcad'
    filters,filterstring,selectedfilter = GenericFile.buildfilters(filetypes,defaultfiletype)

    display = ['inkscape_path','pstoedit_path','nominal_width','nominal_height']
    editable = ['inkscape_path','pstoedit_path','nominal_width','nominal_height']
    
    def __init__(self):
        self.inkscape_path = 'C:\Program Files (x86)\Inkscape\inkscape.exe'
        self.pstoedit_path = 'C:\Program Files\pstoedit\pstoedit.exe'
        self.toolbar_icon_size = 36
        self.id = id(self)
        self.nominal_width = 1024
        self.nominal_height = 768
    def copy(self,identical = True):
        new = type(self)()
        new.inkscape_path = self.inkscape_path
        new.pstoedit_path = self.pstoedit_path
        new.toolbar_icon_size = self.toolbar_icon_size
        new.nominal_width=self.nominal_width
        new.nominal_height=self.nominal_height
        
        if identical:
            new.id = self.id
        return new
        
        