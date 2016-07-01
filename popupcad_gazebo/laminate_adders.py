# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 09:52:48 2016

@author: daukes
"""
import popupcad
import numpy
import os

def toSDFTag(self, tag, name_value):
    from lxml import etree        
    layerdef = self.layerdef
    tree_tags = []
    scaling_factor = popupcad.SI_length_scaling
    counter = 0
    for layer in layerdef.layers:
        layer_node = etree.Element(tag, name=name_value + "-" + str(counter))
        layer_thickness = layer.thickness / scaling_factor
        shapes = self.geoms[layer]
        zvalue = layerdef.z_values[layer] / scaling_factor
        if (len(shapes) == 0) : 
            continue
        for s in shapes:
            center = s.get_center()
            etree.SubElement(layer_node, "pose").text = str(center[0]) + " " + str(center[1]) + " " + str(zvalue) + " 0 0 0"
            geometry = etree.SubElement(layer_node, "geometry")
            line = etree.SubElement(geometry, "polyline")
            points = s.exterior_points_from_center()
            for point in points:
                etree.SubElement(line, "point").text = str(point[0]) + " " + str(point[1])
            etree.SubElement(line, "height").text = str(layer_thickness)
        tree_tags.append(layer_node)
        counter+=1
    return tree_tags
 
#TODO Clean up variable names so it satisifes pylint and whatnot.
#Exports the mesh as an STL files
def toSTL(self):
    """
    Exports the current laminate as an STL file
    """
    from stl.mesh import Mesh #Requires numpy-stl 
    layerdef = self.layerdef
    laminate_verts = []
    for layer in layerdef.layers:
        shapes = self.geoms[layer]#TODO Add it in for other shapes         
        zvalue = layerdef.z_values[layer]      
        thickness = layer.thickness
        if (len(shapes) == 0) : #In case there are no shapes.
            print("No shapes skipping")            
            continue
        for s in shapes:
            shape_verts = s.extrudeVertices(thickness, z0=zvalue)
            laminate_verts.extend(shape_verts)

    laminate_verts = [point/popupcad.SI_length_scaling for point in laminate_verts]
    # Or creating a new mesh (make sure not to overwrite the `mesh` import by
    # naming it `mesh`):
    VERTICE_COUNT = len(laminate_verts)//3 #Number of verticies
    data = numpy.zeros(VERTICE_COUNT, dtype=Mesh.dtype) #We create an array full of zeroes. Will edit it later.
    #Creates a mesh from the specified set of points
    for dtype, points in zip(data, numpy.array(laminate_verts).reshape(-1,9)):
        points = points.reshape(-1, 3) #Splits each triangle into points
        numpy.copyto(dtype[1], points) #Copies the list of points into verticies index
    
    data = Mesh.remove_duplicate_polygons(data)
    
    #This constructs the mesh objects, generates the normals and all
    your_mesh = Mesh(data, remove_empty_areas=True)

    filename =  str(self.id) + '.stl'
            
    old_path = os.getcwd() #Save old directory
    new_path = popupcad.exportdir + os.path.sep #Load export directory
    os.chdir(new_path) #Change to export directory
    print("Saving in " + str(new_path))
    your_mesh.save(filename)#Apparently save does not like absolute paths
    print(filename + " has been saved")
    os.chdir(old_path) #Change back to old directory
    
#Allows the laminate to get exported as a DAE.
def toDAE(self):
    """
    Exports the current lamiante to a DAE file format
    """
    import collada
    mesh = collada.Collada()
    layerdef = self.layerdef
    nodes = [] # Each node of the mesh scene. Typically one per layer.
    for layer in layerdef.layers:
        layer_thickness = layer.thickness    
        shapes = self.geoms[layer]
        zvalue = layerdef.z_values[layer]        
        height = float(zvalue) #* 100 #* 
        if (len(shapes) == 0) : #In case there are no shapes.
            continue
        for s in shapes:
            geom = self.createDAEFromShape(s, height, mesh, layer_thickness)
            mesh.geometries.append(geom) 
            effect = collada.material.Effect("effect", [], "phone", diffuse=(1,0,0), specular=(0,1,0))
            mat = collada.material.Material("material", "mymaterial" + str(s.id), effect)    
            matnode = collada.scene.MaterialNode("materialref" + str(s.id), mat, inputs=[])
            mesh.effects.append(effect)
            mesh.materials.append(mat)
            geomnode = collada.scene.GeometryNode(geom, [matnode])
            node = collada.scene.Node("node" + str(s.id), children=[geomnode])    
            nodes.append(node)
    myscene = collada.scene.Scene("myscene", nodes)
    mesh.scenes.append(myscene)
    mesh.scene = myscene
    filename = popupcad.exportdir + os.path.sep +  str(self.id) + '.dae' # 
    mesh.write(filename)
    
def createDAEFromShape(self, s, layer_num, mesh, thickness): #TODO Move this method into the shape class.
    import collada
    vertices = s.extrudeVertices(thickness, z0=layer_num)
    
    #This scales the verticies properly. So that they are in millimeters.
    vert_floats = [float(x)/(popupcad.SI_length_scaling) for x in vertices] 
    vert_src_name = str(self.id) + '|' + str(s.id) + "-array"
    vert_src = collada.source.FloatSource(vert_src_name, numpy.array(vert_floats), ('X', 'Y', 'Z'))
    geom = collada.geometry.Geometry(mesh, "geometry-" + str(s.id), str(self.id), [vert_src])
    input_list = collada.source.InputList()
    input_list.addInput(0, 'VERTEX', "#" + vert_src_name)
    indices = numpy.array(range(0,(len(vertices) // 3)));    
    triset = geom.createTriangleSet(indices, input_list, "materialref" + str(s.id))
    triset.generateNormals()    
    geom.primitives.append(triset)
    return geom
