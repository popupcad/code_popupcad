# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import networkx
import matplotlib.pyplot as plt
plt.ion()


import os
import sys
import yaml
import popupcad
import glob
import pygraphviz

def fix(*args):
    return os.path.normpath(os.path.join(*args))
    
def get_subfiles_r(d,parent_name,dg):
    for key,subdesign in d.subdesigns.items():
        subdesign_name = subdesign.get_basename()
        subdesign_name = os.path.splitext(subdesign_name)[0]
        dg.add_node(subdesign_name)    
        dg.add_edge(parent_name,subdesign_name)
        get_subfiles_r(subdesign,subdesign_name,dg)

def get_subfiles(filename,dg):
        print(filename)
        full_filename = fix(filename)
        d = popupcad.filetypes.design.Design.load_yaml(full_filename,upgrade=False)
        design_name = d.get_basename()
        design_name = os.path.splitext(design_name)[0]
        
        parent_name = d.get_basename()
        parent_name = os.path.splitext(parent_name)[0]
        get_subfiles_r(d,parent_name,dg)

def get_directory(directory_name,dg):
    globstring = fix(directory_name,'*.cad')
    files = glob.glob(globstring)
    print(files)
    for filename in files[:]:
        get_subfiles(filename,dg)

def plot_dg(dg):
    plt.figure()
#    pos = networkx.spring_layout(dg)
    pos = networkx.pygraphviz_layout(dg,'dot')
    networkx.draw_networkx_labels(dg,pos)
    networkx.draw(dg,pos,arrows=True)
    plt.show()

def make_pdf(dg):
    agraph = networkx.to_agraph(dg)
    agraph.graph_attr['overlap']='false'
    agraph.graph_attr['splines']='true'
    agraph.graph_attr['rankdir']='LR'
    agraph.graph_attr['ranksep']='.1'
    agraph.draw('test.pdf',prog='dot')

def save_dg(dg, filename=None):
    if filename is None:
        filename='graph1.yaml'
    nodes = dg.nodes()
    edges = dg.edges()
    
    nodes = list(set(nodes))
    edges = list(set(edges))
    
    with open(filename,'w') as f:
        yaml.dump({'nodes':nodes,'edges':edges},f)

#    agraph = networkx.to_agraph(dg)
#    agraph.graph_attr['overlap']='false'
#    agraph.graph_attr['splines']='true'
#    agraph.graph_attr['rankdir']='LR'
#    agraph.graph_attr['ranksep']='.1'
#    agraph.write('test.dot')

def make_dg(path):
    dg = networkx.DiGraph()
    if os.path.isdir(path):
        get_directory(path,dg)    
    elif os.path.isfile(path):
        get_subfiles(path,dg)    
    return dg

if __name__=='__main__':
    
    if len(sys.argv)>1:
        path = sys.argv[1]

    dg = make_dg(path)
    plot_dg(dg)
#    save_dg(dg)    
    make_pdf(dg)
