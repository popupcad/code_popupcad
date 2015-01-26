Mac Setup
================
#. (optional?)disable Mac security for apps.
 #. open settings
 #. go to "security and privacy", then select the "general" tab
 #. click the lock and supply your password, if needed
 #. on the "Allow apps downloaded from" radio buttons, select "anywhere"
#. download and install X-Code from the app store(https://developer.apple.com/xcode/)
#. run this...::

    echo Enter your first name and press [ENTER]:
    read FirstName
    echo Enter your last name and press [ENTER]:
    read LastName
    echo Enter your email and press [ENTER]:
    read EmailAddress

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

    echo export PATH=/usr/local/bin:\$PATH >> ~/.bash_profile
    echo export RESOURCEPATH=\$RESOURCEPATH >> ~/.bash_profile
    source ~/.bash_profile

    brew install gcc
    brew install geos
    brew install python3
    brew install pyside --with-python3

    pip3 install cx_freeze numpy pip pyopengl pyqtgraph pyyaml scipy setuptools shapely spyder sympy

    git config --global user.name "$LastName, $FirstName"
    git config --global user.email "$EmailAddress"
    cd ~/
    git clone https://github.com/danaukes/popupcad.git
    cd ~/popupcad/
    git checkout master
    git pull

    echo "export PYTHONPATH=\$PYTHONPATH:~/popupcad" >> ~/.bash_profile
    source ~/.bash_profile
    