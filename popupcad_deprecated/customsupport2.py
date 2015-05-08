# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import popupcad
from popupcad.filetypes.operation import Operation

import PySide.QtCore as qc
import PySide.QtGui as qg

from popupcad.filetypes.validators import StrictDoubleValidator
from dev_tools.enum import enum
from popupcad.filetypes.operationoutput import OperationOutput
from popupcad.widgets.dragndroptree import DraggableTreeWidget

class Dialog(qg.QDialog):
    def __init__(self,operationlist,device_index=0,support_index=0,support_width = 1.0,support_out = 1.0,hole_radius = 1.0,cut_width = 1.0,deviceoutputref = 0,supportoutputref = 0):
        super(Dialog,self).__init__()

        self.operationlist = operationlist

        self.device_index = DraggableTreeWidget()
        self.device_index.linklist(self.operationlist)
#        self.device_index.setCurrentIndeces(device_index,deviceoutputref)
        self.device_index.selectIndeces([(device_index,deviceoutputref)])
        
        self.support_index = DraggableTreeWidget()
        self.support_index.linklist(self.operationlist)
#        self.support_index.setCurrentIndeces(support_index,supportoutputref)
        self.support_index.selectIndeces([(support_index,supportoutputref)])

        self.support_width = qg.QLineEdit()
        self.support_width.setAlignment(qc.Qt.AlignRight)
        self.support_width.setText(str(support_width))
        v = StrictDoubleValidator(0, 1e6, 4,self.support_width)
        self.support_width.setValidator(v)
        
        self.support_out = qg.QLineEdit()
        self.support_out.setAlignment(qc.Qt.AlignRight)
        self.support_out.setText(str(support_out))
        v = StrictDoubleValidator(0, 1e6, 4,self.support_out)
        self.support_out.setValidator(v)

        self.hole_radius = qg.QLineEdit()
        self.hole_radius.setAlignment(qc.Qt.AlignRight)
        self.hole_radius.setText(str(hole_radius))
        v = StrictDoubleValidator(0, 1e6, 4,self.hole_radius)
        self.hole_radius.setValidator(v)

        self.cut_width = qg.QLineEdit()
        self.cut_width.setAlignment(qc.Qt.AlignRight)
        self.cut_width.setText(str(cut_width))
        v = StrictDoubleValidator(0, 1e6, 4,self.cut_width)
        self.cut_width.setValidator(v)

        self.Device= qg.QRadioButton('Device')
        self.Support= qg.QRadioButton('Support')
        self.Cuts= qg.QRadioButton('Cuts')

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')

        layout = qg.QGridLayout()
#        layout = qg.QVBoxLayout()
        layout.addWidget(qg.QLabel('Device'),1,1)
        layout.addWidget(self.device_index,1,2)
        layout.addWidget(qg.QLabel('Support Sketch'),2,1)
        layout.addWidget(self.support_index,2,2)
        layout.addWidget(qg.QLabel('Support Width'),3,1)
        layout.addWidget(self.support_width,3,2)
        layout.addWidget(qg.QLabel('Support Out'),4,1)
        layout.addWidget(self.support_out,4,2)
        layout.addWidget(qg.QLabel('Hole Radius'),5,1)
        layout.addWidget(self.hole_radius,5,2)
        layout.addWidget(qg.QLabel('CutWidth'),6,1)
        layout.addWidget(self.cut_width,6,2)
        layout.addWidget(button1,7,1)
        layout.addWidget(button2,7,2)

        self.setLayout(layout)    

        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)

    def acceptdata(self):
        ii,kk = self.device_index.currentIndeces2()[0]
        jj,ll = self.support_index.currentIndeces2()[0]
        return self.operationlist[ii].id,self.operationlist[jj].id,float(self.support_width.text()),float(self.support_out.text()),float(self.hole_radius.text()),float(self.cut_width.text()),kk,ll

class CustomSupport2(Operation):
    name = 'Custom Support'

    attr_init = 'device_link','support_link','support_width','support_out','hole_radius','cut_width','deviceoutputref','supportoutputref'
    attr_init_k = tuple()
    attr_copy = 'id','customname'
    
    outputtypes = enum(device = 201,supports = 202,cuts = 203)    
    
    def __init__(self,*args):
        super(CustomSupport2,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,device_link,support_link,support_width,support_out,hole_radius,cut_width,deviceoutputref,supportoutputref):
        super(CustomSupport2,self).editdata()
        self.device_link= device_link
        self.support_link= support_link
        self.support_width= support_width
        self.support_out= support_out
        self.hole_radius= hole_radius
        self.cut_width= cut_width
        self.deviceoutputref = deviceoutputref
        self.supportoutputref = supportoutputref

    def parentrefs(self):
        return [self.device_link,self.support_link]

    @classmethod
    def buildnewdialog(cls,design,currentoperation):
        dialog = Dialog(design.operations)
        return dialog

    def buildeditdialog(self,design):        
        device_index= design.operation_index(self.device_link)
        support_index= design.operation_index(self.support_link)
        dialog = Dialog(design.prioroperations(self),device_index,support_index,self.support_width,self.support_out,self.hole_radius,self.cut_width,self.deviceoutputref,self.supportoutputref)
        return dialog

    def generate(self,design):
        import popupcad_manufacturing_plugins
        device = design.op_from_ref(self.device_link).output[self.deviceoutputref].csg
        support = design.op_from_ref(self.support_link).output[self.supportoutputref].csg
        modified_device,supports,cuts = popupcad_manufacturing_plugins.algorithms.modify_device.modify_device(device,support,self.support_width*popupcad.internal_argument_scaling,self.support_out*popupcad.internal_argument_scaling,self.hole_radius*popupcad.internal_argument_scaling,self.cut_width*popupcad.internal_argument_scaling)
#        return supports,cuts,device
#
#    def generate(self,design):
#        supports,cuts,device = self.operate(design)
        s = OperationOutput(supports,'supports',self)
        c = OperationOutput(cuts,'cuts',self)
        d = OperationOutput(modified_device,'device',self)
        self.output = [d,s,c]

