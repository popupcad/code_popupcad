Mac Setup
================
#. disable Mac security for apps.
 #. open settings
 #. go to "security and privacy", then select the "general" tab
 #. click the lock and supply your password, if needed
 #. on the "Allow apps downloaded from" radio buttons, select "anywhere"
#. Download and install packages
 * `<python https://www.python.org/>`_
 * `pip <http://pip.readthedocs.org/en/latest/installing.html#install-pip>`_
 * `Qt4.8 for Mac Opensource <http://qt-project.org/downloads>`_
 * `pyside binaries <http://qt-project.org/wiki/PySide_Binaries_MacOSX>`_
 * `gfortran binaries <https://gcc.gnu.org/wiki/GFortranBinaries#MacOS>`_
 * `cmake <http://www.cmake.org/cmake/resources/software.html>`_
 * `geos <http://trac.osgeo.org/geos/>`_
  #. unzip the source file
  #. from the terminal::
  
      cd DOWNLOAD_DIRECTORY/geos-3.x.x
      sudo make install

#. add the installed version of python to your path::

     echo 'export PATH="/Library/Frameworks/Python.framework/Versions/2.7/bin:${PATH}"' >> .bash_profile
#. install some python modules from pip::

     pip install --upgrade numpy scipy sympy pyqtgraph cx_freeze sphinx spyder shapely pyopengl pyyaml 

#. :doc:`popupcad_git_setup`
#. from the terminal, run spyder::

     spyder
 * navigate to popupcad.py and run to enable debugging
