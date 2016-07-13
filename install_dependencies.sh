#!/bin/bash
sudo apt-get update
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a
conda create -q -n popupcad_env python=$TRAVIS_PYTHON_VERSION shapely pyyaml numpy scipy setuptools cython pyqt sympy pyopengl pyqtgraph matplotlib
pip install pypoly2tri ezdxf
source activate popupcad_env