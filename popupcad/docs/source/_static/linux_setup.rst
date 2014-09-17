Linux Setup
================

#. Install/Update Software::

    sudo apt-get update
    sudo apt-get install dkms git spyder python-pyside python-shapely python-sympy python-pip synaptic python-opengl python-networkx python-yaml python-scipy python-matplotlib python-setuptools
    sudo pip install pyqtgraph
    sudo pip install shapely --upgrade
#. optional: upgrad your system::

     sudo apt-get upgrade
#. optional: set flag for systems without hardware video acceleration(for example if using virtualbox)::
     
	 echo "export LIBGL_ALWAYS_INDIRECT=1" >> ~/.bashrc
#. :doc:`popupcad_git_setup`
#. Run popupCAD
 * From the terminal, navigate to the popupcad directory and type::
 
     python popupcad.py 
 * Or run using spyder a wonderful GUI for editing and debugging python programs.  Open spyder in the program menu or by typing  from the terminal::

	 spyder
  * from there you can navigate to the popupcad directory and open popupcad.py.
  * hit f5 to run.
	
	

 
