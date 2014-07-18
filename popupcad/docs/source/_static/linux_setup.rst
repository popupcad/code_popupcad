Linux Setup
================

#. Install/Update Software::

    sudo apt-get update
    sudo apt-get install dkms git spyder python-pyside python-shapely python-sympy python-pip synaptic python-opengl python-networkx python-yaml python-scipy python-matplotlib
    sudo pip install shapely --upgrade
#. optional: upgrad your system::

     sudo apt-get upgrade
#. optional: set flag for systems without hardware video acceleration(for example if using virtualbox)::
     
	 echo "export LIBGL_ALWAYS_INDIRECT=1" >> ~/.bashrc
#. :doc:`popupcad_git_setup`
	

 
