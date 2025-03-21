# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'castleWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_castleWindow(object):
    def setupUi(self, castleWindow):
        castleWindow.setObjectName("castleWindow")
        castleWindow.resize(976, 751)
        castleWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(castleWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.party_tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.party_tableWidget.setGeometry(QtCore.QRect(30, 450, 551, 211))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.party_tableWidget.setFont(font)
        self.party_tableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.party_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.party_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.party_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.party_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.party_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.party_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.party_tableWidget.setGridStyle(QtCore.Qt.DashLine)
        self.party_tableWidget.setColumnCount(7)
        self.party_tableWidget.setObjectName("party_tableWidget")
        self.party_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(6, item)
        self.castleFrame = QtWidgets.QFrame(self.centralwidget)
        self.castleFrame.setGeometry(QtCore.QRect(30, 10, 551, 431))
        self.castleFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.castleFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.castleFrame.setObjectName("castleFrame")
        castleWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(castleWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 976, 22))
        self.menubar.setObjectName("menubar")
        self.menuCastle = QtWidgets.QMenu(self.menubar)
        self.menuCastle.setObjectName("menuCastle")
        castleWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(castleWindow)
        self.statusbar.setObjectName("statusbar")
        castleWindow.setStatusBar(self.statusbar)
        self.actionGilgamesh_Tavern = QtWidgets.QAction(castleWindow)
        self.actionGilgamesh_Tavern.setObjectName("actionGilgamesh_Tavern")
        self.actionAdventurer_Inn = QtWidgets.QAction(castleWindow)
        self.actionAdventurer_Inn.setObjectName("actionAdventurer_Inn")
        self.actionTemple_of_Cant = QtWidgets.QAction(castleWindow)
        self.actionTemple_of_Cant.setObjectName("actionTemple_of_Cant")
        self.actionBoltac_Trading_Post = QtWidgets.QAction(castleWindow)
        self.actionBoltac_Trading_Post.setObjectName("actionBoltac_Trading_Post")
        self.actionEdge_of_Town = QtWidgets.QAction(castleWindow)
        self.actionEdge_of_Town.setObjectName("actionEdge_of_Town")
        self.menuCastle.addAction(self.actionGilgamesh_Tavern)
        self.menuCastle.addAction(self.actionAdventurer_Inn)
        self.menuCastle.addAction(self.actionTemple_of_Cant)
        self.menuCastle.addAction(self.actionBoltac_Trading_Post)
        self.menuCastle.addAction(self.actionEdge_of_Town)
        self.menubar.addAction(self.menuCastle.menuAction())

        self.retranslateUi(castleWindow)
        QtCore.QMetaObject.connectSlotsByName(castleWindow)

    def retranslateUi(self, castleWindow):
        _translate = QtCore.QCoreApplication.translate
        castleWindow.setWindowTitle(_translate("castleWindow", "CASTLE"))
        item = self.party_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("castleWindow", "Name"))
        item = self.party_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("castleWindow", "Class"))
        item = self.party_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("castleWindow", "Race"))
        item = self.party_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("castleWindow", "AC"))
        item = self.party_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("castleWindow", "HP"))
        item = self.party_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("castleWindow", "HP Max"))
        item = self.party_tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("castleWindow", "Status"))
        self.menuCastle.setTitle(_translate("castleWindow", "Castle"))
        self.actionGilgamesh_Tavern.setText(_translate("castleWindow", "Gilgamesh\'s Tavern"))
        self.actionAdventurer_Inn.setText(_translate("castleWindow", "Adventurer\'s Inn"))
        self.actionTemple_of_Cant.setText(_translate("castleWindow", "Temple of Cant"))
        self.actionBoltac_Trading_Post.setText(_translate("castleWindow", "Boltac\'s Trading Post"))
        self.actionEdge_of_Town.setText(_translate("castleWindow", "Edge of Town"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    castleWindow = QtWidgets.QMainWindow()
    ui = Ui_castleWindow()
    ui.setupUi(castleWindow)
    castleWindow.show()
    sys.exit(app.exec_())
