reg delete HKCR\popupcadfile\ /f
::ftype popupcadfile="python.exe" "C:\Users\danaukes\Documents\code\popupcad\popupcad.py" "%%1"
ftype popupcadfile="C:\Program Files\popupCAD\popupcad.exe" "%%1"
assoc .cad=popupcadfile
::reg add HKCR\popupcadfile\DefaultIcon /ve /d "C:\Users\danaukes\Documents\code\popupcad\popupcad\supportfiles\printapede.ico" /t REG_EXPAND_SZ /f
