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
packages.append('popupcad.constraints')
packages.append('popupcad.deprecated')
packages.append('popupcad.filetypes')
packages.append('popupcad.geometry')
packages.append('popupcad.graphics2d')
packages.append('popupcad.graphics3d')
packages.append('popupcad.guis')
packages.append('popupcad.manufacturing')
packages.append('popupcad.materials')
packages.append('popupcad.supportfiles')
packages.append('popupcad.widgets')

packages.append('pypoly2tri')
packages.append('popupcad_manufacturing_plugins')


package_data = {}
package_data['popupcad'] = ['scripts/*','designs/*','import/*','supportfiles/*']
setup(name=popupcad.program_name,
      version=popupcad.version,
      classifiers=popupcad.classifiers,      
      description=popupcad.description,
      author=popupcad.author,
      author_email=popupcad.author_email,
      url=popupcad.url,
      packages=packages,
      package_data = package_data
     )