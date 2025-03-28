# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spells_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_spellsDialog(object):
    def setupUi(self, spellsDialog):
        spellsDialog.setObjectName("spellsDialog")
        spellsDialog.resize(542, 364)
        self.gridLayout = QtWidgets.QGridLayout(spellsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.spells_tableWidget = QtWidgets.QTableWidget(spellsDialog)
        self.spells_tableWidget.setMinimumSize(QtCore.QSize(501, 0))
        self.spells_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.spells_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.spells_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.spells_tableWidget.setColumnCount(4)
        self.spells_tableWidget.setObjectName("spells_tableWidget")
        self.spells_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.spells_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.spells_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.spells_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.spells_tableWidget.setHorizontalHeaderItem(3, item)
        self.gridLayout.addWidget(self.spells_tableWidget, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(spellsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(spellsDialog)
        self.buttonBox.accepted.connect(spellsDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(spellsDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(spellsDialog)

    def retranslateUi(self, spellsDialog):
        _translate = QtCore.QCoreApplication.translate
        spellsDialog.setWindowTitle(_translate("spellsDialog", "Dialog"))
        item = self.spells_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("spellsDialog", "Name"))
        item = self.spells_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("spellsDialog", "Level"))
        item = self.spells_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("spellsDialog", "School"))
        item = self.spells_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("spellsDialog", "Range"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    spellsDialog = QtWidgets.QDialog()
    ui = Ui_spellsDialog()
    ui.setupUi(spellsDialog)
    spellsDialog.show()
    sys.exit(app.exec_())
