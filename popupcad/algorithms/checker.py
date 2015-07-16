# -*- coding: utf-8 -*-
"""
Created on Tue May 19 17:23:14 2015

@author: danaukes
"""
import sys
import popupcad
import yaml
from dev_tools.process_manager import ProcessData

class LoadException(Exception):
    pass
class SaveLoadException(Exception):
    pass
class ReprocessException(Exception):
    pass
class Error1(Exception):
    pass
class UpgradeException(Exception):
    pass

class Checker(ProcessData):
    def __init__(self,filename,try_deprecated = True,try_upgrade = True):
        super(Checker,self).__init__()
        self.filename = filename
        self.try_deprecated = try_deprecated
#        self.try_test_yaml = try_test_yaml
#        self.try_reprocess = try_reprocess
        self.try_upgrade = try_upgrade
        self.result = ''
    def run(self):
        try:
            try:
                d = popupcad.filetypes.design.Design.load_yaml(self.filename)
                self.result = 'loaded'
            except:
                if self.try_deprecated:
                    import popupcad_deprecated
                    popupcad.deprecated = popupcad_deprecated
                    sys.modules['popupcad.deprecated'] = popupcad_deprecated
                    try:
                        d = popupcad.filetypes.design.Design.load_yaml(self.filename)
                        self.result = 'loaded w/ dependencies'
                    except:
                        self.result = 'load failed'
                        raise LoadException()
                else:
                    self.result = 'load failed'
                    raise LoadException()

            if self.try_upgrade:
                try:
                    d = d.upgrade()
                    self.result += ', upgrade passed'
                except:
                    self.result += ', upgrade failed'
                    raise UpgradeException()

#            if self.try_reprocess:
#                try:
#                    self.result += ', compile passed'
#                    d.reprocessoperations()
#                except:
#                    self.result += ', compile failed'
#                    raise ReprocessException()
            try:
                d = d.copy()
                self.f = yaml.dump(d)
            except Exception as ex:
                print(ex)

        except LoadException:
            pass
        except SaveLoadException:
            pass
        except ReprocessException:
            pass
        except UpgradeException:
            pass
                
class Checker2(ProcessData):
    def __init__(self,checker1,try_reprocess = True,ignore_compile_fail = True):
        self.checker1 = checker1
        self.try_reprocess = try_reprocess
        self.ignore_compile_fail = ignore_compile_fail
        self.filename = self.checker1.filename
        self.result = ''
    def run(self):
        try:
            try:
                d = yaml.load(self.checker1.f)
                self.result = self.checker1.result+', reload passed'
            except AttributeError:
                self.result = self.checker1.result+', reload failed'
                raise Error1()
            except:
                self.result = self.checker1.result+', reload failed'
                raise LoadException()

            if self.try_reprocess:
                try:
                    d.reprocessoperations()
                    self.result += ', compile passed'
                except:
                    if self.ignore_compile_fail:
                        self.d = d
                    self.result += ', compile failed'
                    raise ReprocessException()
            self.d = d                
        except LoadException:
            pass
        except SaveLoadException:
            pass
        except ReprocessException:
            pass
        except Error1:
            pass
        