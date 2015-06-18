# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.laminate import Laminate
import popupcad.materials.materials as mat


def one_way_up(laminatein):
    l = Layer([])
    laminateout = Laminate(laminatein.layerdef)
    for ii, geoms in enumerate(laminatein):
        l = l.union(geoms)
        laminateout[ii] = l
    laminateout = modify_up(laminateout)
    return laminateout


def one_way_down(laminatein):
    return one_way_up(laminatein.flip()).flip()


def two_way(laminatein):
    layers = laminatein.layerdef.layers
    laminateout = laminatein.unarylayeroperation('union', layers, layers)
    return laminateout


def modify_up(removabilityin):
    layers = removabilityin.layerdef.layers
    for layer1, layer2 in zip(layers[:-1], layers[1:]):
        if isinstance(
                layer1,
                mat.Adhesive) or isinstance(
                layer2,
                mat.Adhesive):
            removabilityin.layer_sequence[layer1] = removabilityin.layer_sequence[
                layer1].union(removabilityin.layer_sequence[layer2])
    return removabilityin


def generate_removable_scrap(device, sheet, tol=1e-5, device_buffer=0):
    #    scrap = sheet.difference(device)
    #    smaller_scrap = scrap.buffer(-tol)
    removability_up = one_way_up(device)
    removability_down = one_way_down(device)
    removability_both = two_way(device)
    not_removable_region = (
        removability_up.cleanup(tol)).intersection(
        removability_down.cleanup(tol))
    not_removable_scrap_region = not_removable_region.difference(
        device.cleanup(tol))
    not_removable_scrap_region = not_removable_region.cleanup(tol)

    if device_buffer > 0:
        buffered_device = device.buffer(device_buffer)
    else:
        buffered_device = device
    all_scrap = sheet.difference(buffered_device)
    removable_scrap = all_scrap.difference(
        not_removable_scrap_region.buffer(tol))
    two_way_scrap = removable_scrap.difference(removability_both.buffer(tol))
    directionally_removable_scrap = removable_scrap.difference(
        two_way_scrap.buffer(tol))
    up_scrap = directionally_removable_scrap.intersection(
        removability_up.buffer(-tol))
    down_scrap = directionally_removable_scrap.intersection(
        removability_down.buffer(-tol))
    return two_way_scrap, up_scrap.buffer(-tol), down_scrap.buffer(-tol)


def more_removable_mod(bleed, device, sheet, tol=1e-5):
    two_way_scrap, up_scrap, down_scrap = generate_removable_scrap(
        device, sheet, tol)
    up_bleed = two_way((up_scrap.buffer(bleed)).intersection(two_way_scrap))
    down_bleed = two_way(
        (down_scrap.buffer(bleed)).intersection(two_way_scrap))
    up_bleed = up_bleed.difference(down_bleed.buffer(tol))
    down_bleed = down_bleed.difference(up_bleed.buffer(tol))
    two_way_scrap_mod = two_way_scrap.difference(
        up_bleed).difference(down_bleed)
    up_scrap_mod = up_scrap.union(up_bleed.buffer(tol))
    down_scrap_mod = down_scrap.union(down_bleed.buffer(tol))
    return two_way_scrap_mod, up_scrap_mod, down_scrap_mod
