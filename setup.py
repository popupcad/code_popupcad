# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from distutils.core import setup
import popupcad

packages = []
packages.append('popupcad')
packages.append('popupcad.algorithms')
packages.append('popupcad.filetypes')
packages.append('popupcad.geometry')
packages.append('popupcad.graphics2d')
packages.append('popupcad.graphics3d')
packages.append('popupcad.guis')
packages.append('popupcad.manufacturing')
packages.append('popupcad.widgets')

packages.append('dev_tools')
packages.append('popupcad_manufacturing_plugins')
packages.append('popupcad_manufacturing_plugins.algorithms')
packages.append('popupcad_manufacturing_plugins.manufacturing')
packages.append('popupcad_deprecated')
packages.append('pypoly2tri')

package_data = {}

package_data['popupcad'] = ['docs/*', 'docs/source/*', 'supportfiles/*']

setup(name=popupcad.program_name,
      version=popupcad.version,
      classifiers=popupcad.classifiers,
      description=popupcad.description,
      author=popupcad.author,
      author_email=popupcad.author_email,
      url=popupcad.url,
      packages=packages,
      package_data=package_data
      )
