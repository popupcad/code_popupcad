# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from . import genericpolygon

#from popupcad.deprecated.genericpolygon import GenericShape
import popupcad
import types
import sys

popupcad.genericpolygon.GenericShape = genericpolygon.GenericShape
