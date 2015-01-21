# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 15:15:40 2015

@author: WOODGROUP
"""

import subprocess
#password = getpass.getpass()
#proc = subprocess.Popen(
#  ['sudo','-p','','-S','/etc/init.d/test','restart'],
#   stdin=subprocess.PIPE)
a = 'woodlab\n'.encode()
proc = subprocess.Popen(['sudo','-S','whoami'],stdin=subprocess.PIPE,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
#proc = subprocess.Popen(['sudo','-u','WOODGROUP','-S','whoami'],stdin=subprocess.PIPE,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
out,err = proc.communicate(a)
#proc.wait()