# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

def enum(**enums):
    e = type('Enum', (), enums)
    e.dict = enums
    return  e
