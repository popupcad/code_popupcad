Windows Setup
================

1. Install python and the following modules.  I've also linked to binary Windows Installers (exe) provided by Christoph Gohlke at the Laboratory for Fluorescence Dynamics, University of California, Irvine.  Many thanks.
  
  Required:
  
  `Python <http://python.org/>`_ `(exe) <http:/python.org/downloads/>`_, 
  `PySide <http://qt-project.org/wiki/PySide>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyside>`_, 
  `Numpy <http://www.numpy.org/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_,
  `Scipy <http://www.scipy.org/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_,
  `Sympy <http://sympy.org/en/index.html>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#sympy>`_,
  `Shapely <http://toblerity.org/shapely/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely>`_,
  `NetworkX <http://networkx.github.io/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#networkx>`_,
  `pyOpenGL <http://pyopengl.sourceforge.net/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl>`_,
  `pyparsing <http://pyparsing.wikispaces.com/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyparsing>`_,
  `pydateutil <https://labix.org/python-dateutil>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-dateutil>`_,
  `Matplotlib <http://matplotlib.org/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib>`_,
  `pytz <http://pythonhosted.org//pytz/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytz>`_,
  `six <http://pythonhosted.org/six/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#six>`_,
  `pyyaml <http://pyyaml.org/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyyaml>`_,
  
  Useful, but not required:
  
  `PyQt <http://www.riverbankcomputing.com/software/pyqt/intro>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt>`_,
  `Spyder <https://code.google.com/p/spyderlib/>`_ `(exe) <http://www.lfd.uci.edu/~gohlke/pythonlibs/#spyder>`_
  
2. Add python to your path.
  #. Open explorer window (win+e)
  #. Right click on "Computer" in the left pane.  Select properties at the bottom.
  #. Select "advanced system settings" in the left pane
  #. In the "System Properties" window that pops up, select "Environment Variables" from the "Advanced Tab"
  #. In the "System Variables" list, scroll down to the "Path" variable and select "Edit" or "New" it if it doesn't exist.
  #. In the "Variable Name" field, type "PATH" if it doesn't exist.  
  #. In the "Variable Value" field, append the path to your python installation and scripts directories to the end.
   * Values are separated with a semicolon.
   * No spaces are allowed.
	
   Before::
  
      ...Program Files\Microsoft SQL Server\100\DTS\Binn\
		
   After(Using Python 2.7 as an example)::

      ...Program Files\Microsoft SQL Server\100\DTS\Binn\;C:\Python27;C:\Python27\Scripts

3. Get popupCAD
 * To retrieve the source from the  `SEAS git repository <https://code.seas.harvard.edu>`_ see :doc:`code.seas`
4. Install popupCAD
 * In the start menu, type "cmd" to open up a command prompt
 * move to the popupCAD directory, wherever you downloaded it.  There should be a file called "setup.py" in this folder
 * Type::
   python setup.py install



