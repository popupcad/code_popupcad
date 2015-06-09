# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
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