# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""


class ClassTools(object):

    def copyattrs(self, source, names):
        for name in names:
            setattr(self, name, getattr(source, name))

    def copyvalues(self, *args, **kwargs):
        self.copyattrs(*args, **kwargs)

    def copyclasses(self, source, names, function):
        for name in names:
            classin = getattr(source, name)
            classout = function(classin)
            setattr(self, name, classout)

    def init_copy(self, arglist, kwarglist):
        args = [getattr(self, name) for name in arglist]
        kwargs = dict([(name, getattr(self, name)) for name in kwarglist])
        return type(self)(*args, **kwargs)
