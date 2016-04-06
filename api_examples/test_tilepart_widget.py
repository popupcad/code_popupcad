
import qt.QtGui as qg
import popupcad
from popupcad_manufacturing_plugins.manufacturing.tilepart import TilePart
import os
import sys

# file to load and work with
myfolder  = '/Users/nickgravish/popupCAD_files/designs'
design_file    = 'Transmissions.cad' #'robobee_interference_hinge.cad'

if __name__=='__main__':

    app = qg.QApplication(sys.argv)

    design = popupcad.filetypes.design.Design.load_yaml(os.path.join(myfolder, design_file))
    design.reprocessoperations(debugprint=True) ## IMPORTANT
    #part_opref, sheet_opref, sketch_bounding_box, N, scale, x_gap, y_gap, support_offset

    release = design.operations[-3].id
    part_opref = design.operations[-2].id
    sheet_opref = design.operations[-1].id
    sketch_id = 4762336016  #4751474000

    scaling = popupcad.csg_processing_scaling
    sketch_bounding_box = design.sketches[sketch_id].output_csg()[0].bounds # may break if multiple sketches
    sketch_bounding_box = [geom/scaling for geom in sketch_bounding_box]

    N = 10
    scale = 1.
    x_gap = 0.
    y_gap = 0.
    support_offset = 0.

    new = TilePart(part_opref, release, sheet_opref, sketch_bounding_box, N, scale, x_gap, y_gap, support_offset)

    design.addoperation(new)
    new.operate(design)

    ################## show the new design

    editor = popupcad.guis.editor.Editor()
    editor.load_design(design)
    editor.show()
    sys.exit(app.exec_())