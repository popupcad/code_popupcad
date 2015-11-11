# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import popupcad
import qt
import qt.QtCore as qc
import qt.QtGui as qg

if __name__ =='__main__':
    import sys
    app = qg.QApplication(sys.argv)
#    design = popupcad.filetypes.design.Design.open()
    filename = 'C:\\Users\\danb0b\\downloads\\robot2.cad'
    design = popupcad.filetypes.design.Design.load_yaml(filename)
    design.reprocessoperations()
    outputs = design.operations[-1].output
    volume = []
    mass = []
    center_of_mass = []
    I = []
    for o in outputs[6:25]:
        volume_ii,mass_ii,center_of_mass_ii,I_ii = o.generic_laminate().mass_properties()
        volume.append(volume_ii)
        mass.append(mass_ii)
        center_of_mass.append(center_of_mass_ii)
        I.append(I_ii)
#    sys.exit(app.exec_())