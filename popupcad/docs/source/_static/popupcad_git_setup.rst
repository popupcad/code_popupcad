setup Git repository for popupCAD
===================

#. open a terminal and type::

    git config --global user.name "LastName, Firstname"
    git config --global user.email "email@address.com"
    git clone https://github.com/danb0b/popupcad.git
    cd ~/popupcad/
    git checkout master
    git pull

#. add popupcad directory to path::

     echo "PYTHONPATH$PYTHONPATH:~/popupcad" >> ~/.bashrc
