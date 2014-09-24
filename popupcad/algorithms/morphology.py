# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 19:57:44 2014

@author: danb0b
"""

def cleanup(ls1,value,resolution):
    closing = ls1.buffer(-value,resolution = resolution)
    opening = closing.buffer(2*value,resolution = resolution)
    closing2 = opening.buffer(-value,resolution = resolution)
    return closing2
