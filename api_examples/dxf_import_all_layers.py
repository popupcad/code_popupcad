# -*- coding: utf-8 -*-
"""
Script written by Nick Gravish
Please see LICENSE for full license.
"""

import popupcad
import ezdxf
import popupcad.filetypes.sketch
import sys

import qt.QtCore as qc
import qt.QtGui as qg


from popupcad.filetypes.genericshapes import GenericPolyline
from popupcad.filetypes.genericshapes import GenericPoly
from popupcad.filetypes.genericshapes import GenericLine

def import_dxf_layer_geometry(dxf, layername):
    entities = dxf.entities
    generics = []
    for entity in entities:
        if entity.dxf.layer in layername:
            if isinstance(entity, ezdxf.modern.graphics.Line):
                import numpy
                points = numpy.array(
                    [entity.dxf.start[:2], entity.dxf.end[:2]])
                generics.append(
                    GenericLine.gen_from_point_lists(
                        points.tolist(),
                        []))
            elif isinstance(entity, ezdxf.modern.graphics.LWPolyline):
                import numpy
                points = numpy.array([item for item in entity.get_points()])
                points = points[:, :2]
                if entity.closed:
                    generics.append(GenericPoly.gen_from_point_lists(points.tolist(), []))
                else:
                    generics.append(GenericPolyline.gen_from_point_lists(points.tolist(), []))
            elif isinstance(entity, ezdxf.modern.graphics.Point):
                from popupcad.geometry.vertex import DrawnPoint
                point = DrawnPoint(numpy.array(entity.get_dxf_attrib('location')[:2]))
                generics.append(point)
            elif isinstance(entity, ezdxf.modern.graphics.Spline):
                knots = entity.get_knot_values()
                control_points = entity.get_control_points()
                weights = entity.get_weights()
                n = len(control_points) - 1
                domain = popupcad.algorithms.spline_functions.make_domain(knots, n * 5)
                points = popupcad.algorithms.spline_functions.interpolated_points(control_points, knots, weights,
                                                                                  domain)
                points = points[:, :2]
                if entity.closed:
                    generics.append(GenericPoly.gen_from_point_lists(points.tolist(), []))
                else:
                    generics.append(GenericPolyline.gen_from_point_lists(points.tolist(), []))

                    #                        print(points)
            else:
                print(entity)

    new = popupcad.filetypes.sketch.Sketch.new()
    new.addoperationgeometries(generics)
    newsketchname = layername + '.sketch'
    new.updatefilename(newsketchname)

    return new

# for testing
# filename = '/Users/nickgravish/popupCAD_files/sketches/Scissor02.dxf'

if __name__ == '__main__':

    filename = sys.argv[1] # get the filename passed in

    # create the base CAD design file
    design = popupcad.filetypes.design.Design.new()
    design.define_layers(popupcad.filetypes.layerdef.LayerDef(*popupcad.filetypes.material2.default_sublaminate))


    # load dxf file and select layer names
    import ezdxf.modern

    dxf = ezdxf.readfile(filename)
    layer_names = [layer.dxf.name for layer in dxf.layers]

    # loop through layer names and load geometry
    for layer in layer_names:
        # create the sketch
        sketch = import_dxf_layer_geometry(dxf, layer)

        # add the sketch to the design file
        design.sketches[sketch.id] = sketch

    # save cad file
    design.save_yaml(filename + '.cad')

    # to visualize the result, but can be commented out.
    app = qg.QApplication(sys.argv)
    editor = popupcad.guis.editor.Editor()
    editor.load_design(design)
    editor.show()
    sys.exit(app.exec_())
