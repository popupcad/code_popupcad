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

try:
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
except ImportError:
    pass

class Vertex(popupcad.geometry.vertex.ShapeVertex):
    pass
popupcad.geometry.vertex.Vertex =Vertex

popupcad.materials.laminatesheet = popupcad.filetypes.laminate
sys.modules['popupcad.materials.laminatesheet']  = popupcad.filetypes.laminate
popupcad.filetypes.laminate.Layer = popupcad.filetypes.layer.Layer

popupcad.geometry.genericpolygon= popupcad.filetypes.genericshapes
sys.modules['popupcad.geometry.genericpolygon']  = popupcad.filetypes.genericshapes
popupcad.filetypes.genericshapes.GenericShape = genericpolygon.GenericShape

popupcad.geometry.genericshapebase= popupcad.filetypes.genericshapebase
sys.modules['popupcad.geometry.genericshapebase']  = popupcad.filetypes.genericshapebase

popupcad.materials.LayerDef = popupcad.filetypes.layerdef.LayerDef
popupcad.materials.materials.LayerDef = popupcad.filetypes.layerdef.LayerDef
