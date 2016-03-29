# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


def cleanup(ls1, value, resolution):
    closing = ls1.buffer(-value, resolution=resolution)
    opening = closing.buffer(2 * value, resolution=resolution)
    closing2 = opening.buffer(-value, resolution=resolution)
    return closing2


def simplify(ls1, value):
    closing = ls1.simplify(value)
    return closing
