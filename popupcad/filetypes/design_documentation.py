# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.popupcad_file import popupCADFile

template = \
    '''---
{0}
---

Hello, this is a test

my relative directory is {{{{collection.relative_directory}}}}

My collection is {{{{page.collection}}}}

I have this many files {{{{page.files}}}}

My name is {{{{page.name}}}}

My title is {{{{page.title}}}}

[<img src="{{{{page.png_image_file}}}}" />]({{{{page.cad_file}}}})

{{% for operation in page.operations %}}

* [<img src="{{{{operation.png_image_file}}}}" height = "75px" />]({{{{operation.png_image_file}}}}) **{{{{ operation.name }}}}** {{{{operation.description}}}} 
{{% for file in operation.cut_files%}}
[{{{{file}}}}]({{{{file}}}}),
{{% endfor %}}

{{% for output in operation.outputs %}}
  * [<img src="{{{{output.png_image_file}}}}" height = "50px" />]({{{{output.png_image_file}}}}) **{{{{output.name}}}}** {{{{output.description}}}}
{{% for file in output.cut_files%}}
[{{{{file}}}}]({{{{file}}}}),
{{% endfor %}}


{{% endfor %}}
{{% endfor %}}
'''


class Documentation(object):

    def dictify(self):
        return dict([(item, getattr(self, item)) for item in self.export_keys])

#    @classmethod
#    def undictify(cls,item):
#        new = cls()
#        new.a=item['a']
#        new.b=item['b']

    @staticmethod
    def yaml_representer(dumper, v):
        output = dumper.represent_mapping(v.yaml_node_name, v.dictify())
        return output

#    @classmethod
#    def yaml_constructor(cls,loader, node):
#        dict1 = loader.construct_mapping(node)
#        new = cls.undictify(dict1)
#        return new


def process_output(output, ii, jj, destination):
    filename_in = '{0:02.0f}_{1:02.0f}'.format(ii, jj)
    png_filename_out = output.generic_laminate().raster(
        filename_in,
        'png',
        destination)

    svg_filename_out = output.generic_laminate().to_svg(filename_in+'.svg',destination)

    name = str(output)
    return {
        'name': name,
        'svg_image_file': svg_filename_out,
        'png_image_file': png_filename_out,
        'description': output.description,
        'cut_files': ['cut-dummy1.svg','cut-dummy2.svg']}


class OperationDocumentation(Documentation):
    yaml_node_name = u'Operation'
    export_keys = ['name', 'description', 'svg_image_file','png_image_file', 'cut_files', 'outputs']

    @classmethod
    def build(cls, operation, ii, destination):
        outputs = []
        out0 = process_output(operation.output[0], ii, 0, destination)
        svg_image_file = out0['svg_image_file']
        png_image_file = out0['png_image_file']
        cut_files = out0['cut_files']
        for jj, out in enumerate(operation.output[1:]):
            outputs.append(process_output(out, ii, jj, destination))
        return cls(str(operation),operation.description, svg_image_file, png_image_file,cut_files,outputs)

    def __init__(self, name, description, svg_image_file, png_image_file, cut_files, outputs):
        super(OperationDocumentation, self).__init__()
        self.name = name
        self.description = 'This is a fake operation description.  I am not about to make a separate description for each op, but the description might be about this long.'
        self.svg_image_file = svg_image_file
        self.png_image_file = png_image_file
        self.cut_files = cut_files
        self.outputs = outputs


class DesignDocumentation(popupCADFile, Documentation):
    filetypes = {'docu': 'Design Documentation'}
    defaultfiletype = 'docu'
    yaml_node_name = u'Documentation'
    export_keys = ['title', 'name', 'operations']

    @classmethod
    def build(cls, design, subdir):
        title = design.get_basename()
        operations = [
            OperationDocumentation.build(
                operation, ii, subdir) for ii, operation in enumerate(
                design.operations)]

        ii = design.operation_index(design.main_operation[0])
        svg_image_file = operations[ii].svg_image_file
        png_image_file = operations[ii].png_image_file
        cad_file = design.get_basename()
        return cls(title, operations, svg_image_file,png_image_file,cad_file)

    def __init__(self, title, operations,svg_image_file,png_image_file,cad_file):
        super(DesignDocumentation, self).__init__()
        self.title = title
        self.operations = operations
        self.svg_image_file = svg_image_file
        self.png_image_file = png_image_file
        self.cad_file = cad_file

    def copy(self, identical=True):
        new = type(self)(self.operations)
        return new

    def dictify2(self):
        output = {}
        output['title'] = self.title
        output['description'] = 'This is a leg design, which is meant to be attached to the body of a robot.  It is a 2-dof mechanism, so requires inputs from two motors.  Operation 10 and 12 include the necessary cut files for creating this two-laminate device.'
        output['category'] = 'Parts.Legs.2DOFLegs'
        output['tags'] = 'parts,legs,2dof_robot_legs'
        output['operations'] = [item.dictify() for item in self.operations]
        output['svg_image_file'] = self.svg_image_file
        output['png_image_file'] = self.png_image_file
        output['cad_file'] = self.cad_file
        return output

    def output(self):
        import yaml
        output = template.format(yaml.dump(self.dictify2()))
#        output = output.split('\n')
        return output

#import yaml
#yaml.add_representer(OperationDocumentation, OperationDocumentation.yaml_representer)
#yaml.add_representer(DesignDocumentation, DesignDocumentation.yaml_representer)
##yaml.add_constructor(DesignDocumentation.yaml_node_name, DesignDocumentation.yaml_constructor)
