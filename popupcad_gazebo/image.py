## @package image

"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

## @brief Contains some utility methods for handling images 

from __future__ import division

from random import random

from PIL import Image

from .enhanced_grid import *

## Converts a sequence of floats (ranged 0 to 1) to integers (ranged 0 to 155).
def int_sequence(seq):
    new_seq = []

    for element in seq:
        new_seq.append(int(255 * element))        

    return tuple(new_seq)

## Converts a sequence of integers (ranged 0 to 255) to floats (ranged 0 to 1).
def float_sequence(seq):
    new_seq = []

    for element in seq:
        new_seq.append(element / 255)

    return tuple(new_seq)

## Converts a 2D grid to an image on the disk. 
# The grid must contain float values (ranged 0 to 1).
def grid_to_rgb_image(grid, fname):
    image = Image.new('RGBA', grid.dims)
    pixels = image.load()

    for index in grid.index_iter():
        pixels[index] = int_sequence(grid[index])

    image.save(fname)   


## Converts a 2D grid to an image on the disk. 
# The grid must contain float values (ranged 0 to 1).
def grid_to_greyscale_image(grid, fname):
    image = Image.new('RGBA', grid.dims)
    pixels = image.load()

    for index in grid.index_iter():
        pixels[index] = int_sequence(grid[index])

    image = image.convert("LA")
    image.save(fname)   


## Loads an image from disk, and returns a tuplet of grids, one for each channel.
# The alpha channel is ignored.
def rgb_image_to_image_grid_channels(fname):
    image = Image.open(fname)
    pix = image.load()

    grids = (Grid2D(image.size, 0), Grid2D(image.size, 0), Grid2D(image.size, 0))

    for index in grids[0].index_iter():                
        grids[0][index] = pix[index][0] / 255
        grids[1][index] = pix[index][1] / 255
        grids[2][index] = pix[index][2] / 255

    return grids

## Converts a list of three grids into an RGB grid. The three grids each 
# represents a color channel, and should contain floating point values between 
# 0 and 1.
# The resulting grid contains tuples, each with four elements, between 0 and 1, 
# representing RGBA. Alpha is laways set to 1.
def channels_to_rgb_grid(grids):
    red_grid, green_grid, blue_grid = grids

    new_grid = Grid2D(red_grid.dims)

    for index in new_grid.index_iter():
        new_grid[index] = (red_grid[index], green_grid[index], blue_grid[index], 1)

    return new_grid

## Loads an image from disk into a grid.
def rgb_image_to_grid(fname):
    image = Image.open(fname)
    pix = image.load()

    grid = Grid2D(image.size, 0)

    for index in grid.index_iter():
        grid[index] = float_sequence(pix[index])

    return grid

## Take a grid containing non-negative integers, and makes a new grid with 
# elements from the pallet. If the old grid had an element 3 in a cell, then 
# the element in the corresponding cell in the new grid will hold the value of 
# the 4th element of the pallet.
def index_grid_to_rgb_grid(grid, pallet):
    new_grid = Grid2D(grid.dims)

    for index in new_grid.index_iter():
        new_grid[index] = pallet[grid[index]]                

    return new_grid

def transpose(grid):
    w, h = grid.dims
    new_grid = Grid2D((h, w))

    for index in grid.index_iter():
        x, y = index
        new_grid[y, x] = grid[index]

    return new_grid

## Converts a greyscale grid (every cell contains a float [0..1]) into an RGB 
# grid. The given color is multiplied by the value in the grid to give the value 
# of the corresponding cell in the new grid.
def greyscale_grid_to_rgb_grid(grid, color):
    red, green, blue, alpha = color

    new_grid = Grid2D(grid.dims, None)
    for index in grid.index_iter():
        value = grid[index]
        new_grid[index] = (value * red, value * green, value * blue, alpha)

    return new_grid

def rgb_grid_to_greyscale_grid(grid):
    new_grid = Grid2D(grid.dims, None)

    for index in grid.index_iter():
        red, green, blue, alpha = grid[index]
        new_grid[index] = (red + green + blue) / 3

    return new_grid

## An extremely simple edge detection algorithm.
def edge(grid):
    new_grid = Grid2D(grid.dims, (0, 0, 0, 1))

    for i in range(1, grid.dims[0]):
        for j in range(1, grid.dims[1]):
            red, green, blue, alpha = grid[i, j]
            red1, green1, blue1, alpha1 = grid[i - 1, j]
            red2, green2, blue2, alpha2 = grid[i, j - 1]
            red3, green3, blue3, alpha3 = grid[i - 1, j - 1]
            redd = abs(red - red1) + abs(red - red2) + abs(red - red3)
            greend = abs(green - green1) + abs(green - green2) + abs(green - green3)
            blued = abs(blue - blue1) + abs(blue - blue2) + abs(blue - blue3)

            avr = (redd + greend + blued)#/8

            new_grid[i, j] = (avr, avr, avr, 1)


    return new_grid

## Returns a grid in which the colours have been normalised.
# Colours are adjusted so that the returned grid has a minimum
# color component of 0, and a maximum component of 1.
def normalize(grid):
    max_lum = max(grid[0, 0])
    min_lum = min(grid[0, 0])       

    for cell in grid.cell_iter():
        red, green, blue, alpha = cell
        max_lum = max(red, green, blue, max_lum)
        min_lum = min(red, green, blue, min_lum)

    if max_lum == min_lum:
        multiplier = 1
        min_lum = 0
        max_lum = 0
    else:
        multiplier = 1 / (max_lum - min_lum)

    new_grid = Grid2D(grid.dims)

    for index in grid.index_iter():
        red, green, blue, alpha = grid[index]
        red = (red - min_lum) * multiplier
        green = (green - min_lum) * multiplier
        blue = (blue - min_lum) * multiplier

        new_grid[index] = (red, green, blue, alpha)

    return new_grid

## Returns a grid where all values have been normalised between 0 and 1.
def normalize_grey(grid):
    max_lum = grid[0, 0]
    min_lum = grid[0, 0]       

    for cell in grid.cell_iter():        
        max_lum = max(cell, max_lum)
        min_lum = min(cell, min_lum)

    if max_lum == min_lum:
        multiplier = 1
        min_lum = 0
        max_lum = 0
    else:
        multiplier = 1 / (max_lum - min_lum)

    new_grid = Grid2D(grid.dims)

    for index in grid.index_iter():
        new_grid[index] = (grid[index] - min_lum) * multiplier

    return new_grid

## Clamps all values in a grid between 0 and 1
def saturate(grid):
    new_grid = Grid2D(grid.dims)

    for index in grid.index_iter():
        new_grid[index] = max(min(grid[index], 1), 0)

    return new_grid

def threshold(grid, value):
    new_grid = Grid2D(grid.dims)

    for index in grid.index_iter():
        new_grid[index] = 1 if grid[index] >= value else 0

    return new_grid

## Multiplies all values of a grid with a constant. Returns the result as a new grid.
def multiply_grid(grid, factor):
    new_grid = Grid2D(grid.dims)

    for index in grid.index_iter():
        new_grid[index] = grid[index] * factor

    return new_grid

## Adss a constant to all values of a grid. Returns the result as a new grid.
def add_grid(grid, summand):
    new_grid = Grid2D(grid.dims)

    for index in grid.index_iter():
        new_grid[index] = grid[index] + summand

    return new_grid    

## Returns a grid that represents the entropy around the pixels in a given grid.
# The entropy around a pixel is measured as the sum of the absolute differences 
# between that pixel's channels and the surrounding pixels' corresponding channels.
#
# @param grid The grid to measure
#
# @param n Determines the size of the window around eaxh pixel to use. If n is 1, 
#        the window size is 3by3, if it is 2, the window size is 5 by 5.
def entropy(grid, n):
    new_grid = Grid2D(grid.dims, (0, 0, 0, 1))

    for index in grid.index_iter():
        red, green, blue, alpha = grid[index]
        red_sum, green_sum, blue_sum = 0, 0, 0

        for cell in grid.square_iter(index, n):
            red1, green1, blue1, alpha1 = cell
            red_sum += abs(red - red1)
            green_sum += abs(green - green1)
            blue_sum += abs(blue - blue1)

        new_grid[index] = (red_sum, green_sum, blue_sum, alpha)

    return new_grid

##@brief Returns a grid containing white noise in the range [0 1]
# @param dims
#       The dimensions of the grid to return (as a xy-tuple).
# @param period
#       This is the period of different noise samples. For example,
#       if the period is 2, then 2-by-2 windows in the grid will have
#       the same value.
def white_noise(dims, period=1):
    grid = Grid2D(dims)    
    width, height = dims

    for i in range(0, width, period):
        for j in range(0, height, period):
            r = random()            

            for index in grid.window_index_iter((i, j), (i + period, j+period)):
                grid[index] = r    

    return grid

## Interpolates a grey between two given greys.
# If t is set to 0, the returned grey is the same
# as col1. If t is set to 1, the returned grey
# is the same as col2.
def mix_grey(col1, col2, t):
    return col1 * (1 - t) + col2 * t

## Interpolates a color between two given colors.
# If t is set to 0, the returned grey is the same
# as col1. If t is set to 1, the returned grey
# is the same as col2.
def mix_color(color0, color1, t):  
    new_color = []

    for channel0, channel1 in zip(color0, color1):
        new_color.append(channel0 * (1 - t) + channel1 * t)

    return new_color

## Returns a new grid, containing m by n copies
# of the given grid.
def tile(grid, m, n):
    width, height = grid.dims
    dims = width * m, height * n

    new_grid = Grid2D(dims)

    for index in new_grid.index_iter():
        x, y, = index
        new_grid[index] = grid[x % width, y % height]

    return new_grid

## Adds weighted values of grids together.
def add_grey_grids(grids, factors = None):
    new_grid = Grid2D(grids[0].dims, 0)

    if factors == None:
        factors = [1] * len(grids)

    for grid, factor in zip(grids, factors):
        for index in grid.index_iter():
            new_grid[index] += grid[index] * factor

    return new_grid

## Calculates the integral grid of a grid.
def integrate(grid):
    new_grid = Grid2D(grid.dims, 0)

    new_grid[0, 0] = grid[0, 0]

    for i in xrange(1, grid.width):
        new_grid[i, 0] = new_grid[i-1, 0] + grid[i, 0]

    for j in xrange(1, grid.height):
        new_grid[0, j] = new_grid[i, j-1] + grid[0, j]

    for i in xrange(1, grid.width):                
        for j in xrange(1, grid.height):
            new_grid[i, j] = new_grid[i-1, j] + new_grid[i, j-1] - new_grid[i-1, j-1] + grid[i, j]

    return new_grid

def integrate_vertically(grid):
    w, h = grid.dims
    new_grid = Grid2D((w, h), 0)

    for i in range(w):
        new_grid[i, 0] = grid[i, 0]

    for i in range(w):
        for j in range(1, h):
            new_grid[i, j] = grid[i, j] + new_grid[i, j - 1]

    return new_grid

def blend(grid1, grid2, blend_image):
    dims = blend_image.dims

    grid = Grid2D(dims)

    for index in grid.index_iter():
        grid[index] = mix_color(grid1[index], grid2[index], blend_image[index])

    return grid


