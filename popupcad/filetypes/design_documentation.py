# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import os

template = \
'''---
{0}
---
'''

def process_output(output, filename_in, destination):

    generic = output.csg.to_generic_laminate()

    png_image_file = generic.raster(filename_in,'png',destination)
    png_image_file = os.path.split(png_image_file)[1]

    svg_image_file = generic.to_svg(filename_in+'.svg',destination)
    svg_image_file = os.path.split(svg_image_file)[1]

    name = str(output)

    output_dict = {}
    output_dict['name'] = name 
    output_dict['svg_image_file'] = svg_image_file 
    output_dict['png_image_file'] = png_image_file 
    output_dict['description'] = output.description 
    output_dict['cut_files'] = ['cut-dummy1.svg','cut-dummy2.svg']
    return output_dict

def process_operation(operation, ii, destination):
    name = str(operation)

    outputs = []
    for jj, out in enumerate(operation.output):
        filename = '{0:02.0f}_{1:02.0f}'.format(ii, jj)
        outputs.append(process_output(out, filename, destination))

    output = {}
    output['name'] = name
#    output['description'] = operation.description
    output['description'] = 'This is a fake operation description.  I am not about to make a separate description for each op, but the description might be about this long.'
    output['svg_image_file'] = outputs[0]['svg_image_file']
    output['png_image_file'] = outputs[0]['png_image_file']
    output['cut_files'] = outputs[0]['cut_files']
    output['outputs'] = outputs[1:]
    return output
    
def process_design(design,subdir):
    title = design.get_basename()
    operations = [process_operation(operation, ii, subdir) for ii, operation in enumerate(design.operations)]

    ii = design.operation_index(design.main_operation[0])

    output = {}
    output['title'] = title
    output['description'] = 'This is a leg design, which is meant to be attached to the body of a robot.  It is a 2-dof mechanism, so requires inputs from two motors.  Operation 10 and 12 include the necessary cut files for creating this two-laminate device.'
    output['category'] = 'Parts.Legs.2DOFLegs'
    output['tags'] = 'parts,legs,2dof_robot_legs'
    output['operations'] = operations
    output['svg_image_file'] = operations[ii]['svg_image_file']
    output['png_image_file'] = operations[ii]['png_image_file']
    output['cad_file'] = design.get_basename()
    return output

def format_template(design_dict):
    import yaml
    output = template.format(yaml.dump(design_dict))
    return output
    