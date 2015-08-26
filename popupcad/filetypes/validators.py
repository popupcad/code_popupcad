# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import PySide.QtGui as qg


class StrictDoubleValidator(qg.QDoubleValidator):

    def validate(self, input_value, pos):
        state, input_value, pos = super(
            StrictDoubleValidator, self).validate(
            str(input_value), pos)

        if input_value == '' or input_value == '.':
            return self.Intermediate, input_value, pos
        if state != self.Acceptable:
            return self.Invalid, input_value, pos
        return self.Acceptable, input_value, pos
