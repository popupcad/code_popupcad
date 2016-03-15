# -*- coding: utf-8 -*-
"""
Contributed by Nick Gravish
Email: gravish<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.filetypes.sketch import Sketch
from popupcad.manufacturing.sub_operation2 import SubOperation2
from popupcad.filetypes.laminate import Laminate

import numpy as np
from popupcad.filetypes.operationoutput import OperationOutput

class AlignmentLayup(MultiValueOperation3):
    name = 'AlignmentLayup'
    valuenames = ['Sheet width', 'Pin offset', 'Pin radius']
    defaults = [25., 3., 0.79]
    show = []

    def operate(self, design):

        """
        Return a generic_laminate ref of a layup laminate with all the layers of the part and with the appropriate 25x25mm alignment
        features compatible with the Wood lab micro-robotics manufacturing process.

        Input:
        Design -> a popupcad design file

        Output:
        layup -> A handle to the layup design file
        subop -> A subop which is inserted into the input design file to reduce the number of operations
        """


        #### general geometry constants that most layups will have
        sheet_width = self.values[0]        # mm
        hole_offset = self.values[1]        # location of hole in from corner
        hole_rad    = self.values[2]        # alignment pin geoms

        cross_len   = .75                   # tick length
        cross_horiz = sheet_width/2 - 2*cross_len        # horizontal dimension from center crosshair
        dt          = 0.001                 # small thickness for crosshair

        buff_x      = 5                     # for window sizes
        buff_y      = 1
        wind_h      = 1
        space_x     = 1.3

        # window width, maximum of 1 mm
        wind_w      = lambda N: max(min((sheet_width - 2*buff_x)/(N + 1.3*N - 1.3), 1),0.01)

        # the laminate design
        layup = popupcad.filetypes.design.Design.new()
        layup.updatefilename("layup")
        layer_list = design.return_layer_definition().layers
        layup.define_layers(popupcad.filetypes.layerdef.LayerDef(*layer_list))


        # initiate the sketches
        ############# sheet first
        sheet = Sketch.new()
        tmp_geom = [(-sheet_width/2., -sheet_width/2.), (-sheet_width/2.,  sheet_width/2.),
                    ( sheet_width/2.,  sheet_width/2.), ( sheet_width/2., -sheet_width/2.)]
        sheet_poly = popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists(tmp_geom,[])
        sheet.addoperationgeometries([sheet_poly])

        ############# holes second
        holes = Sketch.new()
        tmp_geom = [(-sheet_width/2. + hole_offset, -sheet_width/2. + hole_offset),
                    (-sheet_width/2. + hole_offset,  sheet_width/2. - hole_offset),
                    ( sheet_width/2. - hole_offset,  sheet_width/2. - hole_offset),
                    ( sheet_width/2. - hole_offset, -sheet_width/2. + hole_offset)]
        # make list of hole geometry
        holes_poly = [popupcad.filetypes.genericshapes.GenericCircle.gen_from_point_lists([pt, (pt[0]+hole_rad, pt[1])],[])
                                            for pt in tmp_geom]
        holes.addoperationgeometries(holes_poly)

        ############# upper triangle
        left_tri = Sketch.new()
        tmp_geom = [(-sheet_width/2. + hole_offset/4, sheet_width/2. - hole_offset*(2/3)),
                    (-sheet_width/2. + hole_offset/4 + hole_rad,  sheet_width/2. - hole_offset*(2/3)),
                    (-sheet_width/2. + hole_offset/4 + 0.5*hole_rad,  sheet_width/2. - hole_offset*(2/3) + 1.2*hole_rad*.75)]
        # make list of hole geometry
        sheet_poly = popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists(tmp_geom,[])
        left_tri.addoperationgeometries([sheet_poly])

        ############# crosshairs
        cross_hairs = Sketch.new()
        tmp_geom_horiz = [(0,-cross_len), (0,cross_len)]
        tmp_geom_vert  = [(-cross_len,0), (cross_len,0)]
        shift = [-cross_horiz, 0, cross_horiz]

        cross_poly_horiz = [popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists([(tmp_geom_horiz[0][0] + c - dt/2.,
                                                                                                tmp_geom_horiz[0][1] - dt/2.),
                                                                                               (tmp_geom_horiz[1][0] + c - dt/2.,
                                                                                                tmp_geom_horiz[1][1] - dt/2.),
                                                                                               (tmp_geom_horiz[1][0] + c + dt/2.,
                                                                                                tmp_geom_horiz[1][1] + dt/2.),
                                                                                               (tmp_geom_horiz[0][0] + c + dt/2.,
                                                                                                tmp_geom_horiz[0][1] - dt/2.)],
                                                                                               [])
                                                                                        for c in shift]

        cross_poly_vert  = [popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists([(tmp_geom_vert[0][0] + c - dt/2.,
                                                                                                tmp_geom_vert[0][1] - dt/2.),
                                                                                               (tmp_geom_vert[1][0] + c - dt/2.,
                                                                                                tmp_geom_vert[1][1] + dt/2.),
                                                                                               (tmp_geom_vert[1][0] + c + dt/2.,
                                                                                                tmp_geom_vert[1][1] + dt/2.),
                                                                                               (tmp_geom_vert[0][0] + c + dt/2.,
                                                                                                tmp_geom_vert[0][1] - dt/2.)],
                                                                                               [])
                                                                                        for c in shift]

        cross_hairs.addoperationgeometries(cross_poly_horiz + cross_poly_vert)

        # Build the sheet with holes
        # Add the sketches to the sketch list
        layup.sketches[sheet.id] = sheet
        layup.sketches[holes.id] = holes
        layup.sketches[cross_hairs.id] = cross_hairs
        layup.sketches[left_tri.id] = left_tri

        # get the layer links for making sketch ops
        layer_links = [layer.id for layer in layer_list]

        holes_sketch = popupcad.manufacturing.simplesketchoperation.SimpleSketchOp({'sketch': [holes.id]},layer_links)
        holes_sketch .name = "Holes"

        trian_sketch = popupcad.manufacturing.simplesketchoperation.SimpleSketchOp({'sketch': [left_tri.id]},layer_links)
        trian_sketch .name = "Left triangle"

        sheet_sketch = popupcad.manufacturing.simplesketchoperation.SimpleSketchOp({'sketch': [sheet.id]},layer_links)
        sheet_sketch.name = "sheet"

        cross_sketch = popupcad.manufacturing.simplesketchoperation.SimpleSketchOp({'sketch': [cross_hairs.id]},layer_links)
        cross_sketch.name = "Crosshairs"

        # laminate operation to combine cross hairs and holes
        sheet_with_holes = popupcad.manufacturing.laminateoperation2.LaminateOperation2({'unary': [(sheet_sketch.id,0)],
                                                                                         'binary': [(holes_sketch.id,0),
                                                                                                    (cross_sketch.id,0),
                                                                                                    (trian_sketch.id,0)]},
                                                                                        'difference')
        sheet_with_holes.name = "Sheet with holes"

        ############# rectangle windows
        windows = [Sketch.new() for _ in layer_list]
        windows_sketchop = []
        # make windows, center on middle of sheet at bottom
        window_width = wind_w(len(windows))
        window_coords = np.array([round(kk*(1 + space_x)*window_width,4) for kk in range(len(windows))])
        window_coords = list(window_coords - np.mean(window_coords)) # center is 0

        for kk, (layer, window, x_coord) in enumerate(zip(layer_list,
                                                          windows,
                                                          window_coords)):

            window.name = layer.name + '_window'

            tmp_geom = [(x_coord, -sheet_width/2. + buff_y),
                        (x_coord,  -sheet_width/2. + buff_y + wind_h),
                        (x_coord + window_width, -sheet_width/2. + buff_y + wind_h),
                        (x_coord + window_width, -sheet_width/2. + buff_y)]
            sheet_poly = popupcad.filetypes.genericshapes.GenericPoly.gen_from_point_lists(tmp_geom,[])
            window.addoperationgeometries([sheet_poly])
            layup.sketches[window.id] = window

            # make a sketch op on all layers above the current layer, this will be removed with a difference from the sheet
            windows_sketchop.append(popupcad.manufacturing.simplesketchoperation.SimpleSketchOp({'sketch': [window.id]},
                                                                                       layer_links[kk+1:]))
            windows_sketchop[-1].name = "Window_" + layer.name

        # laminate operation to remove windows from sheet with holes
        sheet_with_windows = popupcad.manufacturing.laminateoperation2.LaminateOperation2({'unary': [(sheet_with_holes.id,0)],
                                                                                         'binary': [(sktch.id,0) for sktch
                                                                                                    in windows_sketchop]},
                                                                                         'difference')
        sheet_with_windows.name = "Final sheet"

        # add the sketch ops to the design and generate the sketch op
        other_ops = windows_sketchop + [trian_sketch, holes_sketch, sheet_sketch, cross_sketch, sheet_with_holes, sheet_with_windows]
        [layup.addoperation(item) for item in other_ops]
        [item.generate(layup) for item in other_ops]

        return sheet_with_windows.output[0].csg

        # might need valueoperation
