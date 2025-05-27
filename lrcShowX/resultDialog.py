#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: resultDisplay.py

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *



class resultDisplay(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(self.tr("Results from lrclib"))
        self.currentRow = 0

        self.table = QTableWidget(0, 4)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = [self.tr("Title"), self.tr("Artist"), self.tr("Album"), self.tr("Length")]
        self.table.setHorizontalHeaderLabels(header)
        try:
            self.table.horizontalHeader().restoreState(self.parent.parent.parent.parameter.resultDialogTableState)
        except:
            pass
        try:
            self.restoreGeometry(self.parent.parent.parent.parameter.resultDialogGeometry)
        except:
            pass

        buttonBox = QDialogButtonBox(self)
        cancelButton = QPushButton(self.tr("Cancel"))
        okButton = QPushButton(self.tr("OK"))
        buttonBox.addButton(cancelButton, QDialogButtonBox.ButtonRole.RejectRole)
        buttonBox.addButton(okButton, QDialogButtonBox.ButtonRole.AcceptRole)

        mainLayout = QVBoxLayout(None)
        mainLayout.addWidget(self.table)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


        buttonBox.accepted.connect(self.accept_)
        buttonBox.rejected.connect(self.reject_)
        self.table.cellDoubleClicked.connect(self.finishChoose)
        self.table.cellActivated.connect(self.chooseOne)

    def chooseOne(self, row, col):
        self.currentRow = row

    def finishChoose(self, row, col):
        self.currentRow = row
        self.accept()

    def accept_(self):
        self.parent.parent.parent.parameter.resultDialogTableState = self.table.horizontalHeader().saveState()
        self.parent.parent.parent.parameter.resultDialogGeometry = self.saveGeometry()
        self.accept()

    def reject_(self):
        self.parent.parent.parent.parameter.resultDialogTableState = self.table.horizontalHeader().saveState()
        self.parent.parent.parent.parameter.resultDialogGeometry = self.saveGeometry()
        self.reject()



class multiLocalLrc(QDialog):

    def __init__(self):
        super().__init__()
        self.rstl = QListWidget(self)
        self.rstl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.rstl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rstl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        buttonBox = QDialogButtonBox(self)
        cancelButton = QPushButton(self.tr("Cancel"))
        okButton = QPushButton(self.tr("OK"))
        buttonBox.addButton(cancelButton, QDialogButtonBox.ButtonRole.RejectRole)
        buttonBox.addButton(okButton, QDialogButtonBox.ButtonRole.AcceptRole)

        mainLayout = QVBoxLayout(None)
        mainLayout.addWidget(self.rstl)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.rstl.itemDoubleClicked.connect(self.accept)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = multiLocalLrc(None)
    w.show()

    sys.exit(app.exec())
