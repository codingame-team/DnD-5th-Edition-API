# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gilgamesh_Tavern_QFrame.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_tavernFrame(object):
    def setupUi(self, tavernFrame):
        tavernFrame.setObjectName("tavernFrame")
        tavernFrame.resize(634, 400)
        tavernFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        tavernFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(tavernFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.gilgameshTavern_tableWidget = QtWidgets.QTableWidget(tavernFrame)
        self.gilgameshTavern_tableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gilgameshTavern_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gilgameshTavern_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gilgameshTavern_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.gilgameshTavern_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.gilgameshTavern_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.gilgameshTavern_tableWidget.setColumnCount(5)
        self.gilgameshTavern_tableWidget.setObjectName("gilgameshTavern_tableWidget")
        self.gilgameshTavern_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.gilgameshTavern_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.gilgameshTavern_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.gilgameshTavern_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.gilgameshTavern_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.gilgameshTavern_tableWidget.setHorizontalHeaderItem(4, item)
        self.gridLayout.addWidget(self.gilgameshTavern_tableWidget, 0, 0, 1, 2)
        self.addToPartyButton = QtWidgets.QPushButton(tavernFrame)
        self.addToPartyButton.setObjectName("addToPartyButton")
        self.gridLayout.addWidget(self.addToPartyButton, 2, 0, 1, 1)
        self.removeFromPartyButton = QtWidgets.QPushButton(tavernFrame)
        self.removeFromPartyButton.setObjectName("removeFromPartyButton")
        self.gridLayout.addWidget(self.removeFromPartyButton, 2, 1, 1, 1)
        self.inspectButton = QtWidgets.QPushButton(tavernFrame)
        self.inspectButton.setObjectName("inspectButton")
        self.gridLayout.addWidget(self.inspectButton, 1, 0, 1, 1)

        self.retranslateUi(tavernFrame)
        QtCore.QMetaObject.connectSlotsByName(tavernFrame)

    def retranslateUi(self, tavernFrame):
        _translate = QtCore.QCoreApplication.translate
        tavernFrame.setWindowTitle(_translate("tavernFrame", "Frame"))
        item = self.gilgameshTavern_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("tavernFrame", "Name"))
        item = self.gilgameshTavern_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("tavernFrame", "Class/Race"))
        item = self.gilgameshTavern_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("tavernFrame", "AC"))
        item = self.gilgameshTavern_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("tavernFrame", "HP"))
        item = self.gilgameshTavern_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("tavernFrame", "Status"))
        self.addToPartyButton.setText(_translate("tavernFrame", "Add to party"))
        self.removeFromPartyButton.setText(_translate("tavernFrame", "Remove from party"))
        self.inspectButton.setText(_translate("tavernFrame", "Inspect"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    tavernFrame = QtWidgets.QFrame()
    ui = Ui_tavernFrame()
    ui.setupUi(tavernFrame)
    tavernFrame.show()
    sys.exit(app.exec_())
