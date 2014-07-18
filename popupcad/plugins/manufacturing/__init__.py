# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 17:26:23 2014

@author: danaukes
"""
import popupcad
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
#from . import cutop2
#popupcad.manufacturing.AutoWeb3 = autoweb3.AutoWeb3
#popupcad.manufacturing.autoweb3 = autoweb3

popupcad.manufacturing.identifybodies  = identifybodies
sys.modules['popupcad.manufacturing.identifybodies']  = identifybodies

popupcad.manufacturing.identifyrigidbodies  = identifyrigidbodies
sys.modules['popupcad.manufacturing.identifyrigidbodies']  = identifyrigidbodies

popupcad.manufacturing.customsupport3  = customsupport3
sys.modules['popupcad.manufacturing.customsupport3']  = customsupport3

popupcad.manufacturing.supportcandidate3  = supportcandidate3
sys.modules['popupcad.manufacturing.supportcandidate3']  = supportcandidate3

popupcad.manufacturing.toolclearance2  = toolclearance2
sys.modules['popupcad.manufacturing.toolclearance2']  = toolclearance2

popupcad.manufacturing.autoweb3  = autoweb3
sys.modules['popupcad.manufacturing.autoweb3']  = autoweb3

popupcad.manufacturing.keepout2  = keepout2
sys.modules['popupcad.manufacturing.keepout2']  = keepout2

popupcad.manufacturing.outersheet2  = outersheet2
sys.modules['popupcad.manufacturing.outersheet2']  = outersheet2

popupcad.manufacturing.removability  = removability
sys.modules['popupcad.manufacturing.removability']  = removability
