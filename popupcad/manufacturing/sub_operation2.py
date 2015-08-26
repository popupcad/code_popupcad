# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
import PySide.QtGui as qg
import PySide.QtCore as qc
import popupcad
from popupcad.filetypes.operation2 import Operation2
from popupcad.widgets.table_editor_popup import Table, SingleItemListElement,IntegerElement,Row, TableControl, DraggableTreeElement,Delegate
from popupcad.widgets.listmanager import DesignListManager

class SketchData(object):
    def __init__(self, ref1, ref2):
        self.ref1 = ref1
        self.ref2 = ref2

class InputData(object):
    def __init__(self, ref1, ref2,shift):
        self.ref1 = ref1
        self.ref2 = ref2
        self.shift = shift

class OutputData(object):
    def __init__(self, ref1,shift):
        self.ref1 = ref1
        self.shift = shift

class SketchRow(Row):
    def __init__(self, get_sketches, get_layers):
        elements = []
        elements.append(SingleItemListElement('to replace', get_sketches))
        elements.append(SingleItemListElement('replace with', get_layers))
        self.elements = elements

class InputRow(Row):
    def __init__(self, get_sketches, get_layers):
        elements = []
        elements.append(DraggableTreeElement('to replace', get_sketches))
        elements.append(DraggableTreeElement('replace with', get_layers))
        elements.append(IntegerElement('shift'))
        self.elements = elements

class OutputRow(Row):
    def __init__(self, get_sketches):
        elements = []
        elements.append(DraggableTreeElement('output', get_sketches))
        elements.append(IntegerElement('shift'))
        self.elements = elements

class MainWidget(qg.QDialog):

    def __init__(self, design, sketches, layers, operations, jointop=None):
        super(MainWidget, self).__init__()
        self.design = design
        self.sketches = sketches
        self.layers = layers
        self.operations = operations

        self.designwidget = DesignListManager(design)

        self.input_table = Table(InputRow(self.get_subdesign_operations,self.get_operations),Delegate)
        self.sketch_table = Table(SketchRow(self.get_subdesign_sketches,self.get_sketches),Delegate)
        self.output_table = Table(OutputRow(self.get_subdesign_operations),Delegate)

        self.sketch_control = TableControl(self.sketch_table, self)
        self.input_control = TableControl(self.input_table, self)
        self.output_control = TableControl(self.output_table, self)

        button_ok = qg.QPushButton('Ok')
        button_cancel = qg.QPushButton('Cancel')

        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)

        sublayout2 = qg.QHBoxLayout()
        sublayout2.addWidget(button_ok)
        sublayout2.addWidget(button_cancel)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.designwidget)
        layout.addWidget(self.sketch_control)
        layout.addWidget(self.input_control)
        layout.addWidget(self.output_control)
        layout.addLayout(sublayout2)
        self.setLayout(layout)

        if jointop is not None:
            subdesign = design.subdesigns[jointop.design_links['source'][0]]
            for ii in range(self.designwidget.itemlist.count()):
                item = self.designwidget.itemlist.item(ii)
                if item.value == subdesign:
                    item.setSelected(True)
            for item in jointop.sketch_list:
                self.sketch_table.row_add([subdesign.sketches[item.ref1]], [design.sketches[item.ref2]])
            for item in jointop.input_list:
                index1 = self.subdesign().operation_index(item.ref1[0])
                output1 = item.ref1[1]
                index2 = self.design.operation_index(item.ref2[0])
                output2 = item.ref2[1]
                self.input_table.row_add([(index1, output1)], [(index2, output2)],item.shift)
            for item in jointop.output_list:
                index1 = self.subdesign().operation_index(item.ref1[0])
                output1 = item.ref1[1]
                self.output_table.row_add([(index1, output1)],item.shift)

        self.designwidget.itemlist.itemSelectionChanged.connect(
            self.input_table.reset)
        self.designwidget.itemlist.itemSelectionChanged.connect(
            self.output_table.reset)

    def get_operations(self):
        return self.operations

    def get_subdesign_operations(self):
        return self.subdesign().operations

    def get_sketches(self):
        return self.design.sketches.values()

    def get_subdesign_sketches(self):
        return self.subdesign().sketches.values()

    def subdesign(self):
        try:
            return self.designwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):

        sketch_list = []
        data = self.sketch_table.export_data()
        for sketch1, sketch2 in data:
            sketch_list.append(SketchData(sketch1[0].id, sketch2[0].id))

        input_list = []
        for refs_from, refs_to,shift in self.input_table.export_data():
            op1_index, op1_output = refs_from[0]
            op2_index, op2_output = refs_to[0]
            op1_ref = self.subdesign().operations[op1_index].id
            op2_ref = self.design.operations[op2_index].id
            input_list.append(InputData((op1_ref, op1_output), (op2_ref, op2_output),shift))

        output_list = []
        for ref1,shift in self.output_table.export_data():
            op1_index, op1_output = ref1[0]
            op1_ref = self.subdesign().operations[op1_index].id
            output_list.append(OutputData((op1_ref, op1_output),shift))

        design_links = {}
        design_links['source'] = [self.subdesign().id]

        return design_links, sketch_list, input_list, output_list


class SubOperation2(Operation2):
    resolution = 2
    name = 'SubOp'

    def copy(self):
        new = type(self)(
            self.design_links.copy(),
            self.sketch_list[:],
            self.input_list[:],
            self.output_list[:])
        new.id = self.id
        new.customname = self.customname
        return new

    def upgrade(self):
        if isinstance(self.design_links['source'],int):
            design_links = {'source':[self.design_links['source']]}
            new = type(self)(
                design_links,
                self.sketch_list[:],
                self.input_list[:],
                self.output_list[:])
            new.id = self.id
            new.customname = self.customname
            return new
        else:
            return self
        
    def __init__(self, *args):
        super(SubOperation2, self).__init__()
        self.editdata(*args)
        self.id = id(self)

    def editdata(self, design_links, sketch_list, input_list, output_list):
        super(SubOperation2, self).editdata({}, {}, design_links)
        self.sketch_list = sketch_list
        self.design_links = design_links
        self.input_list = input_list
        self.output_list = output_list

    def replace_op_refs(self, refold, refnew):
        for item in self.input_list:
            if item.ref2 == refold:
                item.ref2 = refnew
        self.clear_output()

    def parentrefs(self):
        return [item.ref2[0] for item in self.input_list]

    @classmethod
    def buildnewdialog(cls, design, currentop):
        dialog = MainWidget(
            design,
            design.sketches.values(),
            design.return_layer_definition().layers,
            design.operations)
        return dialog

    def buildeditdialog(self, design):
        dialog = MainWidget(
            design,
            design.sketches.values(),
            design.return_layer_definition().layers,
            design.prioroperations(self),
            self)
        return dialog

    def generate(self, design):
        from popupcad.manufacturing.dummy_operation1 import DummyOp1
        
        subdesign_orig = design.subdesigns[self.design_links['source'][0]]
        subdesign = subdesign_orig.copy_yaml()

        sketches = design.sketches.copy()
        for key,value in sketches.items():
            sketches[key] = value.copy()
        subdesign.sketches.update(sketches)

        layerdef_subdesign = subdesign.return_layer_definition()
        layerdef_design = design.return_layer_definition()

        for sketch_data in self.sketch_list:
            from_ref = sketch_data.ref1
            to_ref = sketch_data.ref2
            subdesign.replace_sketch_refs_force(from_ref, to_ref)

        for input_data in self.input_list:
            from_ref = input_data.ref1
            to_ref = input_data.ref2

            csg = design.op_from_ref(to_ref[0]).output[to_ref[1]].csg
            csg2 = popupcad.algorithms.manufacturing_functions.shift_flip_rotate(csg,input_data.shift,False,False)
            csg3 = csg2.switch_layer_defs(layerdef_subdesign)
            dummy_op = DummyOp1(csg3)
            to_ref2 = (dummy_op.id,0)
            subdesign.operations.insert(0, dummy_op)
            subdesign.replace_op_refs_force(from_ref, to_ref2)

        subdesign.reprocessoperations()

        self.output = []
        for output_data in self.output_list:
            new_output = subdesign.op_from_ref(output_data.ref1[0]).output[output_data.ref1[1]]
            csg= new_output.csg
            csg2 = csg.switch_layer_defs(layerdef_design)
            csg3 = popupcad.algorithms.manufacturing_functions.shift_flip_rotate(csg2,output_data.shift,False,False)
            output2 = popupcad.filetypes.operationoutput.OperationOutput(csg3,new_output.name)
            self.output.append(output2)
