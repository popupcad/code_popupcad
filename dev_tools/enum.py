# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


def enum(**enums):
    e = type('Enum', (), enums)
    e.dict = enums
    return e
