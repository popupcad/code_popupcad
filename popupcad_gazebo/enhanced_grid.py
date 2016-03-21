## @package enhanced_grid 

"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

## @brief Contains 2D and 3D Grid containers that supports extended slicing syntax.
## 
# These classes are provided for rapid prototyping, the methods defined on them might be slow.
# @code
# grid1 = Grid3D(10, 10, 10, 0)
# grid2 = Grid3D(10, 10, 10, 1)
# grid1[0, 0, 0] = grid2[0, 0, 0]
# grid1[0, 0, 2:6:2] = grid2[0, 0, 4:5]
# grid1[0, 0, ...] = grid2[0, 0, ...]
# grid1[0, ..., 0] = grid2[..., 0, 0]
# grid1[..., ..., ...] = grid2[..., ...., ....]
# @endcode
#
# Slicing does not copy elements - an auxiliary window container is created that delegates 
# further operations to the underlying container.
# Note that assignments to slices from the same object might not behave as espected. 
# Parallel assignment also does not always work as expected.
# For example:
#@code
# grid[..., 0], grid[..., 1] = grid[..., 1], grid[..., 0]
#@endcode
# does not correctly swop two rows, but the following does:
#@code
# grid[..., 0], grid[..., 1] = grid[..., 1].clone(), grid[..., 0].clone()
#@endcode
#Strictly speaking, it is necessary only to clone the one object,
#but it is hard to remember which, so it is better to clone both (?).
# 
#@todo Implement a way to use copy containers instead of window containers

from __future__ import division
from random import randint
from math import floor
from math import ceil
from array import array

##@brief A class that works just like a queue or a stack, except
## that a randomly selected element is returned. 
##
# This class is useful for implementing algorithms that gather 
# elements, and need to process them randomly. Something along the 
# lines of:
# 
# @code
# while not rqueue.empty():
#   #generates 3 new elements to process
#   for i in range(3): 
#     rqueue.push(process(rqueue.pop())) 
# @endcode
class RandomQueue:
	## Constructs a new empty RandomQueue
	def __init__(self):		
		## The internal list to store objects.
		self.array = []

	##Returns True if this RandomQueue is empty.	
	def empty(self):
		return len(self.array) <= 0

	## Push a new element into the RandomQueue.
	def push(self, x):
		self.array.append(x)

	## @brief Pops a randomly selected element from the queue. 
	##
	# All elements can be selected equiprobably
	def pop(self):
		n = len(self.array)

		if n <= 0:
			raise IndexError('Cannot pop from emty container!')
		elif n == 1:
			return self.array.pop()
		else:
			i = randint(0, n - 1)
			j = n - 1
			self.array[i], self.array[j] = 	self.array[j], self.array[i]

		return self.array.pop()

## @brief Class that represents a 2D array. 
##
# The following convenient syntax is supported:
# @code
# p = 2, 3 # a coordinate in the grid
# grid[p] = 5
# print grid[p] 
# print grid[2, 3] 
# @endcode
#

def signum(x):
	if x > 0:
		return 1
	elif x < 0:
		return -1
	else:
		return 0

## Truncates a point to integer coordinates.
def int_point_2d(p):
	x, y = p
	return int(x), int(y)

## Truncates a point to integer coordinates.
def int_point_3d(p):
	x, y, z = p
	return int(x), int(y), int(z)

# Every point in the sample set is represented with 
# a 1 in th grid; all other points are represented with 0.
# The returned grid is usefull for producing image data.
def points_to_grid(points, dimensions):
	grid = Grid2D(dimensions, 0)

	for point in points:
		grid[int_point_2d(point)] = 1

	return grid

## Converts a list of points to a 3D grid. 

# Every point in the sample set is represented with 
# a 1 in th grid; all other points are represented with 0.
# The returned grid is usefull for producing image data.
def points_to_grid_3d(points, dimensions):
	grid = Grid3D(dimensions, 0)

	for point in points:
		grid[int_point_3d(point)] = 1

	return grid

def make_grid_1d(width, initial_item=None):
	grid = [initial_item] * width

	return grid

## @brief Makes 2 list of lists.
def make_grid_2d(width, height, initial_item=None):
	grid = [None] * width

	for i in xrange(width):
		grid[i] = [None] * height

		for j in xrange(height):
			grid[i][j] = initial_item

	return grid

## @brief Makes 2 list of lists.
def make_grid_3d(width, height, depth, initial_item):
	grid = [None] * width

	for i in xrange(width):
		grid[i] = [None] * height

		for j in xrange(height):
			grid[i][j] = [None] * depth

			for k in xrange(depth):
				grid[i][j][k] = initial_item

	return grid

## @brief Returns an xrange that can be used to iterate over 
## the slice of the container.
#
# The following snippets are equivalent
#@code
# s = slice(3, 18, 3)
# for i in srange(s):
#	print list[i]
#@endcode
#
#@code
# for item in list[s]:
#	print item
#@endcode
def srange(s, length):
	if s == Ellipsis:
		return xrange(length)
	else:
		b, e, s = s.indices(length)
		return xrange(b, e, s)

## @brief Returns true if s is a slice or an Ellipsis.
def is_slice(s):
	return type(s) is slice or s == Ellipsis

## @brief Returns the number of elements this slice will return, provided the provided 
## primary is large enough.
def slice_len(s, length):
	if s == Ellipsis:
		return length

	b, e, s, = s.indices(length)

	tmp = int(ceil((e - b) / s))

	if tmp < 0:
		return 0
	else:
		return min(tmp, length)

	if s.stop > s.start and s.step > 0:
		return (s.stop - s.start) // s.step
	elif s.stop < s.start and s.step < 0:
		return (s.start - s.stop) // -s.step
	else:
		return 0

## @brief Returns a slice that is equivalent to the two slices combined.
##
# The following snippets are equivalent:
#@code
# list[s1][s2]
#@endcode

#@code
# list[slice_mul(s1, s2)]
#@endcode
def slice_mul(slice1, slice2, length):
	if type(slice2) is int:
		if type(slice1) is type(Ellipsis):
			return slice2
		b1, e1, s1 = slice1.indices(length)
		s2 = slice2
		if s2 < 0:
			s2 += length
		if s2 < 0:
			s2 = 0		
		return b1 + s2*s1
	elif type(slice2) is slice:
		if type(slice1) is type(Ellipsis):
			return slice2
		else:
			b1, e1, s1 = slice1.indices(length)
			b2, e2, s2 = slice2.indices(length)			
			b = b1 + b2*s1
			s = s1*s2
			e = min(b1 + e2*s1, e1)

			if e < 0 and s < 0:
				return slice(b, None, s)
			else:
				return slice(b, e,  s)



			b = slice1.start + slice2.start*slice1.step
			s = slice1.step*slice2.step
			return slice(b, min(slice1.start + slice2.stop*slice1.step, slice1.stop), s)
	elif slice2 == Ellipsis:
		return slice1

## @brief Completes this slice for a given length.
##
# The resulting slice will give the same elements for a container of the given length, but
# none of the start, stop, or step attributes will be None. If s is the Ellipses, then 
# the slice (0, length, 1) is returned.
# @deprecated
def complete_slice(s, length):
	return s

## @brief Sub-classes of this container can be used directly.
##
## A principle container will do assignment on a 1D point.
## Assignment of larger chunks is delegated to the AuxilaryContainer
## with the right dimensions.
##
## The enherritance is merely for documentation purposes.
class PrincipleContainer:
	pass

## @brief Sub-classes of this container is used as windows by a
##PrincipleContainer, and should not be used directly!
##
## An AuxiliaryContainer will do assignment a chunk with the same 
## dimensionality as itself, otherwise it delegates it to the underlying
## principle container, which will, in turn, construct the correct 
## AuxiliaryContainer to perform the assignment, or perform it if it is 
## a 1D point.
##
## The enherritance is merely for documentation purposes.
class AuxiliaryContainer:
	pass

##Abstract super class of all grid-like containers.
##These containers are static, that is, once they are created, 
##their dimensions cannot change.
#
# Children of this class must implement
# the attribute __clonetype__, which must 
# hold a callable type that can be constructed
# for clones.
# 
# Children must also implement the iterators
# cell_iter() and index_iter().
class Container:
	##
	##
	# @param dim
	#		The dimensions of this grid
	def __init__(self, dims):
		self.dims = dims

		count = 1

		for dim in dims:
			count *= dim

		self.count = count

	##Test whether two containers have the same dimensions
	##and the same items at equal indices.
	def __eq__(self, other):
		if other == None:
			return False
		if self.dims != other.dims:
			return False

		for cell1, cell2 in zip(self.cell_iter(), other.cell_iter()):
			if cell1 != cell2:
				return False
		return True

	##Equivalent to @code not (self == other) @endcode .
	def __ne__(self, other):
		return not (self == other)

	## Returns the length (1D) or width (nD) of this container.
	#
	# The length of a container is defined such that the length behaves as it would
	# for a list of lists.
	def __len__(self):
		return self.dims[0]

	## @brief Returns the minimum and maximum elements
	## of this grid as a tuple. 
	##
	#This method assumes the grid is filled.
	def min_max(self):		
		cell_iter = self.cell_iter()		
		min = max = cell_iter.next()

		for cell in cell_iter:
			if cell > max:
				max = cell
			elif cell < min:
				min = cell
		return min, max

	def copy_from(self, other):
		for index in self.index_iter():
			self[index] = other[index]

	##Makes a shallow copy of this container.
	#
	#This method constructs an instance of
	#this instance's __clonetype__. In general,
	#if this class is an AuxiliaryContainer,
	#the clone will be a PrincipleContainer
	#of the same dimension.
	def clone(self):
		new_grid = self.__clonetype__(self.dims)		
		new_grid.copy_from(self)

		return new_grid

## Class that implements __str__ and __iter__.
class Container1D (Container):
	def __init__(self, length):
		Container.__init__(self, (length,))
		self.length = length
		self.__clonetype__ = Grid1D

	def __str__(self):    
		#slow...
		glst = []

		for i in xrange(self.length):
			glst.append(self[i])

		return glst.__repr__()

	def __iter__(self):
		for i in xrange(self.length):
			yield self[i]
		raise StopIteration

	## @brief Returns the same iterator as __iter__.
	#
	# Provided so that all containers have consistent cell_iter methods.
	def cell_iter(self):
		return self.__iter__()

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iteratir will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	# The iterator does not iterate outside the grid.	
	def window_iter(self, x1, x0):
		for i in xrange(max(0, x0), min(x1, self.length)):
			yield self[i]
		raise StopIteration

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iteratir will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_window_iter(self, x1, x0):
		for i in xrange(x0, x1):
			yield self[i % self.length]
		raise StopIteration

	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	def square_iter(self, x, n):
		return self.window_iter(x - n, x + n + 1)

	def wrapped_square_iter(self, x, n):
		return self.wrapped_window_iter(x - n, x + n + 1)

	## @brief Returns an iterator that iterates over the indeces of this 
	## container.
	##
	# If grid is a 2 by 2 grid, then:
	# @code
	# for p in index_iter(grid):
	# 	print p
	# @endcode
	# will produce 
	# @code
	# 0, 0
	# 0, 1
	# 1, 0
	# 1, 1
	# @endcode
	# This iterator is useful for assigning elements of grids:
	# @code
	# for p in index_iter(grid):
	# 	grid[p] = random()
	# @endcode
	def index_iter(self):
		for i in xrange(self.length):
			yield i
		raise StopIteration

## Class that implements __str__ and __iter__.
class Container2D (Container):
	def __init__(self, width, height):
		Container.__init__(self, (width, height))
		self.width = width
		self.height = height
		self.__clonetype__ = Grid2D

	def __str__(self):    
		#slow...
		glst = []

		for i in xrange(self.width):
			gcol = []

			for j in xrange(self.height):
				gcol.append(self[i, j])

			glst.append(gcol)

		return glst.__repr__()	

	## @brief Returns an iterator that iterates over columns.
	##
	# This iterator is provided so that a Grid2D better emulates a list of 
	# lists, as in the following example:
	#@code
	# 	for col in grid:
	#		for item in col:
	#			process(item)
	#@endcode
	# Use of this iterator is discouraged - it is slow
	def __iter__(self):
		for i in xrange(self.width):
			yield self[i, ...]
		raise StopIteration

	## @brief Returns an iterator that iterates over all cells in the grid.
	##
	# This allows you to write:
	#@code
	# for cell in cell_iter(grid):
	#   process(cell)
	#@endcode
	def cell_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				yield self[i, j]
		raise StopIteration

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	#	
	def window_index_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1    
		for i in xrange(max(0, x0), min(x1, self.width)):
			for j in xrange(max(0, y0), min(y1, self.height)):
				yield (i, j)
		raise StopIteration
	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	#	
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return the index of the 
	# first cell in that row.
	def wrapped_window_index_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1    
		for i in xrange(x0, x1):
			for j in xrange(y0, y1):
				yield (i % self.width, j % self.height)
		raise StopIteration

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode	
	def window_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1
		for i in xrange(max(0, x0), min(x1, self.width)):
			for j in xrange(max(0, y0), min(y1, self.height)):
				yield self[i, j]
		raise StopIteration	

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	#	
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_window_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1
		for i in xrange(x0, x1):
			for j in xrange(y0, y1):
				yield self[i % self.width, j % self.height]
		raise StopIteration	

	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	def square_index_iter(self, p, n):
		x, y = p
		return self.window_index_iter((x - n, y - n), (x + n + 1, y + n +1))
	
	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_square_index_iter(self, p, n):
		x, y = p
		return self.wrapped_window_index_iter((x - n, y - n), (x + n + 1, y + n +1))


	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	def square_iter(self, p, n):
		x, y = p
		return self.window_iter((x - n, y - n), (x + n + 1, y + n +1))

	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_square_iter(self, p, n):
		x, y = p
		return self.wrapped_window_iter((x - n, y - n), (x + n + 1, y + n +1))

	## @brief Returns an iterator that iterates over the indeces of this 
	## grid as tuples.
	##
	# If grid is a 2 by 2 grid, then:
	# @code
	# for p in index_iter(grid):
	# 	print p
	# @endcode
	# will produce 
	# @code
	# 0, 0
	# 0, 1
	# 1, 0
	# 1, 1
	# @endcode
	# This iterator is useful for assigning elements of grids:
	# @code
	# for p in index_iter(grid):
	# 	grid[p] = random()
	# @endcode
	def index_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				yield i, j
		raise StopIteration

## Class that implements __str__ and __iter__.
class Container3D (Container):
	def __init__(self, width, height, depth):
		Container.__init__(self, (width, height, depth))
		self.width = width
		self.height = height
		self.depth = depth

		self.__clonetype__ = Grid3D

	def __str__(self):    
		#slow...
		glst = []

		for i in xrange(self.width):
			gcol = []
			for j in xrange(self.height):
				gslice = []

				for k in xrange(self.depth):
					gslice.append(self[i, j, k])

				gcol.append(gslice)
			glst.append(gcol)

		return glst.__repr__()

	def __iter__(self):
		for i in xrange(self.width):
			yield self[i, ..., ...]
		raise StopIteration

	## Returns an iterator that iterates over all cells in the grid
	def cell_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				for k in xrange(self.depth):
					yield self[i, j, k]
		raise StopIteration

	## @brief Returns an iterator that iterates over the indeces of this 
	## grid as tuples.
	##
	# If grid is a 2 by 2 grid, then:
	# @code
	# for p in index_iter(grid):
	# 	print p
	# @endcode
	# will produce 
	# @code
	# 0, 0
	# 0, 1
	# 1, 0
	# 1, 1
	# @endcode
	# This iterator is useful for assigning elements of grids:
	# @code
	# for p in index_iter(grid):
	# 	grid[p] = random()
	# @endcode
	def index_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				for k in xrange (self.depth):
					yield i, j, k
		raise StopIteration	

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y, z in the grid
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	# z0 <= z < z1
	#@endcode
	#
	def window_iter(self, p0, p1):
		x0, y0, z0 = p0
		x1, y1, z1 = p1

		for i in xrange(max(0, x0), min(x1, self.width)):
			for j in xrange(max(0, y0), min(y1, self.height)):
				for k in xrange(max(0, z0), min(z1, self.depth)):
					yield self[i, j, k]
		raise StopIteration

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y, z in the grid
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	# z0 <= z < z1
	#@endcode
	#wrapping around the edges as necessary.
	
	def wrapped_window_iter(self, p0, p1):
		x0, y0, z0 = p0
		x1, y1, z1 = p1

		for i in xrange(x0, x1):
			for j in xrange(y0, y1):
				for k in xrange(z0, z1):
					yield self[i % self.width, j % self.height, k % self.depth]
		raise StopIteration
	## @brief Returns an iterator that iterates over all cells in the square
	##	surrounding the given point. 
	##
	#The cube is 2*n + 1 units.
	def square_iter(self, p, n):
		x, y, z = p
		return self.window_iter(
			(x - n, y - n, z - n), 
			(x + n + 1, y + n +1, z + n +1))
	## @brief Returns an iterator that iterates over all cells in the square
	##	surrounding the given point, wrapping around as necessary.
	##
	#The cube is 2*n + 1 units.
	def wrapped_square_iter(self, p, n):
		x, y, z = p
		return self.wrapped_window_iter(
			(x - n, y - n, z - n), 
			(x + n + 1, y + n +1, z + n +1))

class GridWindow1D (Container1D, AuxiliaryContainer): #Constant y
	def __init__(self, grid, col_slice):
		self.grid = grid
		self.x = complete_slice(col_slice, grid.width)		
		Container1D.__init__(self, slice_len(self.x), grid.width)

	def __getitem__(self, x):
		new_x = slice_mul(self.x, x, self.grid.width)

		return self.grid[new_x]		

	def __setitem__(self, x, item):
		new_x = slice_mul(self.x, x, self.grid.width)

		if type(x) is int:
			self.grid[new_x] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				self.grid[i] = item_i

## Class that represent a 2D grid, with enhanced slicing notation.
class Grid1D (Container1D, PrincipleContainer):
	def __init__(self, dims, initial_item = None):
		(width,) = dims
		Container1D.__init__(self, width)
		self.grid = make_grid_1d(width, initial_item)
		self.width = width
	## @brief Returns an iterator that iterates over all cells in the grid.
	##
	# This allows you to write:
	#@code
	# for cell in cell_iter(grid):
	#   process(cell)
	#@endcode
	def cell_iter(self):
		for i in xrange(self.width):
			yield self.grid[i]
		raise StopIteration

	def __getitem__(self, x):
		if isinstance(x, int):
			return self.grid[x]
		elif is_slice(x):
			GridWindow1D(self, x)
		raise TypeError

	def __setitem__(self, x, item):		
		if type(x) is int:			
			self.grid[x] = item
		elif is_slice(x):
			g = GridWindow1D(self, x)
			g[...] = item
		else:
			raise TypeError

class GridRow2D (Container1D, AuxiliaryContainer): #Constant y
	def __init__(self, grid, col_slice, row):
		self.grid = grid
		self.x = complete_slice(col_slice, grid.width)
		self.y = row

		Container1D.__init__(self, slice_len(self.x, grid.width))

	def __getitem__(self, x):
		new_x = slice_mul(self.x, x, self.grid.width)

		return self.grid[new_x, self.y]		

	def __setitem__(self, x, item):
		new_x = slice_mul(self.x, x, self.grid.width)

		if type(x) is int:
			self.grid[new_x] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				self.grid[i, self.y] = item_i

class GridCol2D (Container1D, AuxiliaryContainer): #Constant x
	def __init__(self, grid, col, row_slice):
		self.grid = grid
		self.x = col
		self.y = complete_slice(row_slice, grid.height)

		Container1D.__init__(self, slice_len(self.y, grid.height))

	def __getitem__(self,  y):
		new_y = slice_mul(self.y, y, self.grid.height)

		return self.grid[self.x, new_y]

	def __setitem__(self, y, item):
		new_y = slice_mul(self.y, y, self.grid.height)

		if type(y) is int:			
			self.grid[self.x, new_y] = item
		else: #slice!
			for i, item_i in zip(srange(new_y, self.grid.height), item):
				self.grid[self.x, i] = item_i

class GridWindow2D (Container2D):
	def __init__(self, grid, x, y):
		self.grid = grid
		self.x = complete_slice(x, grid.width)
		self.y = complete_slice(y, grid.height)

		Container2D.__init__(self, slice_len(self.x, grid.width), slice_len(self.y, grid.height))

	def __getitem__(self, p):
		if isinstance(p, int):
			return self[p, ...]			
		x, y = p			

		new_x = slice_mul(self.x, x, self.grid.width)
		new_y = slice_mul(self.y, y, self.grid.height)
		return self.grid[new_x, new_y]

	def __setitem__(self, p, item):
		if isinstance(p, int):
			self[p, ...] = item
		x, y = p
		new_x = slice_mul(self.x, x, self.grid.width)
		new_y = slice_mul(self.y, y, self.grid.height)

		if type(x) is int or type(y) is int:
			#delegate!			
			self.grid[new_x, new_y] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				for j, item_j in zip(srange(new_y, self.grid.height), item_i):
					self.grid[i, j] = item_j

	def __repr__(self):    
		#slow...
		glst = []

		for i in xrange(slice_len(self.x, self.grid.width)):
			gcol = []
			for j in xrange(slice_len(self.y, self.grid.height)):
				gcol.append(self[i, j])
			glst.append(gcol)

		return glst.__repr__()			

## Class that represent a 2D grid, with enhanced slicing notation.
class Grid2D (Container2D, PrincipleContainer):

	def __init__(self, dims, initial_item = None):
		(width, height) = dims
		Container2D.__init__(self, width, height)
		self.grid = make_grid_2d(width, height, initial_item)
	## @brief Returns an iterator that iterates over all cells in the grid.
	##
	# This allows you to write:
	#@code
	# for cell in cell_iter(grid):
	#   process(cell)
	#@endcode
	def cell_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				yield self.grid[i][j]
		raise StopIteration

	def __getitem__(self, p):
		if isinstance(p, int):
			return self[p, ...]
		x, y = p
		if isinstance(x, int):
			if isinstance(y, int):
				return self.grid[x][y]
			elif is_slice(y):
				return GridCol2D(self, x, y)
		elif is_slice(x):
			if isinstance(y, int):
				return GridRow2D(self, x, y)
			elif is_slice(y):
				return GridWindow2D(self, x, y)

		raise TypeError

	def __setitem__(self, p, item):		
		x, y = p
		if type(x) is int:
			if type(y) is int:
				self.grid[x][y] = item
			elif is_slice(y):
				g = GridCol2D(self, x, y)
				g[...] = item
		elif is_slice(x):
			if type(y) is int:
				g = GridRow2D(self, x, y)
				g[...] = item
			elif is_slice(y):
				g = GridWindow2D(self, x, y)
				g[..., ...] = item
		else:
			raise TypeError

class GridBar3D (Container1D, AuxiliaryContainer): #constant x, y
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = x
		self.y = y
		self.z = complete_slice(z, grid.depth)

		Container1D.__init__(self, slice_len(self.z, grid.depth))

	def __getitem__(self,  z):
		new_z = slice_mul(self.z, z, self.grid.depth)		
		return self.grid[self.x, self.y, new_z]

	def __setitem__(self, z, item):
		new_z = slice_mul(self.z, z, self.grid.depth)

		if type(z) is int:
			self.grid[new_z] = item
		else: #slice!
			for i, item_i in zip(srange(new_z, self.grid.depth), item):
				self.grid[self.x, self.y, i] = item_i	

class GridCol3D (Container1D, AuxiliaryContainer): #constant x, z
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = x
		self.y = complete_slice(y, grid.height)
		self.z = z

		Container1D.__init__(self, slice_len(self.y, grid.height))

	def __getitem__(self,  y):
		new_y = slice_mul(self.y, y, self.grid.height)		
		return self.grid[self.x, new_y, self.z]
	def __setitem__(self, y, item):
		new_y = slice_mul(self.y, y, self.grid.height)

		if type(y) is int:
			self.grid[new_y] = item
		else: #slice!
			for i, item_i in zip(srange(new_y, self.grid.height), item):
				self.grid[self.x, i, self.z] = item_i	

class GridRow3D (Container1D, AuxiliaryContainer): #constant y, z
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = complete_slice(x, grid.width)
		self.y = y
		self.z = z

		Container1D.__init__(self, slice_len(self.x, grid.width))
	def __getitem__(self,  x):
		new_x = slice_mul(self.x, x, self.grid.width)		
		return self.grid[new_x, self.y, self.z]
	def __setitem__(self, x, item):
		new_x = slice_mul(self.x, x, self.grid.width)

		if type(x) is int:
			self.grid[new_x] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				self.grid[i, self.y, self.y] = item_i

class GridSliceXY (Container2D, AuxiliaryContainer): #constant z
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = complete_slice(x, grid.width)
		self.y = complete_slice(y, grid.height)
		self.z = z		
		Container2D.__init__(self, slice_len(self.x, grid.width), slice_len(self.y, grid.height))
	def __getitem__(self,  p):
		if isinstance(p, int):
			return self[p, ...]			
		x, y = p	
		new_x = slice_mul(self.x, x, self.grid.width)		
		new_y = slice_mul(self.y, y, self.grid.height)
		return self.grid[new_x, new_y, self.z]

	def __setitem__(self, p, item):
		if isinstance(p, int):
			self[p, ...] = item
		x, y = p	
		new_x = slice_mul(self.x, x, self.grid.width)
		new_y = slice_mul(self.y, y, self.grid.height)

		if type(x) is int or type(y) is int:
			#delegate!
			self.grid[new_x, new_y, self.z] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				for j, item_j in zip(srange(new_y, self.grid.height), item_i):
					self.grid[i, j, self.z] = item_j

class GridSliceXZ (Container2D, AuxiliaryContainer): #constant Y
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = complete_slice(x, grid.width)
		self.y = y
		self.z = complete_slice(z, grid.depth)

		Container2D.__init__(self, slice_len(self.x, grid.width), slice_len(self.z, grid.depth))
	def __getitem__(self,  p):
		if isinstance(p, int):
			return self[p, ...]			
		x, z = p			
		new_x = slice_mul(self.x, x, self.grid.width)		
		new_z = slice_mul(self.z, z, self.grid.depth)
		return self.grid[new_x, self.y, new_z]

	def __setitem__(self, p, item):
		if isinstance(p, int):
			return self[p, ...]			
		x, z = p	
		new_x = slice_mul(self.x, x, self.grid.width)
		new_z = slice_mul(self.z, z, self.grid.depth)

		if type(x) is int or type(z) is int:
			#delegate!
			self.grid[new_x, self.y, new_z] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				for j, item_j in zip(srange(new_z, self.grid.depth), item_i):
					self.grid[i, self.y, j] = item_j		

class GridSliceYZ (Container2D, AuxiliaryContainer): #constant x
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = x
		self.y = complete_slice(y, grid.height)
		self.z = complete_slice(z, grid.depth)

		Container2D.__init__(self, slice_len(self.y, grid.height), slice_len(self.z, grid.depth))
	def __getitem__(self,  p):
		if isinstance(p, int):
			return self[p, ...]			
		y, z = p	
		new_y = slice_mul(self.y, y, self.grid.height)		
		new_z = slice_mul(self.z, z, self.grid.depth)
		return self.grid[self.x, new_y, new_z]

	def __setitem__(self, p, item):
		if isinstance(p, int):
			self[p, ...] = item
		y, z = p	
		new_y = slice_mul(self.y, y, self.grid.height)
		new_z = slice_mul(self.z, z, self.grid.depth)

		if type(y) is int or type(z) is int:
			#delegate!
			self.grid[self.x, new_y, new_z] = item
		else: #slice!
			for i, item_i in zip(srange(new_y), item):
				for j, item_j in zip(srange(new_z), item_i):
					self.grid[self.x, i, j] = item_j

class GridWindow3D (Container3D, AuxiliaryContainer):
	def __init__(self, grid, x, y, z):
		self.grid = grid
		self.x = complete_slice(x, grid.width)
		self.y = complete_slice(y, grid.height)
		self.z = complete_slice(z, grid.height)	

		Container3D.__init__(self, slice_len(self.x, grid.width), slice_len(self.y, grid.height), slice_len(self.z, grid.depth))
	def __getitem__(self, p):
		if isinstance(p, int):
			return self[p, ..., ...]			
		x, y, z = p	
		new_x = slice_mul(self.x, x, self.grid.width)
		new_y = slice_mul(self.y, y, self.grid.height)
		new_z = slice_mul(self.z, z, self.grid.depth)

		return self.grid[new_x, new_y, new_z]

	def __setitem__(self, p, item):
		if isinstance(p, int):
			self[p, ..., ...] = item
		x, y, z = p	
		new_x = slice_mul(self.x, x, self.grid.width)
		new_y = slice_mul(self.y, y, self.grid.height)
		new_z = slice_mul(self.z, z, self.grid.depth)

		if type(x) is int or type(y) is int or type(z) is int:
			#delegate!
			self.grid[new_x, new_y, self.z] = item
		else: #slice!
			for i, item_i in zip(srange(new_x, self.grid.width), item):
				for j, item_j in zip(srange(new_y, self.grid.height), item_i):
					for k, item_k in zip(srange(new_z, self.grid.depth), item_j):
						self.grid[i, j, k] = item_k

## Class that represent a 3D grid, with enhanced slicing notation.
class Grid3D (Container3D, PrincipleContainer):
	def __init__(self, dims, initial_item = None):
		(width, height, depth) = dims
		Container3D.__init__(self, width, height, depth)
		self.grid = make_grid_3d(width, height, depth, initial_item)

	def __getitem__(self, p):
		if isinstance(p, int):
			return self[p, ..., ...]
		x, y, z = p
		if type(x) is int:
			if type(y) is int:
				if type(z) is int:
					return self.grid[x][y][z]
				elif is_slice(z):
					return GridBar3D(self, x, y, z)
			elif is_slice(y):
				if type(z) is int:
					return GridCol3D(self, x, y, z)
				elif is_slice(z):
					return GridSliceYZ(self, x, y, z)
		elif is_slice(x):
			if type(y) is int:
				if type(z) is int:
					return GridRow3D(self, x, y, z)
				elif is_slice(z):
					return GridSliceXZ(self, x, y, z)
			elif is_slice(y):
				if type(z) is int:
					return GridSliceXY(self, x, y, z)
				elif is_slice(z):
					return GridWindow3D(self, x, y, z)

		raise TypeError

	def __setitem__(self, p, item):
		(x, y, z) = p
		if type(x) is int:
			if type(y) is int:
				if type(z) is int:
					self.grid[x][y][z] = item
				elif is_slice(z):
					g = GridBar3D(self, x, y, z)
					g[...] = item
			elif is_slice(y):
				if type(z) is int:
					g = GridCol3D(self, x, y, z)
					g[...] = item
				elif is_slice(z):
					g = GridSliceYZ(self, x, y, z)
					g[..., ...] = item
		elif is_slice(x):
			if type(y) is int:
				if type(z) is int:
					g = GridRow3D(self, x, y, z)
					g[...] = item
				elif is_slice(z):
					g = GridSliceXZ(self, x, y, z)
					g[..., ...] = item
			elif is_slice(y):
				if type(z) is int:
					g = GridSliceXY(self, x, y, z)
					g[..., ...] = item
				elif is_slice(z):
					g = GridWindow3D(self, x, y, z)
					g[..., ..., ...] = item
		else:
			raise TypeError

class ListGrid3D (Grid3D):
	def __init__(self, dims):
		(width, height, depth) = dims
		Grid3D.__init__(self, (width, height, depth))

		for index in self.index_iter():
			self[index] = []

	## @brief Sets the item at x, y.
	##
	# Use a tuplet (x, y) to access the item.
	def additem(self, p, b):
		(x, y, z) = p
		self[x, y, z].append(b)

class ListGrid2D (Grid2D):
	def __init__(self, dims):
		(width, height) = dims
		Grid2D.__init__(self, (width, height))

		for index in self.index_iter():
			self[index] = []

	## @brief Sets the item at x, y.
	##
	# Use a tuplet (x, y) to access the item.
	def additem(self, p, b):
		(x, y) = p
		self[x, y].append(b)

