# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 09:17:14 2015

@author: danaukes
"""

import networkx
import matplotlib.pyplot as plt
plt.ion()


import os
import sys
import popupcad
import popupcad_deprecated
popupcad.deprecated = popupcad_deprecated
sys.modules['popupcad.deprecated'] = popupcad_deprecated
import glob
#import PySide.QtGui as qg

def fix(*args):
    return os.path.normpath(os.path.join(*args))
    
def get_subfiles_r(d,parent_name):
    for key,subdesign in d.subdesigns.items():
        subdesign_name = subdesign.get_basename()+str(id(d))
        dg.add_node(subdesign_name)    
        dg.add_edge(parent_name,subdesign_name)
        get_subfiles_r(subdesign,subdesign_name)

#app = qg.QApplication(sys.argv)
directory = 'C:/Users/danaukes/Dropbox/sentinal11'

globstring = fix(directory,'*.cad')

files = glob.glob(globstring)
subfiles = {}
allfiles = []

connections = []


print(files)
dg = networkx.DiGraph()

for filename in files[:]:
    print(filename)
    full_filename = fix(filename)
    d = popupcad.filetypes.design.Design.load_yaml(full_filename)
    d = d.upgrade()
    d.save_yaml(full_filename)
    allfiles.append(d.get_basename())
    parent_name = d.get_basename()+str(id(d))
    get_subfiles_r(d,parent_name)

plt.figure()
pos = networkx.circular_layout(dg)
networkx.draw_networkx_labels(dg,pos)
networkx.draw(dg,pos)
plt.show()