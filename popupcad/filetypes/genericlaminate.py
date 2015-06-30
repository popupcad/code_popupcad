# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
import numpy
from popupcad.filetypes.popupcad_file import popupCADFile
from collada import *
try:
    import itertools.izip as zip
except ImportError:
    pass


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
        
        
    #Returns the thickness of the laminate
    def getLaminateThickness(self):
        layerdef = self.layerdef        
        zvalue = 0        
        for layer in layerdef:
            zvalue += layerdef.zvalue[layer]
        return zvalue

    def calculateTrueVolume(self):
        layerdef = self.layerdef
        volume = 0
        for layer in layerdef.layers:
            shapes = self.geoms[layer]
            zvalue = layer.thickness
            for shape in shapes:
                area = shape.trueArea()
                zvalue = zvalue / 1000
                volume += area * zvalue
        return volume
    
    #This will calculate the centeroid
    def calculateCentroid(self):
        layerdef = self.layerdef
        xvalues = []
        yvalues = []
        zvalues = []
        for layer in layerdef.layers:
            shapes = self.geoms[layer]
            zvalue = layer.thickness / 1000            
            for shape in shapes:
                tris = shape.triangles3()
                for tri in tris:
                    for point in tri:   
                        #Scales the mesh properly
                        point = [float(a)/popupcad.internal_argument_scaling/1000 for a in point]
                        xvalues.append(point[0])
                        yvalues.append(point[1])
                        zvalues.append(zvalue)
        x = reduce(lambda x, y: x + y, xvalues) / len(xvalues)
        y = reduce(lambda x, y: x + y, yvalues) / len(yvalues)
        z = reduce(lambda x, y: x + y, zvalues) / len(zvalues)
        out = (x, y, z)
        return out#[float(a)/popupcad.internal_argument_scaling/1000 for a in out]
        

    #Allows the laminate to get exported as a DAE.
    def toDAE(self):
        mesh = Collada()
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
                effect = material.Effect("effect", [], "phone", diffuse=(1,0,0), specular=(0,1,0))
                mat = material.Material("material", "mymaterial", effect)    
                matnode = scene.MaterialNode("materialref", mat, inputs=[])
                mesh.effects.append(effect)
                mesh.materials.append(mat)
                geomnode = scene.GeometryNode(geom, [matnode])
                node = scene.Node("node" + str(s.id), children=[geomnode])    
                nodes.append(node)
        myscene = scene.Scene("myscene", nodes)
        mesh.scenes.append(myscene)
        mesh.scene = myscene
        filename = popupcad.exportdir + os.path.sep +   str(self.id) + '.dae' # 
        mesh.write(filename)
        
    def createMeshFromShape(self, s, layer_num, mesh, thickness): #TODO Move this method into the shape class.
        s.exteriorpoints()
        a = s.triangles3()
        vertices = []
        thickness = thickness * 10
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
        sideTriangles = reduce(lambda x, y: x + y, sideTriangles)
        sideTriangles = [list(point) for point in sideTriangles]
        sideTriangles = reduce(lambda x, y: x + y, sideTriangles)            
        vertices.extend(sideTriangles)
        
        #This scales the verticies properly. So that they are in millimeters.
        vert_floats = [float(x)/popupcad.internal_argument_scaling/1000 for x in vertices] 
        vert_src_name = str(self.get_basename()) + "-array"
        vert_src = source.FloatSource(vert_src_name, numpy.array(vert_floats), ('X', 'Y', 'Z'))
        geom = geometry.Geometry(mesh, "geometry-" + str(self.id), str(self.get_basename()), [vert_src])    
        input_list = source.InputList()
        input_list.addInput(0, 'VERTEX', "#" + vert_src_name)
        indices = numpy.array(range(0,(len(vertices) / 3)));    
        triset = geom.createTriangleSet(indices, input_list, "materialref")
        triset.generateNormals()    
        geom.primitives.append(triset)
        return geom


if __name__ == '__main__':   
    def save_dxf(self,filename):
        import ezdxf
        
        dwg = ezdxf.new('AC1015')
        msp = dwg.modelspace()

        for layer in self.layerdef.layers:
            dxf_layer = dwg.layers.create(name=layer.id)
            for item in self.geoms[layer]:
                if not item.is_construction():
                    item.output_dxf(msp,layer.id)
        
        dwg.saveas(filename)                
