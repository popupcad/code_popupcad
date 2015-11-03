# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
import popupcad
from dev_tools.genericfile import GenericFile

class popupCADFile(GenericFile):

    @classmethod
    def get_parent_program_name(self):
        return popupcad.program_name

    @classmethod
    def get_parent_program_version(self):
        return popupcad.version

    def backup(self,folder = None,backupstring = '_backup_'):
        import os
        import glob
        import popupcad
        
        if folder is None:
            folder = self.dirname
        basename = self.get_basename()
        filename = os.path.normpath(os.path.join(folder,basename))
        filename = os.path.splitext(filename)[0]

        searchstring = (filename+backupstring+'*.'+self.defaultfiletype)
        existingfiles = glob.glob(searchstring)
        existingfiles.sort(reverse=True)

        for item in existingfiles[popupcad.backup_limit-1:]:
            os.remove(item)
        
        time = popupcad.basic_functions.return_formatted_time(specificity = 'minute')
        
        backupfilename = filename+backupstring+time+'.'+self.defaultfiletype
            
        self.save_yaml(backupfilename, update_filename=False)
