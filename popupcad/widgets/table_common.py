# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import qt.QtCore as qc
import qt.QtGui as qg

class CommonTableWidget(qg.QTableWidget):
    pass

    def calc_table_width2(self):
        width = 0
        width += self.verticalHeader().width()
        width += sum([self.columnWidth(ii)
                      for ii in range(self.columnCount())])
        width += self.style().pixelMetric(qg.QStyle.PM_ScrollBarExtent)
        width += self.frameWidth() * 2
        return width

    def reset_min_width(self):
        self.horizontalHeader().setStretchLastSection(False)
        self.setMinimumWidth(self.calc_table_width2())
        self.horizontalHeader().setStretchLastSection(True)
#
#    def calc_table_width(self):
#        w = sum([self.columnWidth(ii) for ii in range(self.columnCount())])
#        w2 = self.frameWidth() * 2
#        return w + w2
        
    def row_add(self, items):
        ii = self.rowCount()
        self.setRowCount(ii + 1)
        for jj, item in enumerate(items):
            self.setItem(ii, jj, item)
        self.reset_min_width()

    def row_add_empty(self, items):
        ii = self.rowCount()
        self.setRowCount(ii + 1)
        for jj, item in enumerate(items):
            self.setItem(ii, jj, item)
        self.reset_min_width()

    def row_remove(self):
        ii = self.currentRow()
        kk = self.currentColumn()
        self.removeRow(ii)
        self.setCurrentCell(ii, kk)

    def row_shift_up(self):
        ii = self.currentRow()
        kk = self.currentColumn()
        if ii > 0:
            cols = self.columnCount()
            items_below = [self.takeItem(ii, jj) for jj in range(cols)]
            items_above = [self.takeItem(ii - 1, jj) for jj in range(cols)]
            [self.setItem(ii, jj, item)
             for item, jj in zip(items_above, range(cols))]
            [self.setItem(ii - 1, jj, item)
             for item, jj in zip(items_below, range(cols))]
        self.setCurrentCell(ii - 1, kk)

    def row_shift_down(self):
        ii = self.currentRow()
        kk = self.currentColumn()
        if ii < self.rowCount() - 1:
            cols = self.columnCount()
            items_below = [self.takeItem(ii + 1, jj) for jj in range(cols)]
            items_above = [self.takeItem(ii, jj) for jj in range(cols)]
            [self.setItem(ii + 1, jj, item)
             for item, jj in zip(items_above, range(cols))]
            [self.setItem(ii, jj, item)
             for item, jj in zip(items_below, range(cols))]
        self.setCurrentCell(ii + 1, kk)

    def reset(self):
        for ii in range(self.rowCount()):
            self.removeRow(0)        
            
class Table(CommonTableWidget):

    def __init__(self, data_class,delegate):
        super(Table, self).__init__()
        self.data_class = data_class
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setRowCount(0)

        self.setColumnCount(self.data_class.column_count)
        self.setHorizontalHeaderLabels(self.data_class.header_labels)

#        self.resizeColumnsToContents()
#        self.reset_min_width()
#        self.setHorizontalScrollBarPolicy(
#            qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setItemDelegate(delegate(self.data_class))
        self.cellClicked.connect(self.cell_clicked)

    def row_add(self, *args, **kwargs):
        items = self.data_class.row_add(*args, **kwargs)
        super(Table,self).row_add(items)

    def row_add_empty(self, *args, **kwargs):
        items = self.data_class.row_add_empty(*args, **kwargs)
        super(Table,self).row_add_empty(items)
    def cell_clicked(self,row,column):
        self.data_class.cell_clicked(row,column,self)
    def export_data(self):
        return [
            [
                self.item(
                    ii,
                    jj).data(
                    qc.Qt.ItemDataRole.UserRole) for jj in range(
                    self.data_class.column_count)] for ii in range(
                        self.rowCount())]

class Delegate(qg.QStyledItemDelegate):

    def __init__(self, data_class, parent=None):
        super(Delegate, self).__init__(parent)
        self.data_class = data_class

    def createEditor(self, parent, option, index):
        return self.data_class.create_editor(parent, option, index, self)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, qg.QAbstractItemDelegate.NoHint)

    def updateEditorGeometry(self, editor, option, index):
        return self.data_class.update_editor_geometry(editor, option, index)

    def setEditorData(self, editor, index):
        return self.data_class.set_editor_data(editor, index, self)

    def setModelData(self, editor, model, index):
        return self.data_class.set_model_data(editor, model, index, self)

                        
class TableControl(qg.QWidget):

    def __init__(self, table, *args, **kwargs):
        super(TableControl, self).__init__(*args, **kwargs)
        main_layout = qg.QHBoxLayout()

        button_add = qg.QPushButton('+')
        button_remove = qg.QPushButton('-')
        button_up = qg.QPushButton('up')
        button_down = qg.QPushButton('down')

        button_add.clicked.connect(table.row_add_empty)
        button_remove.clicked.connect(table.row_remove)
        button_up.clicked.connect(table.row_shift_up)
        button_down.clicked.connect(table.row_shift_down)

        sublayout1 = qg.QVBoxLayout()
        sublayout1.addWidget(button_add)
        sublayout1.addWidget(button_remove)
        sublayout1.addStretch()
        sublayout1.addWidget(button_up)
        sublayout1.addWidget(button_down)

        main_layout.addWidget(table)
        main_layout.addLayout(sublayout1)
        self.setLayout(main_layout)            