# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'boltac_Trading_Post_QFrame.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_boltacFrame(object):
    def setupUi(self, boltacFrame):
        boltacFrame.setObjectName("boltacFrame")
        boltacFrame.resize(551, 491)
        boltacFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        boltacFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(boltacFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.boltacSell_tableWidget = QtWidgets.QTableWidget(boltacFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boltacSell_tableWidget.sizePolicy().hasHeightForWidth())
        self.boltacSell_tableWidget.setSizePolicy(sizePolicy)
        self.boltacSell_tableWidget.setMaximumSize(QtCore.QSize(551, 431))
        self.boltacSell_tableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.boltacSell_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.boltacSell_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.boltacSell_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.boltacSell_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.boltacSell_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.boltacSell_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.boltacSell_tableWidget.setColumnCount(3)
        self.boltacSell_tableWidget.setObjectName("boltacSell_tableWidget")
        self.boltacSell_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.boltacSell_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.boltacSell_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.boltacSell_tableWidget.setHorizontalHeaderItem(2, item)
        self.gridLayout.addWidget(self.boltacSell_tableWidget, 0, 0, 1, 3)
        self.sellButton = QtWidgets.QPushButton(boltacFrame)
        self.sellButton.setEnabled(False)
        self.sellButton.setObjectName("sellButton")
        self.gridLayout.addWidget(self.sellButton, 0, 3, 1, 1)
        self.boltacBuy_tableWidget = QtWidgets.QTableWidget(boltacFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boltacBuy_tableWidget.sizePolicy().hasHeightForWidth())
        self.boltacBuy_tableWidget.setSizePolicy(sizePolicy)
        self.boltacBuy_tableWidget.setMaximumSize(QtCore.QSize(551, 431))
        self.boltacBuy_tableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.boltacBuy_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.boltacBuy_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.boltacBuy_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.boltacBuy_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.boltacBuy_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.boltacBuy_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.boltacBuy_tableWidget.setColumnCount(3)
        self.boltacBuy_tableWidget.setObjectName("boltacBuy_tableWidget")
        self.boltacBuy_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.boltacBuy_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.boltacBuy_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.boltacBuy_tableWidget.setHorizontalHeaderItem(2, item)
        self.gridLayout.addWidget(self.boltacBuy_tableWidget, 1, 0, 1, 3)
        self.poolGoldButton = QtWidgets.QPushButton(boltacFrame)
        self.poolGoldButton.setEnabled(False)
        self.poolGoldButton.setObjectName("poolGoldButton")
        self.gridLayout.addWidget(self.poolGoldButton, 3, 0, 1, 1)
        self.divvyGoldButton = QtWidgets.QPushButton(boltacFrame)
        self.divvyGoldButton.setEnabled(False)
        self.divvyGoldButton.setObjectName("divvyGoldButton")
        self.gridLayout.addWidget(self.divvyGoldButton, 3, 1, 1, 1)
        self.buyButton = QtWidgets.QPushButton(boltacFrame)
        self.buyButton.setEnabled(False)
        self.buyButton.setObjectName("buyButton")
        self.gridLayout.addWidget(self.buyButton, 1, 3, 1, 1)
        self.character_label = QtWidgets.QLabel(boltacFrame)
        self.character_label.setObjectName("character_label")
        self.gridLayout.addWidget(self.character_label, 2, 0, 1, 1)
        self.leaveBoltacButton = QtWidgets.QPushButton(boltacFrame)
        self.leaveBoltacButton.setEnabled(False)
        self.leaveBoltacButton.setObjectName("leaveBoltacButton")
        self.gridLayout.addWidget(self.leaveBoltacButton, 3, 3, 1, 1)

        self.retranslateUi(boltacFrame)
        QtCore.QMetaObject.connectSlotsByName(boltacFrame)

    def retranslateUi(self, boltacFrame):
        _translate = QtCore.QCoreApplication.translate
        boltacFrame.setWindowTitle(_translate("boltacFrame", "Frame"))
        item = self.boltacSell_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("boltacFrame", "Name"))
        item = self.boltacSell_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("boltacFrame", "Cost"))
        item = self.boltacSell_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("boltacFrame", "Type"))
        self.sellButton.setText(_translate("boltacFrame", "Sell"))
        item = self.boltacBuy_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("boltacFrame", "Name"))
        item = self.boltacBuy_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("boltacFrame", "Cost"))
        item = self.boltacBuy_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("boltacFrame", "Type"))
        self.poolGoldButton.setText(_translate("boltacFrame", "Pool Gold"))
        self.divvyGoldButton.setText(_translate("boltacFrame", "Divvy Gold"))
        self.buyButton.setText(_translate("boltacFrame", "Buy"))
        self.character_label.setText(_translate("boltacFrame", "Please select character!"))
        self.leaveBoltacButton.setText(_translate("boltacFrame", "Leave Boltac"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    boltacFrame = QtWidgets.QFrame()
    ui = Ui_boltacFrame()
    ui.setupUi(boltacFrame)
    boltacFrame.show()
    sys.exit(app.exec_())
