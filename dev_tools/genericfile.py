# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt
import qt.QtCore as qc
import qt.QtGui as qg
import os

class FileMissing(Exception):

    def __init__(self, filename):
        super(FileMissing,self).__init__('Child File Missing:{filename}'.format(filename=filename))

class NoFileName(Exception):
    def __init__(self):
        super(NoFileName,self).__init__('No Filename')
    
class GenericFile(object):
    defaultfiletype = 'file'
    _lastdir = '.'

    def __init__(self):
        self.id = id(self)
        self.set_basename(self.genbasename())
    @property
    def my_filename(self):
        try:
            return self._filename
        except AttributeError:
            raise NoFileName()
            
    @my_filename.setter
    def my_filename(self,filename):
        self._filename = os.path.normpath(filename)
    @property
    def my_local_name(self):
        return os.path.split(self.filename)[1]
    @property
    def my_directory(self):
        return os.path.split(self.filename)[0]
    @property
    def my_base_name(self):
        return os.path.splitext(self.my_local_name)[0]
    @property
    def my_extension(self):
        return os.path.splitext(self.my_local_name)[1]

    def get_basename(self):
        try:
            return self._basename
        except AttributeError:
            self._basename = self.genbasename()
            return self._basename

    def copy(self, identical=True):
        new = type(self)()
        self.copy_file_params(new, identical)
        return new

    def upgrade(self, *args, **kwargs):
        return self

    @classmethod
    def lastdir(cls):
        return cls._lastdir

    @classmethod
    def setlastdir(cls, directory):
        cls._lastdir = directory

    @classmethod
    def get_parent_program_name(self):
        return None

    @classmethod
    def get_parent_program_version(self):
        return None

    def copy_file_params(self, new, identical):
        try:
            new.dirname = self.dirname
        except AttributeError:
            pass

        try:
            if identical:
                new.set_basename(self.get_basename())
            else:
                new.set_basename(new.genbasename())
        except AttributeError:
            pass

        try:
            new.parent_program_name = self.parent_program_name
        except AttributeError:
            pass
        try:
            new.parent_program_version = self.parent_program_version
        except AttributeError:
            pass

        return new

    def genbasename(self):
        basename = str(self.id) + '.' + self.defaultfiletype
        return basename

    def set_basename(self, basename):
        self._basename = basename

#    @classmethod
    def updatefilename(self, filename):
        import os
        self.dirname, self._basename = os.path.split(filename)
        self.setlastdir(self.dirname)

    @classmethod
    def load_yaml(cls, filename):
        import yaml
        with open(filename, 'r') as f:
            obj1 = yaml.load(f)
        obj1.updatefilename(filename)
        return obj1

    @classmethod
    def open_filename(cls, parent=None, openmethod=None, **openmethodkwargs):
        if qt.loaded == 'PySide':
            filename, selectedfilter = qg.QFileDialog.getOpenFileName(parent, 'Open', cls.lastdir(), filter=cls.file_filter, selectedFilter=cls.selected_filter)
        else:
            filename = qg.QFileDialog.getOpenFileName(parent, 'Open', cls.lastdir(), filter=cls.file_filter)
        if filename:
            if openmethod is None:
                object1 = cls.load_yaml(filename)
            else:
                object1 = openmethod(filename, **openmethodkwargs)
            return filename, object1
        else:
            return None, None

    @classmethod
    def open(cls, *args, **kwargs):
        filename, object1 = cls.open_filename(*args, **kwargs)
        return object1

    def save(self, parent=None):
        try:
            return self.save_yaml(self.filename())
        except NoFileName:
            return self.saveAs(parent)

    def regen_id(self):
        import random
        self.id = int(random.randint(0, 9999999999))

    def saveAs(self, parent=None):
        import os
        try:
            tempfilename = self.filename()
        except NoFileName:
            tempfilename = os.path.normpath(os.path.join(self.lastdir(),self.get_basename()))

        if qt.loaded == 'PySide':
            filename, selectedfilter = qg.QFileDialog.getSaveFileName(parent, "Save As", tempfilename, filter=self.file_filter, selectedFilter=self.selected_filter)
        else:
            filename = qg.QFileDialog.getSaveFileName(parent, "Save As", tempfilename, filter=self.file_filter)
        if not filename:
            return False
        else:
            self.regen_id()
            return self.save_yaml(filename,identical=False)

    def filename(self):
        try:
            return os.path.normpath(os.path.join(self.dirname,self.get_basename()))
        except AttributeError:
            raise NoFileName()

    def save_yaml(self, filename, identical=True, update_filename=True):
        import yaml
        if update_filename:
            self.updatefilename(filename)
        self.parent_program_name = self.get_parent_program_name()
        self.parent_program_version = self.get_parent_program_version()
        new = self.copy(identical)
        with open(filename, 'w') as f:
            yaml.dump(new, f)
        return True

    def __str__(self):
        return self.get_basename()

    def __repr__(self):
        return str(self)

    def copy_yaml(self, identical=True):
        import yaml
        new = yaml.load(yaml.dump(self.copy(identical)))
        return new

    @staticmethod
    def slugify(string):
        string = string.replace('_','-')
        string = string.replace(' ','-')
        string = string.lower()
        return string        