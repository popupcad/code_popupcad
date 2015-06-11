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
packages.append('dev_tools')
packages.append('popupcad_manufacturing_plugins')
packages.append('popupcad_deprecated')

package_data = {}
package_data['popupcad'] = ['docs/*','docs/source/*','supportfiles/*']

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