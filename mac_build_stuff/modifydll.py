# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 14:01:41 2015

@author: WOODGROUP
"""

import sys
import os
import subprocess
import glob
import shutil


commands = []

path = '/Users/WOODGROUP/code/popupcad/build/exe.macosx-10.9-x86_64-3.4/'
files1 = glob.glob(path+'*.so')
files2 = glob.glob(path+'popupcad')
files3 = glob.glob(path+'*.dylib')
files = files1+files2+files3
curdir = 'newdlls'
curdir = os.path.abspath(curdir)

#commands.append('ls -la;cd ../;ls -la')
#commands.append('cd ../')
#commands.append('ls -la')
commands = []
changedfiles = []
for file in files:
    command = 'otool -L '+file
    run1 = subprocess.Popen(command,universal_newlines = True, shell = True,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    out,err = run1.communicate()
    out2=out.split('\n')
    for item in out2:
        if item.find('.dylibs/')!=-1:
            item = item.strip(' \t')
            item = item.split('(')[0]
            olditem = item
            item = item.split('.dylibs/')[1]
            newitem = '@loader_path/'+item
            print(olditem,newitem)
            newfile = curdir+'/'+os.path.split(file)[-1]
            print(file,item)
            command = 'sudo install_name_tool -change '+olditem+' '+newitem+' '+file+'\n'
            commands.append(command)
            changedfiles.append(file)
            
#        if item.find('/usr/local')!=-1:
##            print(item,err)
#            item = item.strip(' \t')
#            item = item.split('(')[0]
#            olditem = item
#            item = item.split('/')[-1]
#            newitem = '@loader_path/'+item
##            print(olditem,newitem)
#            print(file,item)
#            command = 'sudo install_name_tool -change '+olditem+' '+newitem+' '+file+'\n'
#            commands.append(command)
changedfiles = list(set(changedfiles))
if os.path.exists(curdir):
    shutil.rmtree(curdir)
os.mkdir(curdir)
for file in changedfiles:
    shutil.copy(file,curdir+'/'+os.path.split(file)[-1])
print(commands)
with open('test.sh','w') as f:
    f.writelines(commands)

#            
#    print(out)