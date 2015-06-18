# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""


class UserData(object):
    name = 'UserData'

    def __init__(self, customname=''):
        self.setcustomname(customname)

    def __str__(self):
        return self.buildviewdata()

    def __repr__(self):
        return self.buildviewdata()

    def edit(self, *args, **kwargs):
        print('edited')

    def setcustomname(self, name):
        self.customname = name

    def getcustomname(self):
        return self.customname

    def buildviewdata(self):
        if self.customname == '':
            return self.name
        else:
            return self.customname + '(' + self.name + ')'
