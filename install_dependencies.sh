#!/bin/bash

if [[ "$TRAVIS_PYTHON_VERSION" == "" ]]; then
  export TRAVIS_PYTHON_VERSION=3.5;
fi

sudo apt-get update
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda

export PATH=$HOME/miniconda/bin:$PATH
echo "export PATH="\$HOME/miniconda/bin:\$PATH"" >> ~/.bashrc

hash -r
conda config --set always_yes yes --set changeps1 no
conda update conda
conda info -a

conda create -n test-environment python=$TRAVIS_PYTHON_VERSION  setuptools cython pyyaml shapely numpy scipy sympy pyopengl pyqt pyqtgraph matplotlib
source activate test-environment

pip install pypoly2tri ezdxf


