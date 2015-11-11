# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg

class TableWidget(qg.QTableWidget):
    def __init__(self,columnnames):
        super(TableWidget,self).__init__()
        
#        columnnames = ['Layer','V','E','Color']
        c = self.columnCount()
        for ii in range(len(columnnames)-c):
            super(TableWidget,self).insertColumn(self.columnCount())

        self.setEditTriggers(qg.QAbstractItemView.DoubleClicked | 
                                    qg.QAbstractItemView.SelectedClicked)
        self.setSelectionBehavior(qg.QAbstractItemView.SelectRows)
        self.setHorizontalHeaderLabels(columnnames)
        self.coltype={}
        
        self.coltype[1] = qg.QCheckBox
        self.coltype[2] = qg.QCheckBox

        self.fillfunction ={}
        self.fillfunction[0] = lambda ii,jj,x:self.setItem(ii,jj,qg.QTableWidgetItem(x))
        self.fillfunction[1] = lambda ii,jj,x:self.cellWidget(ii,jj).setChecked(qc.Qt.CheckState(int(x)))
        self.fillfunction[2] = self.fillfunction[1]
        self.fillfunction[3] = self.setbuttoncolor

        self.getfunction={}
        self.getfunction[0] = lambda ii,jj:self.item(ii,jj).data(0)
        self.getfunction[1] = lambda ii,jj:self.cellWidget(ii,jj).isChecked()
        self.getfunction[2] = self.getfunction[1]
        self.getfunction[3] = self.getbuttoncolor

        self.verticalHeader().setVisible(False)
        
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
    def getbuttoncolor(self,row,column):
        button = self.cellWidget(row,column)
        p=button.palette()
        return p.color(qg.QPalette.Button)
        
        
    def setbuttoncolor(self,row,column,data):
        button = self.cellWidget(row,column)
        button.setText(hex(data.value()))
        palette = qg.QPalette()
        palette.setColor(qg.QPalette.Button,data)
        button.setPalette(palette)
        button.setAutoFillBackground(True)
        
    def definerow(self,row):
        for column,widget in self.coltype.items():
            self.setCellWidget(row,column,widget())
        button = qg.QPushButton('Color')       
        button.clicked.connect(lambda:self.setColor(row,3))
        button.setFlat(True)
        self.setCellWidget(row,3,button)

    def fillrow(self,ii,row):
        for jj,celldata in enumerate(row):
            self.fillfunction[jj](ii,jj,celldata)
        self.resizeColumnsToContents()
        self.horizontalHeader().stretchLastSection()
    def returnrow(self,ii):
        rowdata = []
        for jj in range(self.columnCount()):
            rowdata.append(self.getfunction[jj](ii,jj))
#        self.resizeColumnsToContents()
#        self.horizontalHeader().stretchLastSection()
        return rowdata
    def returnrows(self):
        data = []
        for ii in range(self.rowCount()):
            data.append(self.returnrow(ii))
        return data

    def insertrows(self,data):
#        data = []
        for rowdata in data:
            self.insertRow(rowdata)
#        return data
        
    def click_method(row,column):
        print(row, column)

    def insertRow(self,rowdata):
        r = self.rowCount()
        super(TableWidget,self).insertRow(r)
        self.definerow(r)
        self.fillrow(r,rowdata)
        
    def setColor(self,row,column):    
        color = qg.QColorDialog.getColor(qc.Qt.green, self)
        if color.isValid(): 
            print(color,row,column)
            self.fillfunction[column](row,column,color)
            
if __name__=='__main__':
    import sys
    app = qg.QApplication(sys.argv)
    data = [['Row 1', 0,0, qg.QColor(0,0,255)],
             ['Row 2', 0,0, qg.QColor(0,255,0)],
             ['Row 3', 0,0, qg.QColor(255,0,0)],
             ['Row 4', 0,0, qg.QColor(127,127,0)] ]
    
#    data= numpy.array(data)
    w=TableWidget(['Name','V','E','Color'])
#
    w.insertrows(data)
#    for ii,rowdata in enumerate(data):
#        w.insertRow(rowdata)
#    for ii,rowdata in enumerate(data):
#        w.fillrow(ii,rowdata)
#
    w.show()
    sys.exit(app.exec_())
