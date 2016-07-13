# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

from distutils.core import setup
import popupcad

packages = []

packages.append('dev_tools')

packages.append('api_examples')

packages.append('popupcad')
packages.append('popupcad.algorithms')
packages.append('popupcad.constraints')
packages.append('popupcad.filetypes')
packages.append('popupcad.geometry')
packages.append('popupcad.graphics2d')
packages.append('popupcad.graphics3d')
packages.append('popupcad.guis')
packages.append('popupcad.manufacturing')
packages.append('popupcad.materials')
packages.append('popupcad.widgets')

packages.append('popupcad_deprecated')

packages.append('popupcad_manufacturing_plugins')
packages.append('popupcad_manufacturing_plugins.manufacturing')

packages.append('popupcad_microrobotics')

packages.append('popupcad_tests')

packages.append('qt')

#packages.append('popupcad_manufacturing_plugins.manufacturing')
#packages.append('pypoly2tri')

package_data = {}
package_data['popupcad'] = ['supportfiles/*','supportfiles/icons/*']

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
