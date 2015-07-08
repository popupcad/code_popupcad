# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

import numpy
from popupcad.filetypes.constraints import SymbolicVertex
import popupcad

class BaseVertex(object):
    editable = ['pos']
    deletable = []

    roundvalue = popupcad.geometry_round_value

    def __init__(self, position):
        self.id = id(self)
        self.setpos(position)

    def constraints_ref(self):
        try:
            return self._constraints_ref
        except AttributeError:
            self._constraints_ref = SymbolicVertex(self.id)
            return self._constraints_ref

    def isValid(self):
        return True

    def is_equal(self, other, tolerance):
        import popupcad.algorithms.points as points
        if isinstance(self, type(other)):
            return points.twopointsthesame(
                self.getpos(),
                other.getpos(),
                tolerance)
        return False

    def __str__(self):
        return 'vertex' + str(self.id)

    def vertices(self):
        return [self]

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.id == other.id
        return False

    def p(self):
        return self.constraints_ref().p()

    def setpos(self, pos):
        pos = numpy.array(pos)
        pos.round(self.roundvalue)
        self._position = tuple(pos.tolist())

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
        from dev_tools.propertyeditor import PropertyEditor
        return PropertyEditor(self)

    def copy(self, identical=True):
        new = type(self)(self.getpos())
        if identical:
            new.id = self.id
        return new

    def upgrade(self, *args, **kwargs):
        return self

    def shape_is_equal(self, other):
        from popupcad.filetypes.genericshapebase import GenericShapeBase
        tolerance = GenericShapeBase.tolerance
        import popupcad.algorithms.points as points
        if isinstance(self, type(other)):
            return points.twopointsthesame(
                self.getpos(),
                other.getpos(),
                tolerance)
        return False

    def shift(self, dxdy):
        pos = numpy.array(self.getpos())
        dxdy = numpy.array(dxdy)
        newpos = pos + dxdy
        self.setpos(newpos)

    def constrained_shift(self, dxdy, constraintsystem):
        constraintsystem.constrained_shift([(self, dxdy)])

    @classmethod
    def delistify(cls, id, x, y):
        new = cls((x, y))
        new.id = id
        return new

    def listify(self):
        x, y = self.getpos()
        output = [self.id, x, y]
        return output

    @staticmethod
    def vertex_representer(dumper, v):
        output = dumper.represent_sequence(v.yaml_node_name, v.listify())
        return output

    @classmethod
    def vertex_constructor(cls, loader, node):
        list1 = loader.construct_sequence(node)
        new = cls.delistify(*list1)
        return new

class ReferenceVertex(BaseVertex):
    yaml_node_name = u'!ReferenceVertex'

    def gen_interactive(self):
        from popupcad.graphics2d.interactivevertex import ReferenceInteractiveVertex
        iv = ReferenceInteractiveVertex(self)
        iv.updateshape()
        return iv

class ShapeVertex(BaseVertex):
    yaml_node_name = u'!ShapeVertex'

    def gen_interactive(self):
        from popupcad.graphics2d.interactivevertex import InteractiveShapeVertex
        iv = InteractiveShapeVertex(self)
        iv.updateshape()
        return iv

#TODO: does DrawnPoint really need to be a child class of ShapeVertex, or can it be a child of BaseVertex?
class DrawnPoint(ShapeVertex):
    editable = ShapeVertex.editable + ['construction']
    yaml_node_name = u'!DrawnPoint'

    def __init__(self,position,construction = True):
        super(DrawnPoint, self).__init__(position)
        self.set_construction(construction)

    def exteriorpoints(self):
        return [self.getpos()]

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

    def outputshapely(self):
        from popupcad.geometry.customshapely import ShapelyPoint
#        from shapely.geometry import Point
        p = ShapelyPoint(*self.getpos())
        return p

    def is_construction(self):
        try:
            return self.construction
        except AttributeError:
            self.construction = True
            return self.construction

    def set_construction(self, test):
        self.construction = test

    def copy(self, identical=True):
        new = type(self)(self.getpos(),self.is_construction())
        if identical:
            new.id = self.id
        return new

    def output_dxf(self,model_space,layer = None):
        pass
    
    @classmethod
    def delistify(cls, id, x, y, is_construction):
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
yaml.add_constructor(ShapeVertex.yaml_node_name,ShapeVertex.vertex_constructor)
yaml.add_representer(DrawnPoint, DrawnPoint.vertex_representer)
yaml.add_constructor(DrawnPoint.yaml_node_name, DrawnPoint.vertex_constructor)
#yaml.add_representer(ReferenceVertex, ReferenceVertex.vertex_representer)
#yaml.add_constructor(ReferenceVertex.yaml_node_name,ReferenceVertex.vertex_constructor)
