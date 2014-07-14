SEAS Git Repository Initial Setup
================

------------------------
Link to SEAS code server
------------------------

* make an account at https://code.seas.harvard.edu.  Help can be found `Here <https://spaces.seas.harvard.edu/display/USERDOCS/Getting+Started+with+code.seas>`_ and `here <https://spaces.seas.harvard.edu/display/USERDOCS/SEAS+Code+Repository>`_.
 * get permission to be added to the popupcad project (danaukes <at> seas.harvard.edu)
 * add your public key to the repo

  On Linux:

  * open a terminal and type::

     ssh-keygen -t rsa
     cat ~/.ssh/id_rsa.pub

  * copy the key

  On Windows:

  * install `putty <http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html>`_
  * run puttygen, copy the key
	
 * copy the key into website
  * go to the dashboard and select the "Manage SSH Keys".
  * after following the links, paste the generated key in to the text box.

------------------------
Checkout code
------------------------

On Linux:

* open a terminal and type::

   git config --global user.name "LastName, Firstname"
   git config --global user.email "email@address.com"
   git clone git@code.seas.harvard.edu:code/popupcad.git
   cd ~/popupcad/
   git checkout master
   git pull
   cd
   git clone git@code.seas.harvard.edu:code/pypoly2tri.git
   cd pypoly2tri
   git checkout master
   git pull
   sudo python setup.py install   

On Windows:

* Right click in the folder you want to store the code in, and select "clone repository"
 * enter `<git@code.seas.harvard.edu:code/popupcad.git>`_ as the source
 * enter your key information
* repeat the above steps for `<git@code.seas.harvard.edu:code/pypoly2tri.git>`_

