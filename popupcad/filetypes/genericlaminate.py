# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
import numpy
from popupcad.filetypes.popupcad_file import popupCADFile
try:
    import itertools.izip as zip
except ImportError:
    pass
import os

class GenericLaminate(popupCADFile):
    filetypes = {'laminate': 'Laminate File'}
    defaultfiletype = 'laminate'

    def __init__(self, layerdef, geoms):
        super(GenericLaminate, self).__init__()
        self.layerdef = layerdef
        self.geoms = geoms

    def copy(self, identical=True):
        geoms = {}
        for key, value in self.geoms.items():
            geoms[key] = [item.copy(identical) for item in value]
        new = type(self)(self.layerdef, geoms)
        if identical:
            new.id = self.id
        return new

    def to_csg(self):
        from popupcad.filetypes.laminate import Laminate
        new = Laminate(self.layerdef)
        for ii, layer in enumerate(self.layerdef.layers):
            geoms = [item.outputshapely() for item in self.geoms[layer]]
            new.replacelayergeoms(layer, geoms)
        return new

    def to_static(self):
        display_geometry_2d = {}
        for layer, geometry in self.geoms.items():
            displaygeometry = [
                geom.outputstatic(
                    brush_color=layer.color) for geom in geometry]
            display_geometry_2d[layer] = displaygeometry
        return display_geometry_2d

    def to_triangles(self):
        alltriangles = {}
        for layer, geoms in self.geoms.items():
            triangles = []
            for geom in geoms:
                try:
                    triangles.extend(geom.triangles3())
                except AttributeError:
                    pass
            alltriangles[layer] = triangles
        return alltriangles

    def layers(self):
        return self.layerdef.layers

    def to_static_sorted(self):
        items = []
        display_geometry = self.to_static()
        layers = self.layerdef.layers
        for layer in layers:
            items.extend(display_geometry[layer])
        return items

    def raster(
        self,
        filename,
        filetype='PNG',
        destination=None,
        gv=None,
        size=(
            400,
            300)):
        if gv is None:
            from popupcad.widgets.render_widget import RenderWidget
            widget = RenderWidget(size)
            gv = widget.gv

        gv.scene().clear()
        [gv.scene().addItem(item) for item in self.to_static_sorted()]
        gv.zoomToFit(buffer=0)
        filename_out = gv.raster(destination, filename, filetype)
        return filename_out
        
    def save_dxf(self,filename):
        import ezdxf
        
        dwg = ezdxf.new('AC1015')
        msp = dwg.modelspace()

        for ii,layer in enumerate(self.layerdef.layers):
            layername = '{:03.0f}_'.format(ii)+layer.name
            dwg.layers.create(name=layername)
            for item in self.geoms[layer]:
                if not item.is_construction():
                    item.output_dxf(msp,layername)
        
        dwg.saveas(filename)     
    
    def transform(self,T):     
        geoms = {}
        for key, value in self.geoms.items():
            geoms[key] = [item.transform(T) for item in value]
        new = type(self)(self.layerdef, geoms)
        return new
        
        
    #Returns the thickness of the laminate
    def getLaminateThickness(self):
        return self.layerdef.zvalue[self.layerdef.layers[-1]]

    def calculateTrueVolume(self):
        layerdef = self.layerdef
        volume = 0
        for layer in layerdef.layers:
            shapes = self.geoms[layer]
            zvalue = layer.thickness
            for shape in shapes:
                area = shape.trueArea()
                zvalue = zvalue / popupcad.SI_length_scaling
                volume += area * zvalue
        return volume
    
    #This will calculate the centeroid
    def calculateCentroid(self): #TODO reimplement using .get_center method()
        layerdef = self.layerdef
        xvalues = []
        yvalues = []
        zvalues = []
        for layer in layerdef.layers:
            shapes = self.geoms[layer]
            zvalue = layer.thickness / popupcad.SI_length_scaling            
            for shape in shapes:
                tris = shape.triangles3()
                for tri in tris:
                    for point in tri:   
                        #Scales the mesh properly
                        point = [float(a)/(popupcad.internal_argument_scaling*popupcad.SI_length_scaling) for a in point]
                        xvalues.append(point[0])
                        yvalues.append(point[1])
                        zvalues.append(zvalue)
        x = sum(xvalues) / len(xvalues)
        y = sum(yvalues) / len(yvalues)
        z = sum(zvalues) / len(zvalues)
        out = (x, y, z)
        return out#[float(a)/popupcad.internal_argument_scaling/popupcad.SI_length_scaling for a in out]
        
    def toSDFTag(self, tag, name_value):
        from lxml import etree        
        layerdef = self.layerdef
        tree_tags = []
        scaling_factor = popupcad.internal_argument_scaling * popupcad.SI_length_scaling
        counter = 0
        for layer in layerdef.layers:
            layer_node = etree.Element(tag, name=name_value + "-" + str(counter))
            layer_thickness = layer.thickness / scaling_factor
            shapes = self.geoms[layer]
            zvalue = layerdef.zvalue[layer] / scaling_factor
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

    #Allows the laminate to get exported as a DAE.
    def toDAE(self):
        import collada
        mesh = collada.Collada()
        layerdef = self.layerdef
        nodes = [] # Each node of the mesh scene. Typically one per layer.
        for layer in layerdef.layers:
            layer_thickness = layer.thickness    
            shapes = self.geoms[layer]
            zvalue = layerdef.zvalue[layer]        
            height = float(zvalue) #* 100 #* 1/popupcad.internal_argument_scaling
            if (len(shapes) == 0) : #In case there are no shapes.
                continue
            for s in shapes:
                geom = self.createMeshFromShape(s, height, mesh, layer_thickness)
                mesh.geometries.append(geom) 
                effect = collada.material.Effect("effect", [], "phone", diffuse=(1,0,0), specular=(0,1,0))
                mat = collada.material.Material("material", "mymaterial", effect)    
                matnode = collada.scene.MaterialNode("materialref", mat, inputs=[])
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
        
    def createMeshFromShape(self, s, layer_num, mesh, thickness): #TODO Move this method into the shape class.
        import collada
        s.exteriorpoints()
        a = s.triangles3()
        vertices = []
        thickness = thickness 
        #thickness = 0 #TODO Replace this with an actual method parameter when I figure out the values.
        
        for coord in a: 
            for dec in coord:            
                vertices.append(dec[0]) #x-axis
                vertices.append(dec[1]) #y-axis            
                vertices.append(layer_num ) #z-axis
        
        for coord in a: 
            for dec in reversed(coord):            
                vertices.append(dec[0]) #x-axis
                vertices.append(dec[1]) #y-axis            
                vertices.append(layer_num + thickness) #z-axi            
            
        raw_edges = s.exteriorpoints()        
        top_edges = []
        bottom_edges = []            
        for dec in raw_edges:      
            top_edges.append((dec[0], dec[1], layer_num)) #x-axis
            bottom_edges.append((dec[0], dec[1], layer_num + thickness))
            
        sideTriangles = list(zip(top_edges, top_edges[1:] + top_edges[:1], bottom_edges))
        sideTriangles2 = list(zip(bottom_edges[1:] + bottom_edges[:1], bottom_edges, top_edges[1:] + top_edges[:1]))
        sideTriangles.extend(sideTriangles2)
        sideTriangles = [list(triangle) for triangle in sideTriangles]
        import itertools
        sideTriangles = list(itertools.chain.from_iterable(sideTriangles))
        sideTriangles = [list(point) for point in sideTriangles]
        sideTriangles = list(itertools.chain.from_iterable(sideTriangles))            
        vertices.extend(sideTriangles)
        
        #This scales the verticies properly. So that they are in millimeters.
        vert_floats = [float(x)/(popupcad.internal_argument_scaling*popupcad.SI_length_scaling) for x in vertices] 
        vert_src_name = str(self.get_basename()) + "-array"
        vert_src = collada.source.FloatSource(vert_src_name, numpy.array(vert_floats), ('X', 'Y', 'Z'))
        geom = collada.geometry.Geometry(mesh, "geometry-" + str(self.id), str(self.get_basename()), [vert_src])    
        input_list = collada.source.InputList()
        input_list.addInput(0, 'VERTEX', "#" + vert_src_name)
        indices = numpy.array(range(0,(len(vertices) / 3)));    
        triset = geom.createTriangleSet(indices, input_list, "materialref")
        triset.generateNormals()    
        geom.primitives.append(triset)
        return geom

