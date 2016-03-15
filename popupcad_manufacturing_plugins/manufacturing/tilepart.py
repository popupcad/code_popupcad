# -*- coding: utf-8 -*-
"""
Contributed by Nick Gravish
Email: gravish<at>seas.harvard.edu.
Please see LICENSE for full license.
"""


# import os
# import sys
# import numpy as np
import math
import qt.QtGui as qg

# from popupcad.filetypes.operationoutput import OperationOutput
# import popupcad_manufacturing_plugins

import popupcad
from popupcad.filetypes.sketch import Sketch
from popupcad_manufacturing_plugins.manufacturing.autoweb4 import AutoWeb4
from popupcad.manufacturing.simplesketchoperation import SimpleSketchOp
from popupcad.filetypes.genericshapes import GenericLine
from popupcad.manufacturing.transform_internal import TransformInternal
from popupcad.manufacturing.laminateoperation2 import LaminateOperation2
from popupcad.filetypes.operation2 import Operation2
from popupcad.manufacturing.multivalueoperation3 import MultiValueOperation3
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.widgets.listmanager import SketchListManager,SketchListViewer
from popupcad.filetypes.operationoutput import OperationOutput

class Dialog(qg.QDialog):

    def __init__(self,design,prioroperations, tilepart = None):
        super(Dialog, self).__init__()

        if tilepart is not None:

            self.sheet_opref_tp = tilepart.sheet_opref
            self.part_opref_tp = tilepart.part_opref
            self.sketch_bounding_box_tp = tilepart.sketch_bounding_box
            self.sc_tp = tilepart.sc
            self.N_tp = tilepart.N
            self.x_gap_tp = tilepart.x_gap
            self.y_gap_tp = tilepart.y_gap
            self.support_offset_tp = tilepart.support_offset

        else:
            # define defaults
            self.sheet_opref_tp = design.operations[1].id
            self.part_opref_tp = design.operations[1].id
            self.sketch_bounding_box_tp = [(0,0),(0,0)]
            self.sc_tp = 1
            self.N_tp = 10
            self.x_gap_tp = 0
            self.y_gap_tp = 0
            self.support_offset_tp = 0

        self.build_dialog(design, prioroperations)

    def build_dialog(self, design, prioroperations):

        self.prioroperations = prioroperations
        self.design = design

        #       operation/part | sketch to tile in | sheet to tile into
        #                  'Number of parts', 'Scale'
        #                       'x-gap', 'y-gap'
        #                       'Support offset'

        self.part = DraggableTreeWidget()
        self.part.linklist(prioroperations)
        self.part.setObjectName("Operation to tile")
        # self.part.setCurrentItem(design.operation_index(self.part_opref_tp))

        self.release = DraggableTreeWidget()
        self.release.linklist(prioroperations)
        self.release.setObjectName("Release cut (optional)")
        # self.part.setCurrentItem(design.operation_index(self.part_opref_tp))

        self.sketch_to_tile = SketchListManager(design,name = 'Sketch of tile area')

        self.sheet = DraggableTreeWidget()
        self.sheet.linklist(prioroperations)
        self.sheet.setObjectName("Sheet to tile into")
        # self.sheet.setCurrentItem(design.operation_index(self.sheet_opref_tp))

        #       operation/part | sketch to tile in | sheet to tile into
        layout_ops_sheet_sketch = qg.QHBoxLayout()
        layout_ops_sheet_sketch.addWidget(self.part)
        layout_ops_sheet_sketch.addWidget(self.release)
        layout_ops_sheet_sketch.addWidget(self.sketch_to_tile)
        layout_ops_sheet_sketch.addWidget(self.sheet)

        #       'Number of parts', 'Scale'
        number_of_parts_and_scale = qg.QHBoxLayout()

        number_of_parts_and_scale.addStretch()
        number_of_parts_and_scale.addWidget(qg.QLabel('Number of parts'))
        self.N = qg.QLineEdit()
        number_of_parts_and_scale.addWidget(self.N)
        self.N.setText(str(self.N_tp))

        number_of_parts_and_scale.addWidget(qg.QLabel('Scale'))
        self.scale = qg.QLineEdit()
        number_of_parts_and_scale.addWidget(self.scale)
        number_of_parts_and_scale.addStretch()
        self.scale.setText(str(self.sc_tp))

        #                       'x-gap', 'y-gap'
        xy_gap = qg.QHBoxLayout()
        xy_gap.addStretch()

        xy_gap.addWidget(qg.QLabel('X-gap'))
        self.x_gap = qg.QLineEdit()
        self.x_gap.setText(str(self.x_gap_tp))
        xy_gap.addWidget(self.x_gap)

        xy_gap.addWidget(qg.QLabel('Y-gap'))
        self.y_gap = qg.QLineEdit()
        self.y_gap.setText(str(self.y_gap_tp))
        xy_gap.addWidget(self.y_gap)
        xy_gap.addStretch()

        s_offset = qg.QHBoxLayout()
        s_offset.addStretch()
        s_offset.addWidget(qg.QLabel('Support offset'))
        self.support_offset = qg.QLineEdit()
        self.support_offset.setText(str(self.support_offset_tp))
        s_offset.addWidget(self.support_offset)
        s_offset.addWidget(self.support_offset)
        s_offset.addStretch()

        # Button 1 and 2
        buttons = qg.QHBoxLayout()
        button1 = qg.QPushButton('Ok')
        button1.clicked.connect(self.accept)
        buttons.addWidget(button1)

        button2 = qg.QPushButton('Cancel')
        button2.clicked.connect(self.reject)
        buttons.addWidget(button2)


        layout = qg.QVBoxLayout()
        layout.addLayout(layout_ops_sheet_sketch)
        layout.addLayout(number_of_parts_and_scale)
        layout.addLayout(xy_gap)
        layout.addLayout(s_offset)
        layout.addLayout(buttons)
        self.setLayout(layout)


    def build_sketch_links(self):
        try:
            sketch_links = {}
            sketch_links['sketch_from']=[self.sketch_to_tile.itemlist.selectedItems()[0].value.id]
            return sketch_links
        except IndexError:
            return None

    def acceptdata(self):

        # get operation reference for part
        ii, jj = self.part.currentIndeces2()[0]
        opid = self.design.operations[ii].id
        part_opref = opid

        # get operation reference for sheet
        ii, jj = self.sheet.currentIndeces2()[0]
        opid = self.design.operations[ii].id
        sheet_opref = opid

        # get operation reference for release
        ii, jj = self.release.currentIndeces2()[0]
        opid = self.design.operations[ii].id
        release_opref = opid

        # get bounding box from the sketch
        sketch_id = self.sketch_to_tile.itemlist.selectedItems()[0].value.id
        sketch_bounding_box = self.design.sketches[sketch_id].output_csg()[0].bounds # may break if multiple sketches
        sketch_bounding_box = [geom/popupcad.csg_processing_scaling for geom in sketch_bounding_box]

        N = int(self.N.text())
        scale = float(self.scale.text())
        x_gap = float(self.x_gap.text())
        y_gap = float(self.y_gap.text())
        support_offset = float(self.support_offset.text())

        return part_opref, release_opref, sheet_opref, sketch_bounding_box, N, scale, x_gap, y_gap, support_offset


class TilePart(Operation2):
    name = 'TiledPart'
    show = []

    def __init__(self, *args):
        super(TilePart, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self,part_opref, release_opref, sheet_opref, sketch_bounding_box, N, scale, x_gap, y_gap, support_offset):
        super(TilePart, self).editdata({},{},{})
        self.sheet_opref = sheet_opref
        self.release_opref = release_opref
        self.part_opref = part_opref
        self.sketch_bounding_box = sketch_bounding_box
        self.sc = scale
        self.N = N
        self.x_gap = x_gap
        self.y_gap = y_gap
        self.support_offset = support_offset

    def copy(self):
        new = type(self)(
            self.part_opref,
            self.release_opref,
            self.sheet_opref,
            self.sketch_bounding_box,
            self.N,
            self.sc,
            self.x_gap,
            self.y_gap,
            self.support_offset)
        new.id = self.id
        new.customname = self.customname
        return new


    # finally initialize sketch op in design
    def operate(self, design):

        design_copy = design
        # design_copy.reprocessoperations()

        part_to_insert = design_copy.operations[design_copy.operation_index(self.part_opref)]
        sheet_to_insert_into = design_copy.operations[design_copy.operation_index(self.sheet_opref)]
        release_to_insert_into = design_copy.operations[design_copy.operation_index(self.release_opref)]

        # build the op_links, then auto make the operation
        op = part_to_insert
        op_ref = op.id
        op_links = {'parent': [(op_ref, op.getoutputref())]}

        new_web = AutoWeb4(op_links,[self.support_offset,0],MultiValueOperation3.keepout_types.laser_keepout)
        new_web.setcustomname(op.name)

        # support = OperationOutput(new_web.output[1], "support", self)

        design_copy.addoperation(new_web)
        new_web.generate(design_copy)

        ######################## generate the same size construction line somewhere in the sheet file

        # get geom for line
        parts_bounding_box = new_web.output[1].generic_laminate().getBoundingBox()
        # parts_bounding_box  = support.generic_laminate().getBoundingBox()

        # make the sketch
        construction_geom_hinge = Sketch.new()
        tmp_geom = [(parts_bounding_box[0],parts_bounding_box[1]), (parts_bounding_box[0],parts_bounding_box[3])]
        construction_line = GenericLine.gen_from_point_lists(tmp_geom,[],construction=False)
        construction_geom_hinge.addoperationgeometries([construction_line])

        # add sketch to sketch list
        design_copy.sketches[construction_geom_hinge.id] = construction_geom_hinge

        # # make the sketchop
        # construction_geom_sketchop_hinge = SimpleSketchOp({'sketch': [construction_geom_hinge.id]},
        #                                     [layer.id for layer in design_copy.return_layer_definition().layers])
        # construction_geom_sketchop_hinge.name = "ConstructionLine"
        #
        # # finally initialize sketch op in design_copy
        # design_copy.addoperation(construction_geom_sketchop_hinge)
        # construction_geom_sketchop_hinge.generate(design_copy)

        ######################## generate the external transform geometry in the sheet

        # center the locate line top left as origin
        position_hinge = (-tmp_geom[0][0],-tmp_geom[0][1])
        locate_lines = [(x + position_hinge[0], y + position_hinge[1]) for (x,y) in tmp_geom]

        # lets make 4x4
        width = (parts_bounding_box[2] - parts_bounding_box[0])*self.sc + self.x_gap
        height = (parts_bounding_box[3] - parts_bounding_box[1])*self.sc + self.y_gap


        # check if will all fit in one window, if not fill first and check if remainder will fit in second window
        max_num_cols = divmod(self.sketch_bounding_box[2] - self.sketch_bounding_box[0], width)[0]
        max_num_rows = divmod(self.sketch_bounding_box[3] - self.sketch_bounding_box[1], height)[0]

        arrayed_reference_lines = []

        # check if can fit in one
        # if N <= max_num_rows*max_num_cols:
        rows = math.ceil(self.N / max_num_cols)
        cols = math.ceil(self.N / rows)          # spread across the two windows


        # new_center = (-parts_bounding_box[0]/2, 2)
        # tmp_geom = [(x + new_center[0], y + new_center[1]) for (x,y) in tmp_geom]

        upper_right_origin_bounding_box = (self.sketch_bounding_box[0], self.sketch_bounding_box[3])

        n_count = 0

        for row in range(rows):
            for col in range(cols):
                if n_count >= self.N or n_count >= max_num_rows*max_num_cols*2:
                    break

                newx = upper_right_origin_bounding_box[0] + locate_lines[0][0] + col*width
                newy = upper_right_origin_bounding_box[1] - locate_lines[1][1] - row*height

                arrayed_reference_lines.append([(newx, newy), (newx, newy + height)])

                n_count = n_count + 1

        construction_geom_sheet = Sketch.new()
        construction_line = [GenericLine.gen_from_point_lists(line,[],construction=False) for
                     line in arrayed_reference_lines]
        construction_geom_sheet.addoperationgeometries(construction_line)

        # add sketch to sketch list
        design_copy.sketches[construction_geom_sheet.id] = construction_geom_sheet

        # # make the sketchop
        # construction_geom_sketchop_sheet = SimpleSketchOp({'sketch': [construction_geom_sheet.id]},
        #                                     [layer.id for layer in design_copy.return_layer_definition().layers])
        # construction_geom_sketchop_sheet.name = "ConstructionLine"

        # # finally initialize sketch op in design_copy
        # design_copy.addoperation(construction_geom_sketchop_sheet)
        # construction_geom_sketchop_sheet.generate(design_copy)

        ######################## External transform the hinge onto the sheet construction line

        # # insert hinge into sheet as subdesign
        # sheet.subdesigns[hinge.id] = hinge

        # # make design links
        operation_links = {}
        operation_links['from'] = [(part_to_insert.id,0)]

        sketch_links = {}
        sketch_links['sketch_to'] = [construction_geom_sheet.id]
        sketch_links['sketch_from'] = [construction_geom_hinge.id]

        insert_part = TransformInternal(sketch_links, operation_links, 'scale', 'scale', 0, False, 1., 1.)
        insert_part.customname = 'Inserted part'

        design_copy.addoperation(insert_part)
        insert_part.generate(design_copy)
        insert_part_id = design_copy.operations[-1].id # save for later

        ######################## External transform the web.sheet to the construction line

        # # make design links
        operation_links = {}
        operation_links['from'] = [(new_web.id,1)]

        sketch_links = {}
        sketch_links['sketch_to'] = [construction_geom_sheet.id]
        sketch_links['sketch_from'] = [construction_geom_hinge.id]

        insert_webs = TransformInternal(sketch_links, operation_links, 'scale', 'scale', 0, False, 1., 1.)
        insert_webs.customname = 'Inserted part webs'

        design_copy.addoperation(insert_webs)
        insert_webs.generate(design_copy)

        ######################## Remove web.sheet from sheet, union external transform + generateed sheet with hole + web
        # first the difference
        # link 1 is the sheet
        sheet_with_hole = LaminateOperation2({'unary': [(sheet_to_insert_into.id,0)], 'binary': [(insert_webs.id,0)]},'difference')
        sheet_with_hole.customname = 'Sheet with hole'
        design_copy.addoperation(sheet_with_hole)
        sheet_with_hole.generate(design_copy)

        sheet_with_part = LaminateOperation2({'unary': [(sheet_with_hole.id,0), (insert_part_id,0)],
                                      'binary':[]},'union')

        sheet_with_part.customname = 'First pass cuts'
        design_copy.addoperation(sheet_with_part)
        sheet_with_part.generate(design_copy)

        # ######################## Make release cut laminate operation


        operation_links = {}
        operation_links['from'] = [(release_to_insert_into.id,0)]

        sketch_links = {}
        sketch_links['sketch_to'] = [construction_geom_sheet.id]
        sketch_links['sketch_from'] = [construction_geom_hinge.id]

        insert_release = TransformInternal(sketch_links, operation_links, 'scale', 'scale', 0, False, 1., 1.)

        design.addoperation(insert_release)
        insert_release.generate(design)

        ######################################### prepare outputs

        # delete the intermediate layers
        design.remove_operation(sheet_with_hole)
        design.remove_operation(insert_webs)
        design.remove_operation(insert_part)
        design.remove_operation(new_web)
        design.remove_operation(sheet_with_part)
        design.remove_operation(insert_release)

        self.output = [OperationOutput(sheet_with_part.output[0].csg, 'FirstCuts', self),
                       OperationOutput(sheet_with_part.output[0].csg, 'FirstCuts', self),
                       OperationOutput(insert_release.output[0].csg, 'Release', self)]

        return sheet_with_part.output[0].csg

        # probably a memory leak here not deleting design_copy


    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = Dialog(design, design.operations, None)
        return dialog

    def buildeditdialog(self, design):
        dialog = Dialog(design,design.operations, self)
        return dialog