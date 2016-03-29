## @package perlin_noise

"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

## @brief Contains the algorithms for producing perlin noise.
## Tutorial: http://www.luma.co.za/labs/2008/01/20/perlin-noise/

from __future__ import division
from __future__ import with_statement

from random import random
from random import shuffle
from random import randint
from math import floor
from math import cos
from math import pi
from math import sqrt

from .enhanced_grid import Grid1D
from .enhanced_grid import Grid2D
from .enhanced_grid import Grid3D

##Generates a Grid with uniform noise, generated 
##between 0 and 1.
##
#	@param width
#		The width of the Grid to produce.
#		@param height
#		The height of the Grid to produce.
def make_uniform_noise(width, height):
	noise = Grid2D((width, height), 0)
	
	for p in noise.index_iter():
		noise[p] = random() #randint(0, 1) #random()

	return noise
	
def make_checker_board_noise(width, height, period=1):
	noise = Grid2D((width, height), 0)
	
	for p in noise.index_iter():
		i, j = p
		noise[p] = (i // period % 2 + j // period % 2) % 2
		
	return noise

##@brief Class for generating smooth noise.
##
# Successive calls to generate will use the same underlying grid
# of uniform noise to sample from.
class SmoothNoise:
	
	## Constructs a new SmoothNoise object
	# @param width
	#		Width of the grid to generate
	# @param height
	#		Height of the grid to generate
	# @param noise_fn
	# 		A function that takes two arguments (the grid dimensions) and return a grid of noise
	# @param interpolation
	#		A string that specifies what interpolation scheme to use. Can be 'linear', 'cosine', or 'cubic'.
	def __init__(self, width, height, noise_fn = make_uniform_noise, interpolation='linear'):
		self.nois_fn = noise_fn
		self.uniform_noise = noise_fn(width, height)
		
		self.width = width
		self.height = height
		
		if interpolation == 'linear':
			self.interpolation = self.linear_interpolation	
		elif interpolation == 'cosine':
			self.interpolation = self.cosine_interpolation	
		elif interpolation == 'cubic':
			self.interpolation == self.cubic_interpolation
		else:
			self.interpolation = self.linear_interpolation
	
	##Generates a grid with the smooth noise
	##
	# @param k
	#		The sampling distance, usually a power of 2.
	#		If k == 1, every point in the uniform noise grid is sampled
	#		and the returned grid is equivalent to the uniform noise
	#		grid.
	def generate(self, k):
		return self.linear_interpolation(k)
	
	def linear_interpolation(self, k):
		t = 2**k
		noise = self.uniform_noise
		smooth_noise = Grid2D((self.width, self.height), 0)
		
		for i in range(self.width):	
			x0, x1, x_alpha = sample_points(i, t, self.width)
			
			for j in range(self.height):				
				y0, y1, y_alpha = sample_points(j, t, self.height)
				
				a0 = (1 - x_alpha)*noise[x0, y0] +(x_alpha)*noise[x1, y0]
				a1 = (1 - x_alpha)*noise[x0, y1] + (x_alpha)*noise[x1, y1]
				
				smooth_noise[i, j] = (1 - y_alpha)*a0 + (y_alpha)*a1
		return smooth_noise

	def cosine_interpolation(self, k):
		t = 2**k
		noise = self.uniform_noise
		smooth_noise = Grid2D((self.width, self.height), 0)
		
		for i in range(self.width):	
			x0, x1, x_alpha = sample_points(i, t, self.width)
			x_alpha = (1-cos(x_alpha*pi))/2
			for j in range(self.height):				
				y0, y1, y_alpha = sample_points(j, t, self.height)
				y_alpha = (1-cos(y_alpha*pi))/2
				
				a0 = (1 - x_alpha)*noise[x0, y0] +(x_alpha)*noise[x1, y0]
				a1 = (1 - x_alpha)*noise[x0, y1] + (x_alpha)*noise[x1, y1]
				
				smooth_noise[i, j] = (1 - y_alpha)*a0 + (y_alpha)*a1
		return smooth_noise

	def cubic_interpolation(self, k):
		t = 2**k
		noise = self.uniform_noise
		smooth_noise = Grid2D((self.width, self.height), 0)
		
		for i in range(self.width):	
			x0, x1, x2, x3, x_alpha, x_alpha_2, x_alpha_3, x_alpha_i, x_alpha_i2, x_alpha_i3 = sample_points_cubic(i, t, self.width)
			
			for j in range(self.height):				
				y0, y1, y2, y3, y_alpha, y_alpha_2, y_alpha_3, y_alpha_i, y_alpha_i2, y_alpha_i3 = sample_points_cubic(j, t, self.height)
			
				a0 = x_alpha_i3*noise[x0, y0] + x_alpha_i2*x_alpha*noise[x1, y0] + \
					 x_alpha_i*x_alpha_2*noise[x2, y0] + x_alpha_3*noise[x3, y0]
				a1 = x_alpha_i3*noise[x0, y1] + x_alpha_i2*x_alpha*noise[x1, y1] + \
					 x_alpha_i*x_alpha_2*noise[x2, y1] + x_alpha_3*noise[x3, y1]
				a2 = x_alpha_i3*noise[x0, y2] + x_alpha_i2*x_alpha*noise[x1, y2] + \
					 x_alpha_i*x_alpha_2*noise[x2, y2] + x_alpha_3*noise[x3, y2]
				a3 = x_alpha_i3*noise[x0, y3] + x_alpha_i2*x_alpha*noise[x1, y3] + \
					 x_alpha_i*x_alpha_2*noise[x2, y3] + x_alpha_3*noise[x3, y3]
				
				smooth_noise[i, j] = y_alpha_i3*a0 + y_alpha_i2*y_alpha*a1 + \
					 y_alpha_i*y_alpha_2*a2 + y_alpha_3*a3
		return smooth_noise		

##@brief Private.
##
# @param noise
#		A noise grid from which the first row and first column will be copied.
def perlin_noise_from_smoothnoise(width, height, layers, falloff, noise, normalize=True):
	perlin_noise = Grid2D((width, height), 0)	
	r = 1
	
	for k in range(layers):
		r *= falloff
		s_noise = noise.generate(layers - k - 1)

		for p in perlin_noise.index_iter():
			perlin_noise[p] += s_noise[p]*r

	#Normalise
	if normalize:
		r = 1
		w = 0
		
		for k in range(layers):
			r *= falloff
			w += r
		
		for p in perlin_noise.index_iter():
			perlin_noise[p] /= w
			
	return perlin_noise

##@brief Generates Perlin noise in a rectangle.
##
# @param width
#		The width of the rectangle.
# @param height
#		The height of the rectangle
# @param layers
#		The number of layers of smooth noise to use.
# @param tiles
#		The number of tiles to generate. These tiles will all 
#		tile with themselves and each other.
def perlin_noise(width, height, layers, falloff = 0.5, tiles=1):
	noise = SmoothNoise(width, height)
	p = [perlin_noise_from_smoothnoise(width, height, layers, falloff, noise)]
	
	for k in xrange(tiles - 1):
		noise = SmoothNoise(width, height)
		p.append(perlin_noise_from_smoothnoise(width, height, layers, falloff, noise))
		
	return p

##@brief Generates tiles of Perlin noise that are mutually seamless.
##
# @param width
#		The width of the rectangle.
# @param height
#		The height of the rectangle
# @param layers
#		The number of layers of smooth noise to use.
# @param tiles
#		The number of tiles to generate. These tiles will all 
#		tile with themselves and each other.
def perlin_noise_tileable(width, height, layers, falloff = 0.5, tiles=1):
	noise = SmoothNoise(width, height)
	p = [perlin_noise_from_smoothnoise(width, height, layers, falloff, noise)]
	
	for k in xrange(tiles - 1):
		new_noise = SmoothNoise(width, height)
		new_noise.uniform_noise[:,0] = noise.uniform_noise[:,0]
		new_noise.uniform_noise[0,:] = noise.uniform_noise[0, :]
		
		p.append(perlin_noise_from_smoothnoise(width, height, layers, falloff, new_noise))
		
	return p
	
##@brief Generates integer Perlin noise in a rectangle.
##
# @param width
#		The width of the rectangle.
# @param height
#		The height of the rectangle
# @param layers
#		The number of layers of smooth noise to use.
# @param n
#		The integer range for the resulting noise. If n is 7, for
#		example, all values in the grid will be 0, 1, 2, 3, 4, 5, or 6.
# @param tiles
#		The number of tiles to generate. These tiles will all 
#		tile with themselves and each other.
def int_perlin_noise(width, height, layers, n, tiles=1):
	noise_list = perlin_noise(width, height, layers)
	int_noise_list = []
	
	for noise in noise_list:
		int_noise = Grid2D((width, height))
		
		for p in noise.index_iter():
			int_noise[p] = int(floor(noise[p]/(1 / n)))
		
		int_noise_list.append(int_noise)
			
	return int_noise_list

##@brief Returns a shuffled list of integers in the range 0 to n - 1.
def random_permutation(n):
	return shuffle(range(n))	

##@brief Private.
# Returns a tuple that can be used for cubic interpolation
# the tuple is the tuple x0, x1, x2, x3, alpha
# such that 
# @code
# x0 = x // t * t
# x1 = x0 + t
# x = alpha * t + x0
# x = x1 - (1 - alpha) * t
# x0 <= x <x1
# @endcode
def sample_points(x, t, max_x):
	x0 = x // t * t
	return x0, (x0 + t) % max_x, (x - x0) / t

def sample_points_cubic(x, t, max_x):
	x1 = x // t * t
	x0 = (x1 - t) % max_x
	x2 = (x1 + t) % max_x
	x3 = (x1 + 2*t) % max_x
	x_alpha = 1 - (x - x1) / t 
	
	x_alpha_2 = x_alpha * x_alpha
	x_alpha_3 = x_alpha * x_alpha_2

	x_alpha_i = 1 - x_alpha
	x_alpha_i2 = x_alpha_i*x_alpha_i
	x_alpha_i3 = x_alpha_i2 * x_alpha_i
	
	return x0, x1, x2, x3, x_alpha, x_alpha_2, x_alpha_3, x_alpha_i, x_alpha_i2, x_alpha_i3
	

def uniform_noise_3d(width, height, depth):
	noise = Grid3D((width, height, depth), 0)
	
	for p in noise.index_iter():
		noise[p] = random()
					
	return noise

def make_uniform_noise_1d(length):
	noise = Grid1D((length, ), 0)
	
	for p in noise.index_iter():
		noise[p] = random()
					
	return noise

##@brief Class for generating smooth noise.
##
# Successive calls to generate will use the same underlying grid
# of uniform noise to sample from.
class SmoothNoise1D:
	
	## Constructs a new SmoothNoise object
	# @param width
	#		Width of the grid to generate
	# @param height
	#		Height of the grid to generate
	# @param noise_fn
	# 		A function that takes two arguments (the grid dimensions) and return a grid of noise
	# @param interpolation
	#		A string that specifies what interpolation scheme to use. Can be 'linear', 'cosine', or 'cubic'.
	def __init__(self, length, noise_fn = make_uniform_noise_1d, interpolation='linear'):
		self.nois_fn = noise_fn
		self.uniform_noise = noise_fn(length)
		
		self.length = length
		
		if interpolation == 'linear':
			self.interpolation = self.linear_interpolation	
		elif interpolation == 'cosine':
			self.interpolation = self.cosine_interpolation	
		elif interpolation == 'cubic':
			self.interpolation == self.cubic_interpolation
		else:
			self.interpolation = self.linear_interpolation
	
	##Generates a grid with the smooth noise
	##
	# @param k
	#		The sampling distance, usually a power of 2.
	#		If k == 1, every point in the uniform noise grid is sampled
	#		and the returned grid is equivalent to the uniform noise
	#		grid.
	def generate(self, k):
		return self.linear_interpolation(k)
	
	def linear_interpolation(self, k):
		t = 2**k
		noise = self.uniform_noise
		smooth_noise = Grid1D((self.length, ), 0)
		
		for i in range(self.length):	
			x0, x1, x_alpha = sample_points(i, t, self.length)							
			smooth_noise[i] = (1 - x_alpha)*noise[x0] +(x_alpha)*noise[x1]
		return smooth_noise

			
##@brief Private.
##
# @param noise
#		A noise grid from which the first row and first column will be copied.
def perlin_noise_from_smoothnoise_1d(length, layers, falloff, noise, normalize=True):
	perlin_noise = Grid1D((length, ), 0)	
	r = 1
	
	for k in range(layers):
		r *= falloff
		s_noise = noise.generate(layers - k - 1)

		for p in perlin_noise.index_iter():
			perlin_noise[p] += s_noise[p]*r

	#Normalise
	if normalize:
		r = 1
		w = 0
		
		for k in range(layers):
			r *= falloff
			w += r
		
		for p in perlin_noise.index_iter():
			perlin_noise[p] /= w
			
	return perlin_noise

##@brief Class for generating smooth noise.
##
# Successive calls to generate will use the same underlying grid
# of uniform noise to sample from.
class SmoothNoise3D:
	
	## Constructs a new SmoothNoise object
	# @param oldNoise
	#		If oldNoise is given, the first row and column of oldNoise's
	#		uniform noise grid is copied to this SmoothNoise object's
	#		uniform noise grid. This is for making sets of tiles with certain 
	#		algorithms, such as the Perlin noise algorithm.
	def __init__(self, width, height, depth):
		self.uniform_noise = uniform_noise_3d(width, height, depth)
		
		self.width = width
		self.height = height
		self.depth = depth
		
	##Generates a grid with the smooth noise
	##
	# @param k
	#		The sampling distance, usually a power of 2.
	#		If k == 1, every point in the uniform noise grid is sampled
	#		and the returned grid is equivalent to the uniform noise
	#		grid.
	def generate(self, k):			
		t = 2**k
		noise = self.uniform_noise
		smooth_noise = Grid3D((self.width, self.height, self.depth), 0)
	
		for i in range(self.width):
			x0, x1, x_alpha = sample_points(i, t, self.width)
			
			for j in range(self.height):
				y0, y1, y_alpha = sample_points(j, t, self.height)
				
				for k in range(self.depth):
					z0, z1, z_alpha = sample_points(k, t, self.depth)
										
					a0 = (1 - x_alpha)*noise[x0, y0, z0] + x_alpha*noise[x1, y0, z0]
					a1 = (1 - x_alpha)*noise[x0, y1, z0] + x_alpha*noise[x1, y1, z0]
					c0 = (1 - y_alpha)*a0 + y_alpha*a1
					
					b0 = (1 - x_alpha)*noise[x0, y0, z1] + x_alpha*noise[x1, y0, z1]
					b1 = (1 - x_alpha)*noise[x0, y1, z1] + x_alpha*noise[x1, y1, z1]
					c1 = (1 - y_alpha)*b0 + y_alpha*b1
		
					smooth_noise[i, j, k] = (1 - z_alpha)*c0 + z_alpha*c1

		return smooth_noise

##@brief Private.
##
def perlin_noise_from_smoothnoise_3d(width, height, depth, layers, falloff):
	perlin_noise = Grid3D((width, height, depth), 0)
	noise = SmoothNoise3D(width, height, depth)
	r = 1
	
	for kk in range(layers):
		r *= falloff
		s_noise = noise.generate(layers - kk - 1)
		
		for p in perlin_noise.index_iter():
			perlin_noise[p] += s_noise[p]*r

	r = 1
	w = 0
	
	for kk in xrange(layers):
		r *= falloff
		w += r
	
	for p in perlin_noise.index_iter():
		perlin_noise[p] /= w
		
	return perlin_noise

##@brief Generates integer Perlin noise in a 3D box.
##
# @param width
#		The width of the box.
# @param height
#		The height of the box
# @param depth
#		The depth of the box
# @param layers
#		The number of layers of smooth noise to use.
# @param n
#		The integer range for the resulting noise. If n is 7, for
#		example, all values in the grid will be 0, 1, 2, 3, 4, 5, or 6.
# @param tiles
#		The number of tiles to generate. These tiles will all 
#		tile with themselves and each other.
def perlin_noise_3d(width, height, depth, layers, falloff = 0.5, tiles=1):
	p = [perlin_noise_from_smoothnoise_3d(width, height, depth, layers, falloff)]
			
	return p

