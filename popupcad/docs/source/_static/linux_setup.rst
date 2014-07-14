Linux Setup
================

Install/Update Software::

 sudo apt-get install dkms git spyder python-pyside python-shapely python-sympy python-pip synaptic python-opengl python-networkx python-yaml python-scipy python-matplotlib
 sudo pip install shapely --upgrade
 sudo apt-get update
 sudo apt-get upgrade
 echo "PYTHONPATH$PYTHONPATH:~/popupcad" >> ~/.bashrc
 echo "export LIBGL_ALWAYS_INDIRECT=1" >> ~/.bashrc
