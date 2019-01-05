# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


import numpy
from popupcad.filetypes.genericshapes import GenericPoly
from popupcad.filetypes.genericshapebase import NotSimple, ShapeInvalid, GenericShapeBase
import popupcad

import qt.QtCore as qc
import qt.QtGui as qg
from popupcad.filetypes.popupcad_file import popupCADFile

class Loop(object):

    def __init__(self, loop, geom):
        self.loop = loop
        self.geom = geom


class Face(object):
    pass


class Component(object):
    pass


class Assembly(popupCADFile):
    file_filter = 'Yaml File(*.yaml)'
    selected_filter = 'Yaml File(*.yaml)'
    defaultfiletype = 'yaml'

    @classmethod
    def lastdir(cls):
        return popupcad.lastimportdir

    @classmethod
    def setlastdir(cls, directory):
        popupcad.lastimportdir = directory

    def convert(
            self,
            parent=None,
            scalefactor=1.,
            area_ratio=1e-3,
            colinear_tol=1e-1,
            bufferval=0.,
            cleanup=.01):
        ok1 = True
        ok2 = True
        ok3 = True
        ok4 = True
        ok5 = True
        if scalefactor is None:
            scalefactor, ok1 = qg.QInputDialog.getDouble(
                parent, 'Scale Factor', 'Scale Factor', 1, 0, popupcad.gui_positive_infinity, decimals=popupcad.gui_default_decimals)

        if area_ratio is None:
            area_ratio, ok2 = qg.QInputDialog.getDouble(
                parent, 'Area Ratio', 'Area Ratio', .001, 0, popupcad.gui_positive_infinity, decimals=popupcad.gui_default_decimals)

        if colinear_tol is None:
            colinear_tol, ok3 = qg.QInputDialog.getDouble(
                parent, 'Colinear Tolerance', 'Colinear Tolerance', 1e-8, 0, popupcad.gui_positive_infinity, decimals=popupcad.gui_default_decimals)

        if bufferval is None:
            bufferval, ok4 = qg.QInputDialog.getDouble(
                parent, 'Buffer', 'Buffer', 0, popupcad.gui_negative_infinity, popupcad.gui_positive_infinity, decimals=popupcad.gui_default_decimals)

        if cleanup is None:
            cleanup, ok5 = qg.QInputDialog.getDouble(
                parent, 'Simplify', 'Simplify', 0.0, 0, popupcad.gui_positive_infinity, decimals=popupcad.gui_default_decimals)

        if ok1 and ok2 and ok3 and ok4 and ok5:
            self._convert(
                scalefactor,
                area_ratio,
                colinear_tol,
                bufferval,
                cleanup)

    def _convert(self,scalefactor,area_ratio,colinear_tol,bufferval,cleanup):
        self.geoms = []
        T1 = numpy.array(self.transform)
        R1 = T1[0:3, 0:3]
        b1 = T1[0:3, 3:4]
        for ii, component in enumerate(self.components):
            T2 = numpy.array(component.transform)
            R2 = T2[0:3, 0:3]
            b2 = T2[0:3, 3:4]
            if component.faces is not None:
                for jj, face in enumerate(component.faces):
                    try:
                        loops = face.loops

                        ints_c = [self.transform_loop(interior,R1,b1,R2,b2,scalefactor) for interior in loops]

                        a = [
                            GenericPoly.gen_from_point_lists(
                                loop,
                                []) for loop in ints_c]
                        b = [item.to_shapely(scaling = popupcad.csg_processing_scaling) for item in a]
                        if cleanup >= 0:
                            b = [
                                item.simplify(
                                    cleanup *
                                    popupcad.csg_processing_scaling) for item in b]
                        c = b.pop(0)
                        for item in b:
                            c = c.symmetric_difference(item)
                        d = popupcad.algorithms.csg_shapely.condition_shapely_entities(c)
                        e = popupcad.algorithms.csg_shapely.condition_shapely_entities(*[item.buffer(bufferval * popupcad.csg_processing_scaling,resolution=popupcad.default_buffer_resolution) for item in d])
                        f = [popupcad.algorithms.csg_shapely.to_generic(item) for item in e]
                        self.geoms.extend(f)
                    except NotSimple:
                        pass
                    except ShapeInvalid:
                        pass
                    except ValueError as ex:
                        print(ex)
#                        if ex.message!='A LinearRing must have at least 3 coordinate tuples':
#                            print(ex.message)
        self.filter_small_areas(area_ratio)

    @staticmethod
    def transform_loop(loop, R1, b1, R2, b2, scalefactor):
        looparray = numpy.array(loop).T

        v2 = R1.T.dot(R2.T.dot(looparray) + b2)
        v2 = v2[0:2, :].T
        v2 = v2 * scalefactor * popupcad.solidworks_mm_conversion
        return v2.tolist()

    def build_face_sketch(self):
        self.convert(scalefactor=None, bufferval=None, cleanup=None)
        sketch = popupcad.filetypes.sketch.Sketch.new()
        sketch.addoperationgeometries(self.geoms)
        return sketch

    def filter_small_areas(self, area_ratio):
        areas = []
        for geom in self.geoms:
            shape = geom.to_shapely(scaling = popupcad.csg_processing_scaling)
            areas.append(abs(shape.area))
        goodgeoms = []
        badgeoms = []
        for geom in self.geoms:
            shape = geom.to_shapely(scaling = popupcad.csg_processing_scaling)
            if abs(shape.area) < max(areas) * area_ratio:
                badgeoms.append(geom)
            else:
                goodgeoms.append(geom)
        self.geoms = goodgeoms
        self.badgeoms = badgeoms

    @staticmethod
    def buildloops(geoms):
        loops = []
        for geom in geoms:
            loops.append(geom.exteriorpoints())
            loops.extend(geom.interiorpoints())
        return loops

if __name__ == '__main__':
    import sys

    app = qg.QApplication(sys.argv)
    a = Assembly.open()
    a.convert(scalefactor=1., bufferval=None)
    sys.exit(app.exec_())
