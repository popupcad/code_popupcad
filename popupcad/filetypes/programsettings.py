# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from popupcad.filetypes.popupcad_file import popupCADFile

class ProgramSettings(popupCADFile):
    filetypes = {'popupcad':'CAD Design'}
    defaultfiletype = 'popupcad'

#    display = ['*']
    editable = ['*']
    hidden = ['filetypes','filters','filterstring','defaultfiletype','selectedfilter','id']
#    display = ['inkscape_path','pstoedit_path','nominal_width','nominal_height']
#    editable = ['inkscape_path','pstoedit_path','nominal_width','nominal_height']
    
    def __init__(self):
        super(ProgramSettings,self).__init__()
        
        self.inkscape_path = 'C:\Program Files (x86)\Inkscape\inkscape.exe'
        self.pstoedit_path = 'C:\Program Files\pstoedit\pstoedit.exe'
        self.toolbar_icon_size = 36
        self.id = id(self)
        self.nominal_width = 1024
        self.nominal_height = 768
#        self.deprecated_mode = False

    def copy(self,identical = True):
        new = type(self)()
        new.inkscape_path = self.inkscape_path
        new.pstoedit_path = self.pstoedit_path
        new.toolbar_icon_size = self.toolbar_icon_size
        new.nominal_width=self.nominal_width
        new.nominal_height=self.nominal_height
#        new.deprecated_mode=self.deprecated_mode
        if identical:
            new.id = self.id
        return new
        
