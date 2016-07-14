#!/bin/bash
sudo apt-get update
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda
#export PATH="$HOME/miniconda/bin:$PATH"
echo "export PATH="\$HOME/miniconda/bin:\$PATH"" >> ~/.bashrc
source ~/.bashrc

hash -r
conda config --set always_yes yes --set changeps1 no
conda update conda
conda info -a

conda create -n test-environment python=$TRAVIS_PYTHON_VERSION 
source activate test-environment

conda install setuptools 
conda install cython
conda install pyyaml
conda install shapely 
conda install numpy 
conda install scipy
conda install sympy 
conda install pyopengl 
conda install pyqt
conda install pyqtgraph 
conda install matplotlib

pip install pypoly2tri ezdxf

echo "export PYTHONPATH=\$PYTHONPATH:\$HOME/" >> ~/.bashrc
source ~/.bashrc

#python3 setup.py install
