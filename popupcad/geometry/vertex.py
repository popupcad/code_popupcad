# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import numpy
from popupcad.constraints.constraint_support import SymbolicVertex
import popupcad
import shapely.geometry as sg

class BaseVertex(object):
    editable = ['position']
    hidden = ['roundvalue,yaml_node_name']
    deletable = []

    roundvalue = popupcad.geometry_round_value

    def __init__(self, position,scaling = 1):
        self.id = id(self)
        self.setpos(position,scaling)
        
    def variables(self):
        my_id = str(self.id)
        return my_id+'.x',my_id+'.y'

    def constraints_ref(self):
        try:
            return self._constraints_ref
        except AttributeError:
            self._constraints_ref = SymbolicVertex(self.id)
            return self._constraints_ref

    def isValid(self):
        return True

    def __str__(self):
        return 'vertex' + str(self.id) +str(self.getpos())
        
    def __repr__(self):
        return str(self)

    def vertices(self):
        return [self]

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.id == other.id
        return False

    def p(self):
        return self.constraints_ref().p()

    def setpos(self, pos,scaling = 1):
        pos = numpy.array(pos)*scaling
#        pos = pos.round(self.roundvalue)
        self._position = tuple(pos.tolist())

    def round(self, identical = False, decimal_places = None):
        if decimal_places is None:
            decimal_places = popupcad.geometry_round_value

        pos = numpy.array(self.getpos()).round(decimal_places)
        new = type(self)(pos)
        if identical:
            new.id = self.id
        return new

    def getpos(self, scaling=1):
        try:
            return self.scale_tuple(self._position,scaling)
        except AttributeError:
            if hasattr(self,'_pos') and (self._pos is not None):
                self._position = self.scale_tuple(self._pos,1/popupcad.deprecated_internal_argument_scaling )
                del self._pos
            elif hasattr(self,'__pos'):
                self._position = self.scale_tuple(self.__pos,1/popupcad.deprecated_internal_argument_scaling )
                del self.__pos
            elif hasattr(self,'_Vertex__pos'):
                self._position = self.scale_tuple(self._Vertex__pos,1/popupcad.deprecated_internal_argument_scaling )
                del self._Vertex__pos
            else:
                raise Exception
            return self.scale_tuple(self._position,scaling)
    position = property(getpos,setpos)
    
    @staticmethod
    def scale_tuple(value, scale):
        if scale != 1:
            value = tuple([item * scale for item in value])
        return value

    def getpos3D(self):
        return tuple(numpy.r_[self.getpos(),0].tolist())

    def setsymbol(self, variable, value):
        p = self.constraints_ref().p()
        if p[0] == variable:
            self.setpos((value, self.getpos()[1]))
        if p[1] == variable:
            self.setpos((self.getpos()[0], value))

    def properties(self):
        from idealab_tools.propertyeditor import PropertyEditor
        return PropertyEditor(self)

    def copy(self, identical=True):
        new = type(self)(self.getpos())
        if identical:
            new.id = self.id
        return new

    def upgrade(self, *args, **kwargs):
        return self

    def is_equal(self, other, tolerance = None):
        import popupcad.algorithms.points as points
        if tolerance is None:
            tolerance = popupcad.distinguishable_number_difference

        if isinstance(self, type(other)):
            return points.twopointsthesame(self.getpos(),other.getpos(),tolerance)
        return False

    def rounded_is_equal(self, other, decimal_places = None):
        import popupcad.algorithms.points as points

        if decimal_places is None:
            decimal_places = popupcad.geometry_round_value
        if isinstance(self, type(other)):
            return points.rounded_equal(self.getpos(),other.getpos(),decimal_places)
        return False

    def is_identical(self, other):
        import popupcad.algorithms.points as points
        if isinstance(self, type(other)):
            return points.identical(self.getpos(),other.getpos())
        return False

    def scale(self, m):
        pos = numpy.array(self.getpos())
        self.setpos(m*pos)

    def shift(self, dxdy):
        pos = numpy.array(self.getpos())
        dxdy = numpy.array(dxdy)
        newpos = pos + dxdy
        self.setpos(newpos)

    def constrained_shift(self, dxdy, constraintsystem):
        constraintsystem.constrained_shift([(self, dxdy)])

    @classmethod
    def delistify_0(cls, id, x, y):
        new = cls((x/popupcad.deprecated_internal_argument_scaling, y/popupcad.deprecated_internal_argument_scaling))
        new.id = id
        return new

    @classmethod
    def delistify_1(cls, id, x, y):
        new = cls((x, y))
        new.id = id
        return new

    def listify(self):
        x, y = self.getpos()
        output = [self.id, x, y]
        return output

    @staticmethod
    def vertex_representer(dumper, v):
        output = dumper.represent_sequence(v.yaml_node_name_1, v.listify())
        return output

    @classmethod
    def vertex_constructor_0(cls, loader, node):
        list1 = loader.construct_sequence(node)
        new = cls.delistify_0(*list1)
        return new

    @classmethod
    def vertex_constructor_1(cls, loader, node):
        list1 = loader.construct_sequence(node)
        new = cls.delistify_1(*list1)
        return new

class ReferenceVertex(BaseVertex):
    def gen_interactive(self):
        from popupcad.graphics2d.interactivevertex import ReferenceInteractiveVertex
        iv = ReferenceInteractiveVertex(self)
        iv.updateshape()
        return iv

class ShapeVertex(BaseVertex):
    yaml_node_name_0 = u'!ShapeVertex'
    yaml_node_name_1 = u'!ShapeVertex_1'

    def gen_interactive(self):
        from popupcad.graphics2d.interactivevertex import InteractiveShapeVertex
        iv = InteractiveShapeVertex(self)
        iv.updateshape()
        return iv

#TODO: does DrawnPoint really need to be a child class of ShapeVertex, or can it be a child of BaseVertex?
class DrawnPoint(BaseVertex):
    editable = ShapeVertex.editable + ['construction']
    yaml_node_name_0 = u'!DrawnPoint'
    yaml_node_name_1 = u'!DrawnPoint_1'

    def __init__(self,position,scaling = 1,construction = False):
        super(DrawnPoint, self).__init__(position,scaling)
        self.set_construction(construction)

    def exteriorpoints(self,scaling = 1):
        return [self.getpos(scaling)]

    def interiorpoints(self):
        return []

    def gen_interactive(self):
        from popupcad.graphics2d.interactivevertex import DrawingPoint
        iv = DrawingPoint(self)
        iv.updateshape()
        return iv

    def points(self):
        return [self.getpos()]

    def segments(self):
        return []

    def segmentpoints(self):
        return []

    def outputinteractive(self):
        from popupcad.graphics2d.interactivevertex import DrawingPoint
        iv = DrawingPoint(self)
        iv.updateshape()
        return iv

    def outputstatic(self, *args, **kwargs):
        from popupcad.graphics2d.interactivevertex import StaticDrawingPoint
        iv = StaticDrawingPoint(self)
        iv.updateshape()
        return iv

    def to_shapely(self):
        p = sg.Point(*self.getpos(scaling = popupcad.csg_processing_scaling))
        return p

    def is_construction(self):
        try:
            return self.construction
        except AttributeError:
            self.construction = False
            return self.construction

    def set_construction(self, test):
        self.construction = test

    def copy(self, identical=True):
        new = type(self)(self.getpos(),construction = self.is_construction())
        if identical:
            new.id = self.id
        return new

    def output_dxf(self,model_space,layer = None):
        dxfattribs = {}
        if layer is not None:
            dxfattribs['layer']=layer
        model_space.add_point(self.getpos(),dxfattribs = dxfattribs)    
    @classmethod
    def delistify_0(cls, id, x, y, is_construction):
        new = cls((x/popupcad.deprecated_internal_argument_scaling, y/popupcad.deprecated_internal_argument_scaling))
        new.id = id
        new.set_construction(is_construction)
        return new

    @classmethod
    def delistify_1(cls, id, x, y, is_construction):
        new = cls((x, y))
        new.id = id
        new.set_construction(is_construction)
        return new

    def listify(self):
        x, y = self.getpos()
        output = [self.id, x, y, self.is_construction()]
        return output

import yaml

yaml.add_representer(ShapeVertex, ShapeVertex.vertex_representer)
yaml.add_constructor(ShapeVertex.yaml_node_name_0,ShapeVertex.vertex_constructor_0)
yaml.add_constructor(ShapeVertex.yaml_node_name_1,ShapeVertex.vertex_constructor_1)
yaml.add_representer(DrawnPoint, DrawnPoint.vertex_representer)
yaml.add_constructor(DrawnPoint.yaml_node_name_0, DrawnPoint.vertex_constructor_0)
yaml.add_constructor(DrawnPoint.yaml_node_name_1, DrawnPoint.vertex_constructor_1)
