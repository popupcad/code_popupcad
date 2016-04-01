# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
## @package perlin_demo 
# Illustrates some functions in the perlin_noise module.

from __future__ import division
from __future__ import with_statement

from .perlin_noise import SmoothNoise, perlin_noise_from_smoothnoise
from .gradient import SimpleGradient, map_gradient
from .image import grid_to_greyscale_image
from lxml import etree

def generate_heightmap(filename, size = 129, octaves = 9, persistence = 0.5):
    w = h = size
    
    print('Making smooth noise...')
    s_noise = SmoothNoise(w, h)

    print('Making Perlin noise...')
    p_noise = perlin_noise_from_smoothnoise(w, h, octaves, persistence, s_noise, True)

    gradient = SimpleGradient((0, 0, 0, 0), (1, 1, 1, 1))    
    color_grid = map_gradient(gradient, p_noise)
    grid_to_greyscale_image(color_grid, filename + ".png")
     
    print('Done Generating Geoms')

def generate_terrain(output_loc):
    #Generate the actual heightmap geometry
    geometry = etree.Element("geometry")    
    height_map = etree.SubElement(geometry, "heightmap")
    generate_heightmap("terrain")
    etree.SubElement(height_map, "uri").text = "file://" + output_loc + "terrain.png"
    etree.SubElement(height_map, "pos").text = '0 0 0'
    etree.SubElement(height_map, "size").text = '129 129 5'  
    
    #Generate the rest of the stuff we need
    model_root = etree.SubElement(world_root, "model", name='terrain')
    etree.SubElement(model_root, "static").text = "true"    
    #etree.SubElement(model_root, "pose").text = "0 0 0 0 0 0"    
    link_root = etree.SubElement(model_root, "link", name='hills')
    visual_root = etree.SubElement(link_root, "visual", name='visual')
    visual_root.insert(0, geometry)
    material = etree.SubElement(visual_root, "material")    
    etree.SubElement(material, "ambient").text = "1 0 0 1"
    etree.SubElement(material, "diffuse").text = "1 0 0 1"    
    
    collision_root = etree.SubElement(link_root, 'collision', name ='collision')    
    from copy import deepcopy
    copy = deepcopy(geometry)
    collision_root.insert(0, copy)
    return model_root
    
#Main
if __name__ == "__main__":
    import os
    sdf_root = etree.Element("sdf", version='1.5')
    world_root = etree.SubElement(sdf_root, "world", name='world')
    world_root.append(generate_terrain(os.getcwd() + "/"))
    file_output = os.getcwd() + os.path.sep + "terrain" + ".world"
    f = open(file_output,"w")
    f.write(etree.tostring(sdf_root, pretty_print=True))
    f.close()
    print("File saved")    