# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
from popupcad.filetypes.userdata import UserData


class OperationOutput(UserData):

    def __init__(self, csg, name, parent=None):
        super(OperationOutput, self).__init__()
        self.csg = csg
        self.name = name
        self.parent = parent

    def generic_laminate(self):
        try:
            return self._generic_laminate
        except AttributeError:
            self._generic_laminate = self.csg.to_generic_laminate()
            return self._generic_laminate

    def controlpoints(self):
        try:
            return self._controlpoints
        except AttributeError:
            self.update_controls()
            return self._controlpoints

    def controllines(self):
        try:
            return self._controllines
        except AttributeError:
            self.update_controls()
            return self._controllines

    def controlpolygons(self):
        try:
            return self._control_polygons
        except AttributeError:
            self.update_controls()
            return self._control_polygons

    def update_controls(self):
        self._controlpoints, self._controllines, self._control_polygons = self.getcontrols(
            self.generic_laminate())

    @staticmethod
    def getcontrols(genericgeometry):
        from popupcad.geometry.line import ReferenceLine
        from popupcad.geometry.vertex import ReferenceVertex
        vertices = []
        unique_geoms = []
        all_geoms = []
        lines = []
        for layer, geoms in genericgeometry.geoms.items():
            all_geoms.extend(geoms)
            for geom in geoms:
                p = geom.points()
                vertices.extend(p)
                lines.extend(geom.segmentpoints())

        for geom in all_geoms:
            is_unique = True
            for geom2 in unique_geoms:
                if geom.is_equal(geom2):
                    is_unique = False
                    break
            if is_unique:
                unique_geoms.append(geom)

        vertices = list(set(vertices))
        controlpoints = [ReferenceVertex(p) for p in vertices]

        lines = list(set(lines))
        lines2 = [(vertices.index(p1), vertices.index(p2)) for p1, p2 in lines]
        controllines = [
            ReferenceLine(
                controlpoints[ii],
                controlpoints[jj]) for ii,
            jj in lines2]
        return controlpoints, controllines, unique_geoms

    def edit(self, *args, **kwargs):
        if self.parent is not None:
            self.parent.edit(*args, **kwargs)

    def display_geometry_2d(self):
        try:
            return self._display_geometry_2d
        except AttributeError:
            self._display_geometry_2d = self.generic_laminate().to_static()
            return self._display_geometry_2d

    @property
    def triangles_by_layer(self):
        try:
            return self._triangles_by_layer
        except AttributeError:
            self._triangles_by_layer = self.generic_laminate().to_triangles()
            return self._triangles_by_layer

    def description_get(self):
        try:
            return self._description
        except AttributeError:
            self._description = ''
            return self._description

    def description_set(self, value):
        self._description = value

    description = property(description_get, description_set)

    def edit_description(self):
        
        import qt.QtCore as qc
        import qt.QtGui as qg
        result, ok = qg.QInputDialog.getText(
            None, 'description', 'label', text=self.description)
        if ok:
            self.description = result
