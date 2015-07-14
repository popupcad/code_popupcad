## @package gradient 
# Functions for handling colour gradients.

from math import floor
from enhanced_grid import Grid2D
from image import mix_color

## A gradient without any interpolation.
class DiscreteGradient:
  def __init__(self, colors):
    self.colors = []
    
    for color in colors:
      self.colors.append(color)
    
    self.color_count = len(colors)  
    
  def get_color(self, t): #assumes 0 <= t < 1
    col_index = int(floor(t * self.color_count))
    
    if (col_index >= self.color_count):
      col_index = self.color_count - 1
      
    return self.colors[col_index]

## A gradient between two colours with linear interpolation.    
class SimpleGradient:
  def __init__(self, color0, color1):
    self.color0 = color0
    self.color1 = color1
    
  def get_color(self, t):
    return mix_color(self.color0, self.color1, t)

## Maps a gradient to a grid, and returns the result as a new grid.
# @grid A grid containing values in the range [0 1]
def map_gradient(gradient, grid):
  color_grid = Grid2D(grid.dims)
  
  for index in grid.index_iter():
    color_grid[index] = gradient.get_color(grid[index])
    
  return color_grid
