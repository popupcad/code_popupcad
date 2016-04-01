# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
from popupcad.filetypes.laminate import Laminate
import popupcad


def modify_device(
        device,
        support_sketch,
        support_width,
        support_out,
        holes_radius,
        cut_width):
    '''from a user-input support sketch, modify a device to be compatible with the given support design.'''
    layers = device.layerdef.layers
    support_out1 = device.buffer(support_out)
    support_out2 = support_out1.difference(device)
    support_width = support_sketch.buffer(support_width / 2)
    support_pieces = support_width.intersection(support_out2)

    holes_1 = support_pieces.buffer(holes_radius)
    holes_2 = holes_1.unarylayeroperation('union', layers, layers)
    holes = holes_2.difference(holes_1.buffer(1e-3 * popupcad.csg_processing_scaling))
    device_with_holes = device.difference(holes)

    cut_width = support_sketch.buffer(cut_width / 2)
    cuts_1 = cut_width.intersection(support_out2)
    cuts_2 = cuts_1.unarylayeroperation('union', layers, layers)
#    cuts_3 = cuts_2.difference(cuts_1)
#    cuts= cuts_3.unarylayeroperation('union',layers,layers)

# return the support, the cuts which will remove the support from the
# device, and the modified device
    return device_with_holes, support_width, cuts_2
