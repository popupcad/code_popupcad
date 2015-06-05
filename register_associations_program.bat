reg delete HKCR\popupcadfile\ /f
ftype popupcadfile="C:\Program Files\popupCAD\popupcad.exe" "%%1"
assoc .cad=popupcadfile
