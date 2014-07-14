touch libpyside-python2.7.1.2.dylib
touch libshiboken-python2.7.1.2.dylib
touch libgeos.3.4.2.dylib

ln -s /Library/Frameworks/QtCore.framework .
ln -s /Library/Frameworks/QtGui.framework .
ln -s /Library/Frameworks/QtNetwork.framework .
ln -s /Library/Frameworks/QtOpenGl.framework .
ln -s /Library/Frameworks/QtSvg.framework .
ln -s /Library/Frameworks/QtXml.framework .

python build_mac.py bdist_dmg

rm Qt*