# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'templeOfCant_QFrame.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_cantFrame(object):
    def setupUi(self, cantFrame):
        cantFrame.setObjectName("cantFrame")
        cantFrame.resize(551, 491)
        cantFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        cantFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(cantFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.saveButton = QtWidgets.QPushButton(cantFrame)
        self.saveButton.setEnabled(False)
        self.saveButton.setObjectName("saveButton")
        self.gridLayout.addWidget(self.saveButton, 2, 1, 1, 1)
        self.char_to_pay_label = QtWidgets.QLabel(cantFrame)
        self.char_to_pay_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.char_to_pay_label.setObjectName("char_to_pay_label")
        self.gridLayout.addWidget(self.char_to_pay_label, 2, 0, 1, 1)
        self.leaveCantButton = QtWidgets.QPushButton(cantFrame)
        self.leaveCantButton.setObjectName("leaveCantButton")
        self.gridLayout.addWidget(self.leaveCantButton, 3, 1, 1, 1)
        self.injured_char_table = QtWidgets.QTableWidget(cantFrame)
        self.injured_char_table.setMaximumSize(QtCore.QSize(551, 431))
        self.injured_char_table.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.injured_char_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.injured_char_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.injured_char_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.injured_char_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.injured_char_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.injured_char_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.injured_char_table.setColumnCount(6)
        self.injured_char_table.setObjectName("injured_char_table")
        self.injured_char_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.injured_char_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.injured_char_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.injured_char_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.injured_char_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.injured_char_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.injured_char_table.setHorizontalHeaderItem(5, item)
        self.gridLayout.addWidget(self.injured_char_table, 1, 0, 1, 2)
        self.char_to_save_label = QtWidgets.QLabel(cantFrame)
        self.char_to_save_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.char_to_save_label.setObjectName("char_to_save_label")
        self.gridLayout.addWidget(self.char_to_save_label, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)

        self.retranslateUi(cantFrame)
        QtCore.QMetaObject.connectSlotsByName(cantFrame)

    def retranslateUi(self, cantFrame):
        _translate = QtCore.QCoreApplication.translate
        cantFrame.setWindowTitle(_translate("cantFrame", "Frame"))
        self.saveButton.setText(_translate("cantFrame", "Heal"))
        self.char_to_pay_label.setText(_translate("cantFrame", "Select party\'s member to pay ->"))
        self.leaveCantButton.setText(_translate("cantFrame", "Leave Temple"))
        item = self.injured_char_table.horizontalHeaderItem(0)
        item.setText(_translate("cantFrame", "Name"))
        item = self.injured_char_table.horizontalHeaderItem(1)
        item.setText(_translate("cantFrame", "Level"))
        item = self.injured_char_table.horizontalHeaderItem(2)
        item.setText(_translate("cantFrame", "Class"))
        item = self.injured_char_table.horizontalHeaderItem(3)
        item.setText(_translate("cantFrame", "Race"))
        item = self.injured_char_table.horizontalHeaderItem(4)
        item.setText(_translate("cantFrame", "Status"))
        item = self.injured_char_table.horizontalHeaderItem(5)
        item.setText(_translate("cantFrame", "Cost"))
        self.char_to_save_label.setText(_translate("cantFrame", "Wo do you want to save?"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    cantFrame = QtWidgets.QFrame()
    ui = Ui_cantFrame()
    ui.setupUi(cantFrame)
    cantFrame.show()
    sys.exit(app.exec_())
