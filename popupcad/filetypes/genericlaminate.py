from __future__ import division
# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
import popupcad
import os

class GenericLaminate(object):
    def __init__(self, layerdef, geoms):
        self.id = id(self)
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
            geoms = [item.to_shapely() for item in self.geoms[layer]]
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
        triangles_by_layer = {}
        for layer, geoms in self.geoms.items():
            triangles = []
            for geom in geoms:
                try:
                    triangles.extend(geom.triangles3())
                except AttributeError:
                    pass
            triangles_by_layer[layer] = triangles
        return triangles_by_layer

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
        
    def to_svg(self,filename,destination,gv=None,size=(400,300)):
        if gv is None:
            from popupcad.widgets.render_widget import RenderWidget
            widget = RenderWidget(size)
            gv = widget.gv

        gv.scene().clear()
        [gv.scene().addItem(item) for item in self.to_static_sorted()]
        gv.zoomToFit(buffer=0)
        import os
        filename_out = os.path.join(destination,filename)
        gv.scene().renderprocess(filename,1.0,destination)
        return filename_out

    def save_dxf(self,basename,separate_files=False,directory = None):
        import ezdxf
        ezdxf.options.template_dir = popupcad.supportfiledir        
        
        if directory is None:
            directory = popupcad.exportdir
        
        if not separate_files:
            filename = os.path.normpath(os.path.join(directory,basename+'.dxf'))
            dwg = ezdxf.new('AC1015')
            msp = dwg.modelspace()

        for ii,layer in enumerate(self.layerdef.layers):
            layername = '{:03.0f}_'.format(ii)+layer.name
            if separate_files:
                filename = os.path.normpath(os.path.join(directory,basename+'_'+layername+'.dxf'))
                dwg = ezdxf.new('AC1015')
                msp = dwg.modelspace()
            dwg.layers.create(name=layername)
            for item in self.geoms[layer]:
                if not item.is_construction():
                    item.output_dxf(msp,layername)
            if separate_files:
                dwg.saveas(filename)     
        
        if not separate_files:
            dwg.saveas(filename)     
    
    def transform(self,T):     
        geoms = {}
        for key, value in self.geoms.items():
            geoms[key] = [item.transform(T) for item in value]
        new = type(self)(self.layerdef, geoms)
        return new
        
        
    #Returns the thickness of the laminate
    def getLaminateThickness(self):
        return self.layerdef.z_values[self.layerdef.layers[-1]]

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
    
    #This will calculate the centeroid #REMOVE DEPECRATED CODE
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
                        point = [float(a)/(popupcad.SI_length_scaling) for a in point]
                        xvalues.append(point[0])
                        yvalues.append(point[1])
                        zvalues.append(zvalue)
        x = sum(xvalues) / len(xvalues)
        y = sum(yvalues) / len(yvalues)
        z = sum(zvalues) / len(zvalues)
        out = (x, y, z)
        return out#[float(a)/popupcad.SI_length_scaling for a in out]
        
    def getDensity(self):
        total_densities = sum([layer.density for layer in self.layers()])
        return total_densities / len(self.layers())
                
                
        
    def getBoundingBox(self):
        all_shapes = []
        layerdef = self.layerdef
        for layer in layerdef.layers:
            layer_thickness = layer.thickness    
            shapes = self.geoms[layer]
            zvalue = layerdef.z_values[layer]        
            height = float(zvalue) #* 100 #* 1/popupcad.internal_argument_scaling
            if (len(shapes) == 0) : #In case there are no shapes.
                continue
            all_shapes.extend(shapes)
        all_shapes = [shape.to_shapely() for shape in shapes]
        master_shape = all_shapes[0]
        for shape in all_shapes[1:]:
            master_shape = master_shape.union(shape)
        bounds = master_shape.bounds
        bounds = [value/popupcad.csg_processing_scaling for value in bounds]
        return bounds

    def mass_properties(self,length_scaling = 1):
        zvalues = self.layerdef.z_values2()
        volume_total = 0
        center_of_mass_accumulator = 0
        next_args = []
        mass_total = 0
        for layer in self.layers():
            layer_volume = 0
            density = layer.density
            z_lower = zvalues[layer]['lower']
            z_upper = zvalues[layer]['upper']
            for geom in self.geoms[layer]:
                area,centroid,volume,mass,tris = geom.mass_properties(density,z_lower,z_upper,length_scaling)
                volume_total+=volume
                layer_volume+=volume
                center_of_mass_accumulator+=volume*centroid*density
                next_args.append((geom,(density,z_lower,z_upper,tris)))
            mass_total+=layer_volume*density
        center_of_mass = center_of_mass_accumulator/mass_total
        I = 0
        for geom,args in next_args:
            I+=geom.inertia_tensor(center_of_mass,*args)
        return volume_total,mass_total,center_of_mass,I

    def all_geoms(self):
        allgeoms = []
        for layer in self.layerdef.layers:
            allgeoms.extend(self.geoms[layer])
        return allgeoms
        
    def __lt__(self,other):
        return self.all_geoms()[0]<other.all_geoms()[1]
        
    def hollow(self):
        new = self.copy()
        for layer in new.layers():
            new.geoms[layer] = [item2 for item in new.geoms[layer] for item2 in item.hollow()]
        return new

    def fill(self):
        new = self.copy()
        for layer in new.layers():
            new.geoms[layer] = [item2 for item in new.geoms[layer] for item2 in item.fill()]
        return new

    def toSDFTag(self, *args,**kwargs):
        import popupcad_gazebo.laminate_adders
        return popupcad_gazebo.laminate_adders.toSDFTag(self, *args,**kwargs)            

    def toSTL(self, *args,**kwargs):
        import popupcad_gazebo.laminate_adders
        return popupcad_gazebo.laminate_adders.toSTL(self,*args,**kwargs)            

    def toDAE(self, *args,**kwargs):
        import popupcad_gazebo.laminate_adders
        return popupcad_gazebo.laminate_adders.toDAE(self, *args,**kwargs)            

    def createDAEFromShape(self, *args,**kwargs):
        import popupcad_gazebo.laminate_adders
        return popupcad_gazebo.laminate_adders.createDAEFromShape(self, *args,**kwargs)            
        