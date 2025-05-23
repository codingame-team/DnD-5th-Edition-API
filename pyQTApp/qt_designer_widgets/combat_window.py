# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'combat_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_combatWindow(object):
    def setupUi(self, combatWindow):
        combatWindow.setObjectName("combatWindow")
        combatWindow.resize(1038, 600)
        self.centralwidget = QtWidgets.QWidget(combatWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.party_action_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.party_action_groupBox.setObjectName("party_action_groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.party_action_groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.radioButton_4 = QtWidgets.QRadioButton(self.party_action_groupBox)
        self.radioButton_4.setObjectName("radioButton_4")
        self.gridLayout_2.addWidget(self.radioButton_4, 0, 0, 1, 1)
        self.radioButton_5 = QtWidgets.QRadioButton(self.party_action_groupBox)
        self.radioButton_5.setObjectName("radioButton_5")
        self.gridLayout_2.addWidget(self.radioButton_5, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.party_action_groupBox, 1, 3, 1, 1)
        self.char_actions_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.char_actions_groupBox.setEnabled(False)
        self.char_actions_groupBox.setObjectName("char_actions_groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.char_actions_groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton_6 = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.radioButton_6.setObjectName("radioButton_6")
        self.gridLayout.addWidget(self.radioButton_6, 2, 0, 1, 1)
        self.radioButton_3 = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.radioButton_3.setObjectName("radioButton_3")
        self.gridLayout.addWidget(self.radioButton_3, 3, 0, 1, 1)
        self.radioButton_2 = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout.addWidget(self.radioButton_2, 1, 0, 1, 1)
        self.fight_radioButton = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.fight_radioButton.setObjectName("fight_radioButton")
        self.gridLayout.addWidget(self.fight_radioButton, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.char_actions_groupBox, 2, 3, 1, 1)
        self.party_tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.party_tableWidget.sizePolicy().hasHeightForWidth())
        self.party_tableWidget.setSizePolicy(sizePolicy)
        self.party_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.party_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.party_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.party_tableWidget.setColumnCount(8)
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
        item = QtWidgets.QTableWidgetItem()
        self.party_tableWidget.setHorizontalHeaderItem(7, item)
        self.gridLayout_3.addWidget(self.party_tableWidget, 1, 0, 1, 3)
        self.event_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.event_scrollArea.setWidgetResizable(True)
        self.event_scrollArea.setObjectName("event_scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 800, 172))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.event_scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.event_scrollArea, 2, 0, 1, 3)
        self.monsters_tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.monsters_tableWidget.sizePolicy().hasHeightForWidth())
        self.monsters_tableWidget.setSizePolicy(sizePolicy)
        self.monsters_tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.monsters_tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.monsters_tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.monsters_tableWidget.setColumnCount(2)
        self.monsters_tableWidget.setObjectName("monsters_tableWidget")
        self.monsters_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.monsters_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.monsters_tableWidget.setHorizontalHeaderItem(1, item)
        self.gridLayout_3.addWidget(self.monsters_tableWidget, 0, 0, 1, 1)
        self.monster_1_Frame = QtWidgets.QFrame(self.centralwidget)
        self.monster_1_Frame.setMinimumSize(QtCore.QSize(150, 150))
        self.monster_1_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.monster_1_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.monster_1_Frame.setObjectName("monster_1_Frame")
        self.gridLayout_3.addWidget(self.monster_1_Frame, 0, 1, 1, 1)
        self.monster_2_Frame = QtWidgets.QFrame(self.centralwidget)
        self.monster_2_Frame.setMinimumSize(QtCore.QSize(150, 150))
        self.monster_2_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.monster_2_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.monster_2_Frame.setObjectName("monster_2_Frame")
        self.gridLayout_3.addWidget(self.monster_2_Frame, 0, 2, 1, 1)
        self.char_actions_groupBox.raise_()
        self.event_scrollArea.raise_()
        self.party_tableWidget.raise_()
        self.party_action_groupBox.raise_()
        self.monsters_tableWidget.raise_()
        self.monster_1_Frame.raise_()
        self.monster_2_Frame.raise_()
        combatWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(combatWindow)
        self.statusbar.setObjectName("statusbar")
        combatWindow.setStatusBar(self.statusbar)
        self.actionAuthor = QtWidgets.QAction(combatWindow)
        self.actionAuthor.setObjectName("actionAuthor")
        self.actionFile = QtWidgets.QAction(combatWindow)
        self.actionFile.setObjectName("actionFile")
        self.actionLoad = QtWidgets.QAction(combatWindow)
        self.actionLoad.setObjectName("actionLoad")

        self.retranslateUi(combatWindow)
        QtCore.QMetaObject.connectSlotsByName(combatWindow)

    def retranslateUi(self, combatWindow):
        _translate = QtCore.QCoreApplication.translate
        combatWindow.setWindowTitle(_translate("combatWindow", "Combat"))
        self.party_action_groupBox.setTitle(_translate("combatWindow", "Party actions"))
        self.radioButton_4.setText(_translate("combatWindow", "Fight monsters"))
        self.radioButton_5.setText(_translate("combatWindow", "Flee"))
        self.char_actions_groupBox.setTitle(_translate("combatWindow", "#Char# actions"))
        self.radioButton_6.setText(_translate("combatWindow", "Use Item"))
        self.radioButton_3.setText(_translate("combatWindow", "Parry"))
        self.radioButton_2.setText(_translate("combatWindow", "Cast Spell"))
        self.fight_radioButton.setText(_translate("combatWindow", "Fight"))
        item = self.party_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("combatWindow", "Name"))
        item = self.party_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("combatWindow", "Class"))
        item = self.party_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("combatWindow", "Race"))
        item = self.party_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("combatWindow", "AC"))
        item = self.party_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("combatWindow", "HP"))
        item = self.party_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("combatWindow", "HP Max"))
        item = self.party_tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("combatWindow", "Status"))
        item = self.party_tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("combatWindow", "Action"))
        item = self.monsters_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("combatWindow", "Monster"))
        item = self.monsters_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("combatWindow", "Count"))
        self.actionAuthor.setText(_translate("combatWindow", "Author"))
        self.actionFile.setText(_translate("combatWindow", "File"))
        self.actionLoad.setText(_translate("combatWindow", "Load"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    combatWindow = QtWidgets.QMainWindow()
    ui = Ui_combatWindow()
    ui.setupUi(combatWindow)
    combatWindow.show()
    sys.exit(app.exec_())
