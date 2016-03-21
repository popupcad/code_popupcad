# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import popupcad
from popupcad.filetypes.sketch import Sketch
import numpy
import sys

import qt.QtCore as qc
import qt.QtGui as qg
from popupcad_manufacturing_plugins.manufacturing.outersheet3 import OuterSheet3

def find_sketch_with_string(design,string):
    sketches = []
    for key,value in design.sketches.items():
        if string.lower() in value.get_basename().lower():
            sketches.append(value)
    return sketches

if __name__=='__main__':
    
    app = qg.QApplication(sys.argv)
    
    top_design = popupcad.filetypes.design.Design.new()
    top_design.define_layers(popupcad.filetypes.layerdef.LayerDef(*popupcad.filetypes.material2.default_sublaminate))
    
    single_layer_joint_manufacturing = popupcad.filetypes.design.Design.load_yaml('jointed_robot_subdesign.cad')
    sub_body_sketch = find_sketch_with_string(single_layer_joint_manufacturing,'body')[0]
    sub_joint_sketch = find_sketch_with_string(single_layer_joint_manufacturing,'joint')[0]
    
    devices = {}
    device_links = {'unary': [], 'binary': []}
    sheet_links= {'unary': [], 'binary': []}
    first_cut_links= {'unary': [], 'binary': []}
    second_cut_links= {'unary': [], 'binary': []}
    
    ii = 0
    while ii<5:
        points = numpy.random.rand(5,2)*20+[ii*20,0]
        body_polygon = popupcad.algorithms.triangulate.convex_hull(points)
        area,centroid,volume,mass,tris = body_polygon.mass_properties(1,-1,1,popupcad.SI_length_scaling)
        centroid = centroid[:2].tolist()
    #    
        points = numpy.array(body_polygon.exteriorpoints()+[centroid])
        body_triangles= popupcad.algorithms.triangulate.triangulate(points)
        generic_lines = popupcad.algorithms.getjoints.getjoints(body_triangles,5)
        
        body_sketch = Sketch.new()
        body_sketch.addoperationgeometries([body_polygon])
        joints_sketch = Sketch.new()
        joints_sketch.addoperationgeometries(generic_lines)
        
        
        top_design.subdesigns[single_layer_joint_manufacturing.id] = single_layer_joint_manufacturing
        top_design.sketches[body_sketch.id] = body_sketch
        top_design.sketches[joints_sketch.id] = joints_sketch
        
        design_links = {}
        design_links['source'] = [single_layer_joint_manufacturing.id]
        sketch_list = []
        sketch_list.append(popupcad.manufacturing.sub_operation2.SketchData(sub_body_sketch.id,body_sketch.id))
        sketch_list.append(popupcad.manufacturing.sub_operation2.SketchData(sub_joint_sketch.id,joints_sketch.id))
        input_list = []
        output_list = []
        output_list.append(popupcad.manufacturing.sub_operation2.OutputData((single_layer_joint_manufacturing.operations[3].id,0),0))
        output_list.append(popupcad.manufacturing.sub_operation2.OutputData((single_layer_joint_manufacturing.operations[5].id,0),0))
        output_list.append(popupcad.manufacturing.sub_operation2.OutputData((single_layer_joint_manufacturing.operations[8].id,0),0))
        output_list.append(popupcad.manufacturing.sub_operation2.OutputData((single_layer_joint_manufacturing.operations[9].id,0),0))
        
        subop = popupcad.manufacturing.sub_operation2.SubOperation2(design_links, sketch_list, input_list, output_list)
        try:
            subop.generate(top_design)
            top_design.addoperation(subop)
            device_links['unary'].append((subop.id,0))
            sheet_links['unary'].append((subop.id,1))
            first_cut_links['unary'].append((subop.id,2))
            second_cut_links['unary'].append((subop.id,3))
            ii+=1
        except:
            pass
    
    devices = popupcad.manufacturing.laminateoperation2.LaminateOperation2(device_links,'union')
    devices.customname = 'Devices'
    sheets = popupcad.manufacturing.laminateoperation2.LaminateOperation2(sheet_links,'union')
    sheets.customname = 'Sheets'
    first_passes = popupcad.manufacturing.laminateoperation2.LaminateOperation2(first_cut_links,'union')
    sheet = OuterSheet3({'parent':[(sheets.id,0)]},[1],OuterSheet3.keepout_types.laser_keepout)
    sheet_with_holes = popupcad.manufacturing.laminateoperation2.LaminateOperation2({'unary': [(sheet.id,0)], 'binary': [(sheets.id,0)]},'difference')
    first_pass = popupcad.manufacturing.laminateoperation2.LaminateOperation2({'unary': [(sheet_with_holes.id,0),(first_passes.id,0)], 'binary': []},'union')
    first_pass.customname='First Pass'
    second_passes = popupcad.manufacturing.laminateoperation2.LaminateOperation2(second_cut_links,'union')
    second_passes.customname = 'Second Pass' 
    
    other_ops = [devices,sheets,first_passes,sheet,sheet_with_holes,first_pass,second_passes]
    [top_design.addoperation(item) for item in other_ops]
    [item.generate(top_design) for item in other_ops]
    
    editor = popupcad.guis.editor.Editor()
    editor.load_design(top_design)
    editor.show()
    sys.exit(app.exec_())
