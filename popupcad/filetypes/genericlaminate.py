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
            zvalue = layerdef.zvalue[layer]        
            for shape in shapes:
                area = shape.trueArea()
                zvalue = zvalue/popupcad.internal_argument_scaling/1000
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
            zvalue = layerdef.zvalue[layer]        
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
            shapes = self.geoms[layer]
            zvalue = layerdef.zvalue[layer]        
            height = float(zvalue) #* 100 #* 1/popupcad.internal_argument_scaling
            if (len(shapes) == 0) : #In case there are no shapes.
                continue
            for s in shapes:
                geom = self.createMeshFromShape(s, height, mesh)
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
        #ath_parts = self.lastdir().split(str(os.path.sep))
        #path_parts =         
        filename = popupcad.exportdir + os.path.sep +   str(self.id) + 'dat.dae' # 
        mesh.write(filename)
        
    def createMeshFromShape(self, s, layer_num, mesh): #TODO Move this method into the shape class.
        s.exteriorpoints()
        a = s.triangles3()
        vertices = []
        for coord in a: 
            for dec in coord:            
                vertices.append(dec[0]) #x-axis
                vertices.append(dec[1]) #y-axis            
                vertices.append(layer_num ) #z-axi
            
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
    import PySide.QtGui as qg
    import sys
    
    app = qg.QApplication(sys.argv)

    a = GenericLaminate(1, {})
    a.copy()
    a.saveAs()
#    sys.exit(app.exec_())
