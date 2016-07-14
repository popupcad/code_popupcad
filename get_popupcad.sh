#!/bin/bash
sudo apt-get update
sudo apt-get install -y git
git config --global user.name "LastName, Firstname"
git config --global user.email "email@address.com"
cd ~
git clone https://github.com/popupcad/popupcad.git
cd ~/popupcad
git checkout pyqt4_only
git pull
echo "export PYTHONPATH=\$PYTHONPATH:~/popupcad" >> ~/.bashrc
source ~/.bashrc
