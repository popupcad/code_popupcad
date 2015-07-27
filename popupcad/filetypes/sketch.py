# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
from popupcad.filetypes.constraints import ConstraintSystem
import popupcad
from popupcad.filetypes.popupcad_file import popupCADFile
import PySide.QtGui as qg
import PySide.QtCore as qc


class Sketch(popupCADFile):
    filetypes = {'sketch': 'Sketch File', 'dxf': 'DXF'}
    defaultfiletype = 'sketch'

    @classmethod
    def lastdir(cls):
        return popupcad.lastsketchdir

    @classmethod
    def setlastdir(cls, directory):
        popupcad.lastsketchdir = directory

    def __init__(self):
        super(Sketch, self).__init__()
        self.operationgeometry = []
        self.constraintsystem = ConstraintSystem()

    def copy(self, identical=True):
        new = type(self)()
        new.operationgeometry = [
            geom.copy(
                identical=True) for geom in self.operationgeometry if geom.isValid()]
        new.constraintsystem = self.constraintsystem.copy()
        if identical:
            new.id = self.id
        self.copy_file_params(new, identical)
        return new

    def upgrade(self, identical=True):
        new = type(self)()
        new.operationgeometry = [
            geom.upgrade(
                identical=True) for geom in self.operationgeometry if geom.isValid()]
        new.constraintsystem = self.constraintsystem.upgrade()
        if identical:
            new.id = self.id
        self.copy_file_params(new, identical)
        return new

    def addoperationgeometries(self, polygons):
        self.operationgeometry.extend(polygons)

    def cleargeometries(self):
        self.operationgeometry = []

    def edit(self, parent, design=None, **kwargs):
        from popupcad.guis.sketcher import Sketcher
        sketcher = Sketcher(
            parent,
            self,
            design,
            accept_method=self.edit_result,
            **kwargs)
        sketcher.show()
        sketcher.graphicsview.zoomToFit()

    def edit_result(self, sketch):
        self.operationgeometry = sketch.operationgeometry
        self.constraintsystem = sketch.constraintsystem

    def output_csg(self):
        import popupcad.geometry.customshapely
        shapelygeoms = []
        for item in self.operationgeometry:
            try:
                if not item.is_construction():
                    shapelyitem = item.outputshapely()
                    shapelygeoms.append(shapelyitem)
            except ValueError as ex:
                print(ex)
            except AttributeError as ex:
                shapelyitem = item.outputshapely()
                shapelygeoms.append(shapelyitem)
        shapelygeoms = popupcad.geometry.customshapely.unary_union_safe(
            shapelygeoms)
        shapelygeoms = popupcad.geometry.customshapely.multiinit(shapelygeoms)
        return shapelygeoms

    @classmethod
    def load_dxf(cls, filename, parent=None):
        import ezdxf
        ezdxf.options.template_dir = popupcad.supportfiledir        
        
        import ezdxf.modern
        dxf = ezdxf.readfile(filename)
        layer_names = [layer.dxf.name for layer in dxf.layers]
        
        dialog = qg.QDialog()
        lw = qg.QListWidget()
        for item in layer_names:
            lw.addItem(qg.QListWidgetItem(item))
        lw.setSelectionMode(lw.SelectionMode.ExtendedSelection)
        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')
        button_ok.clicked.connect(dialog.accept)
        button_cancel.clicked.connect(dialog.reject)

        layout = qg.QVBoxLayout()
        layout_buttons = qg.QHBoxLayout()
        layout_buttons.addWidget(button_ok)
        layout_buttons.addWidget(button_cancel)
        layout.addWidget(lw)
        layout.addLayout(layout_buttons)
        dialog.setLayout(layout)
        result = dialog.exec_()
        
        if result:
            selected_layers = [
                item.data(
                    qc.Qt.ItemDataRole.DisplayRole) for item in lw.selectedItems()]
            entities = dxf.entities
            generics = []
            for entity in entities:
                if entity.dxf.layer in selected_layers:
                    if isinstance(entity, ezdxf.modern.graphics.Line):
                        from popupcad.filetypes.genericshapes import GenericLine
                        import numpy
                        points = numpy.array(
                            [entity.dxf.start[:2], entity.dxf.end[:2]])
                        generics.append(
                            GenericLine.gen_from_point_lists(
                                points.tolist(),
                                []))
                    elif isinstance(entity, ezdxf.modern.graphics.LWPolyline):
                        from popupcad.filetypes.genericshapes import GenericPolyline
                        from popupcad.filetypes.genericshapes import GenericPoly
                        import numpy
                        points = numpy.array(entity.dxf.points)
                        if entity.is_closed:
                            generics.append(
                                GenericPoly.gen_from_point_lists(
                                    points.tolist(),
                                    []))
                        else:
                            generics.append(
                                GenericPolyline.gen_from_point_lists(
                                    points.tolist(),
                                    []))
                    else:
                        print(entity)
            new = cls()
            new.addoperationgeometries(generics)
            return filename, new
        else:
            return None, None

    @classmethod
    def open_filename(cls, parent=None):
        filterstring, selectedfilter = cls.buildfilters()
        filename, selectedfilter = qg.QFileDialog.getOpenFileName(
            parent, 'Open', cls.lastdir(), filter=filterstring, selectedFilter=selectedfilter)
        if filename:
            if 'sketch' in selectedfilter:
                object1 = cls.load_yaml(filename)
                return filename, object1
            elif 'dxf' in selectedfilter:
                return cls.load_dxf(filename, parent)
        return None, None

    def saveAs(self, parent=None):
        import os
        try:
            tempfilename = os.path.normpath(
                os.path.join(
                    self.dirname,
                    self.get_basename()))
        except AttributeError:
            try:
                basename = self.get_basename()
            except AttributeError:
                basename = self.genbasename()

            tempfilename = os.path.normpath(
                os.path.join(
                    self.lastdir(),
                    basename))

        filterstring, selectedfilter = self.buildfilters()
        filename, selectedfilter = qg.QFileDialog.getSaveFileName(
            parent, "Save As", tempfilename, filter=filterstring, selectedFilter=selectedfilter)
        if not filename:
            return False
        else:
            if 'sketch' in selectedfilter:
                return self.save_yaml(filename,identical=False)
            elif 'dxf' in selectedfilter:
                return self.save_dxf(filename)

    def save_dxf(self,filename):
        import ezdxf
        ezdxf.options.template_dir = popupcad.supportfiledir        
        
        dwg = ezdxf.new('AC1015')
        msp = dwg.modelspace()
        
        for item in self.operationgeometry:
            if not item.is_construction():
                item.output_dxf(msp)
        
        dwg.saveas(filename)        