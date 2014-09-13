# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import popupcad
import types
import sys

from . import genericpolygon
from . import placeop4
from . import placeop5
from . import placeop6
from . import sketchoperation
from . import cutop
from . import customsupport2

popupcad.geometry.genericpolygon.GenericShape = genericpolygon.GenericShape

popupcad.manufacturing.placeop4  = placeop4
popupcad.manufacturing.placeop5  = placeop5
popupcad.manufacturing.placeop6  = placeop6
popupcad.manufacturing.sketchoperation  = sketchoperation
popupcad.manufacturing.cutop  = cutop
popupcad.manufacturing.customsupport2  = customsupport2

sys.modules['popupcad.manufacturing.placeop4']  = placeop4
sys.modules['popupcad.manufacturing.placeop5']  = placeop5
sys.modules['popupcad.manufacturing.placeop6']  = placeop6
sys.modules['popupcad.manufacturing.sketchoperation']  = sketchoperation
sys.modules['popupcad.manufacturing.cutop']  = cutop
sys.modules['popupcad.manufacturing.customsupport2']  = customsupport2


import popupcad_manufacturing_plugins
popupcad.manufacturing.identifybodies  = popupcad_manufacturing_plugins.manufacturing.identifybodies
popupcad.manufacturing.identifyrigidbodies  = popupcad_manufacturing_plugins.manufacturing.identifyrigidbodies
popupcad.manufacturing.customsupport3  = popupcad_manufacturing_plugins.manufacturing.customsupport3
popupcad.manufacturing.supportcandidate3  = popupcad_manufacturing_plugins.manufacturing.supportcandidate3
popupcad.manufacturing.toolclearance2  = popupcad_manufacturing_plugins.manufacturing.toolclearance2
popupcad.manufacturing.autoweb3  = popupcad_manufacturing_plugins.manufacturing.autoweb3
popupcad.manufacturing.keepout2  = popupcad_manufacturing_plugins.manufacturing.keepout2
popupcad.manufacturing.outersheet2  = popupcad_manufacturing_plugins.manufacturing.outersheet2
popupcad.manufacturing.removability  = popupcad_manufacturing_plugins.manufacturing.removability

sys.modules['popupcad.manufacturing.identifybodies']  = popupcad_manufacturing_plugins.manufacturing.identifybodies
sys.modules['popupcad.manufacturing.identifyrigidbodies']  = popupcad_manufacturing_plugins.manufacturing.identifyrigidbodies
sys.modules['popupcad.manufacturing.customsupport3']  = popupcad_manufacturing_plugins.manufacturing.customsupport3
sys.modules['popupcad.manufacturing.supportcandidate3']  = popupcad_manufacturing_plugins.manufacturing.supportcandidate3
sys.modules['popupcad.manufacturing.toolclearance2']  = popupcad_manufacturing_plugins.manufacturing.toolclearance2
sys.modules['popupcad.manufacturing.autoweb3']  = popupcad_manufacturing_plugins.manufacturing.autoweb3
sys.modules['popupcad.manufacturing.keepout2']  = popupcad_manufacturing_plugins.manufacturing.keepout2
sys.modules['popupcad.manufacturing.outersheet2']  = popupcad_manufacturing_plugins.manufacturing.outersheet2
sys.modules['popupcad.manufacturing.removability']  = popupcad_manufacturing_plugins.manufacturing.removability

popupcad.plugins = popupcad_manufacturing_plugins
sys.modules['popupcad.plugins']  = popupcad_manufacturing_plugins

#popupcad.plugins.manufacturing = popupcad_manufacturing_plugins.manufacturing
#sys.modules['popupcad.plugins.manufacturing']  = popupcad_manufacturing_plugins.manufacturing
#popupcad.plugins.algorithms = popupcad_manufacturing_plugins.algorithms
#sys.modules['popupcad.plugins.algorithms']  = popupcad_manufacturing_plugins.algorithms
#
#popupcad.plugins.manufacturing.identifybodies  = popupcad_manufacturing_plugins.identifybodies
#sys.modules['popupcad.plugins.manufacturing.identifybodies']  = popupcad_manufacturing_plugins.identifybodies
#
#popupcad.plugins.manufacturing.identifyrigidbodies  = popupcad_manufacturing_plugins.identifyrigidbodies
#sys.modules['popupcad.plugins.manufacturing.identifyrigidbodies']  = popupcad_manufacturing_plugins.identifyrigidbodies
#
#popupcad.plugins.manufacturing.customsupport3  = popupcad_manufacturing_plugins.customsupport3
#sys.modules['popupcad.plugins.manufacturing.customsupport3']  = popupcad_manufacturing_plugins.customsupport3
#
#popupcad.plugins.manufacturing.supportcandidate3  = popupcad_manufacturing_plugins.supportcandidate3
#sys.modules['popupcad.plugins.manufacturing.supportcandidate3']  = popupcad_manufacturing_plugins.supportcandidate3
#
#popupcad.plugins.manufacturing.toolclearance2  = popupcad_manufacturing_plugins.toolclearance2
#sys.modules['popupcad.plugins.manufacturing.toolclearance2']  = popupcad_manufacturing_plugins.toolclearance2
#
#popupcad.plugins.manufacturing.autoweb3  = popupcad_manufacturing_plugins.autoweb3
#sys.modules['popupcad.plugins.manufacturing.autoweb3']  = popupcad_manufacturing_plugins.autoweb3
#
#popupcad.plugins.manufacturing.keepout2  = popupcad_manufacturing_plugins.keepout2
#sys.modules['popupcad.plugins.manufacturing.keepout2']  = popupcad_manufacturing_plugins.keepout2
#
#popupcad.plugins.manufacturing.outersheet2  = popupcad_manufacturing_plugins.outersheet2
#sys.modules['popupcad.plugins.manufacturing.outersheet2']  = popupcad_manufacturing_plugins.outersheet2
#
#popupcad.plugins.manufacturing.removability  = popupcad_manufacturing_plugins.removability
#sys.modules['popupcad.plugins.manufacturing.removability']  = popupcad_manufacturing_plugins.removability