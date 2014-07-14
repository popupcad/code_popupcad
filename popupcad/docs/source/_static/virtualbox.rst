.. VirtualMachine:
Set up a virtual machine for Linux
================
Preparing your computer

* install virtualbox
* make sure extensions are enabled in bios

Make a new virtual machine

* dynamic hard drive, 50gb
* disable sound, usb, absolute pointing device
* enable 3d Acceleration, bidirectional clipboard, nested paging, VT-x/AMD-V
* 4096Gb Memory
* 128Mb Video
* 4 cpus

Install Ubuntu x64 or Linux Mint x64

* username woodgroup

Install/Update Software

* install guest additions
* sudo usermod -a -G vboxsf woodgroup
