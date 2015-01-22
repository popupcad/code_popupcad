# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import sys
import imp
#import dev_tools
import dev_tools.constraints
#import dev_tools.acyclicdirectedgraph

import popupcad

dev_tools.constraints.internal_argument_scaling = popupcad.internal_argument_scaling

popupcad.constraints = imp.new_module('constraints')
popupcad.constraints.constraints = dev_tools.constraints
sys.modules['popupcad.constraints.constraints']  = dev_tools.constraints

