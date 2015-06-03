# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.popupcad_file import popupCADFile

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

class OperationDocumentation(Documentation):
    yaml_node_name = u'Operation'
    export_keys = ['name','description','image_filename']
    @classmethod
    def build(cls,operation):
        return cls(str(operation),'This is the description','asdf.jpg')
        
    def __init__(self,name,description,image_filename):
        self.name = name
        self.description = description
        self.image_filename = image_filename
        
class DesignDocumentation(popupCADFile,Documentation):
    filetypes = {'docu':'Design Documentation'}
    defaultfiletype = 'docu'
    yaml_node_name = u'Documentation'
    export_keys = ['operations']
    @classmethod
    def build(cls,design):
        operations = [OperationDocumentation.build(operation) for operation in design.operations]
        return cls(operations)
        
    def __init__(self,operations):
        self.operations = operations

    def copy(self,identical=True):
        new = type(self)(self.operations)
        return new
        

import yaml
yaml.add_representer(OperationDocumentation, OperationDocumentation.yaml_representer)
yaml.add_representer(DesignDocumentation, DesignDocumentation.yaml_representer)
#yaml.add_constructor(DesignDocumentation.yaml_node_name, DesignDocumentation.yaml_constructor)
