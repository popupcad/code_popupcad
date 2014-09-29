# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
#import popupcad
import types
import sys

from . import manufacturingplugin
from . import identifybodies
from . import identifyrigidbodies
from . import customsupport3
from . import supportcandidate3
from . import toolclearance2
from . import autoweb3
from . import keepout2
from . import outersheet2
from . import removability
from . import scrapoperation

def initialize(editor,design):
    manufacturingplugin.ManufacturingPlugin(editor,design)