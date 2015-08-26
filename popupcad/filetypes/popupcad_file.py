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

