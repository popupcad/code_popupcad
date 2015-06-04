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

{{% for operation in page.operations %}}

* [<img src="{{{{operation.image_file}}}}" height = "75px" />]({{{{operation.image_file}}}}) **{{{{ operation.name }}}}** {{{{operation.description}}}}

{{% for output in operation.outputs %}}
  * [<img src="{{{{output.image_file}}}}" height = "50px" />]({{{{output.image_file}}}}) **{{{{output.name}}}}** {{{{output.description}}}}

{{% endfor %}}
{{% endfor %}}
'''

class Documentation(object):
    def dictify(self):
        return dict([(item,getattr(self,item)) for item in self.export_keys])

#    @classmethod
#    def undictify(cls,item):
#        new = cls()
#        new.a=item['a']        
#        new.b=item['b']        

    @staticmethod
    def yaml_representer(dumper,v):
        output = dumper.represent_mapping(v.yaml_node_name,v.dictify())
        return output
    
#    @classmethod
#    def yaml_constructor(cls,loader, node):
#        dict1 = loader.construct_mapping(node)
#        new = cls.undictify(dict1)
#        return new

def process_output(output,ii,jj,destination):
    filename_in = '{0:02.0f}_{1:02.0f}'.format(ii,jj)
    filename_out = output.generic_laminate().raster(filename_in,'png',destination)
    name = str(output)
    return {'name':name,'image_file':filename_out,'description':output.description}


class OperationDocumentation(Documentation):
    yaml_node_name = u'Operation'
    export_keys = ['name','description','image_file','outputs']
    @classmethod
    def build(cls,operation,ii,destination):
        outputs = []
        image_file = process_output(operation.output[0],ii,0,destination)['image_file']
        for jj,out in enumerate(operation.output[1:]):
            outputs.append(process_output(out,ii,jj,destination))
        return cls(str(operation),operation.description,image_file,outputs)

    def __init__(self,name,description,image_file,outputs):
        super(OperationDocumentation,self).__init__()
        self.name = name
        self.description = description
        self.image_file = image_file,
        self.outputs = outputs
        
class DesignDocumentation(popupCADFile,Documentation):
    filetypes = {'docu':'Design Documentation'}
    defaultfiletype = 'docu'
    yaml_node_name = u'Documentation'
    export_keys = ['title','name','operations']
    @classmethod
    def build(cls,design,subdir):
        title = design.get_basename()
        name = design.get_basename()
        operations = [OperationDocumentation.build(operation,ii,subdir) for ii,operation in enumerate(design.operations)]
        return cls(title,name,operations)
        
    def __init__(self,title,name,operations):
        super(DesignDocumentation,self).__init__()
        self.title = title
        self.name = name
        self.operations = operations


    def copy(self,identical=True):
        new = type(self)(self.operations)
        return new
        
    def dictify2(self):
        output = {}
        output['title']=self.title
        output['name']=self.name
        output['operations']=[item.dictify() for item in self.operations]
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
