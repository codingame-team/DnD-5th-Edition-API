# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'combat_select_Dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_combatSelectDialog(object):
    def setupUi(self, combatSelectDialog):
        combatSelectDialog.setObjectName("combatSelectDialog")
        combatSelectDialog.resize(826, 378)
        self.gridLayout_2 = QtWidgets.QGridLayout(combatSelectDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.char_actions_groupBox = QtWidgets.QGroupBox(combatSelectDialog)
        self.char_actions_groupBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.char_actions_groupBox.sizePolicy().hasHeightForWidth())
        self.char_actions_groupBox.setSizePolicy(sizePolicy)
        self.char_actions_groupBox.setObjectName("char_actions_groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.char_actions_groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton_2 = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout.addWidget(self.radioButton_2, 1, 0, 1, 1)
        self.radioButton_3 = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.radioButton_3.setObjectName("radioButton_3")
        self.gridLayout.addWidget(self.radioButton_3, 3, 0, 1, 1)
        self.radioButton_6 = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.radioButton_6.setObjectName("radioButton_6")
        self.gridLayout.addWidget(self.radioButton_6, 2, 0, 1, 1)
        self.fight_radioButton = QtWidgets.QRadioButton(self.char_actions_groupBox)
        self.fight_radioButton.setObjectName("fight_radioButton")
        self.gridLayout.addWidget(self.fight_radioButton, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.char_actions_groupBox, 1, 0, 3, 1)
        self.pushButton = QtWidgets.QPushButton(combatSelectDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 1, 1, 1, 1)
        self.party_tableWidget = QtWidgets.QTableWidget(combatSelectDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
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
        self.gridLayout_2.addWidget(self.party_tableWidget, 0, 0, 1, 4)
        self.buttonBox = QtWidgets.QDialogButtonBox(combatSelectDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.pushButton_2 = QtWidgets.QPushButton(combatSelectDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 2, 1, 1, 1)

        self.retranslateUi(combatSelectDialog)
        QtCore.QMetaObject.connectSlotsByName(combatSelectDialog)

    def retranslateUi(self, combatSelectDialog):
        _translate = QtCore.QCoreApplication.translate
        combatSelectDialog.setWindowTitle(_translate("combatSelectDialog", "Dialog"))
        self.char_actions_groupBox.setTitle(_translate("combatSelectDialog", "#Char# actions"))
        self.radioButton_2.setText(_translate("combatSelectDialog", "Cast Spell"))
        self.radioButton_3.setText(_translate("combatSelectDialog", "Parry"))
        self.radioButton_6.setText(_translate("combatSelectDialog", "Use Item"))
        self.fight_radioButton.setText(_translate("combatSelectDialog", "Fight"))
        self.pushButton.setText(_translate("combatSelectDialog", ">>"))
        item = self.party_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("combatSelectDialog", "Name"))
        item = self.party_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("combatSelectDialog", "Class"))
        item = self.party_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("combatSelectDialog", "Race"))
        item = self.party_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("combatSelectDialog", "AC"))
        item = self.party_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("combatSelectDialog", "HP"))
        item = self.party_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("combatSelectDialog", "HP Max"))
        item = self.party_tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("combatSelectDialog", "Status"))
        item = self.party_tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("combatSelectDialog", "Action"))
        self.pushButton_2.setText(_translate("combatSelectDialog", "<<"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    combatSelectDialog = QtWidgets.QDialog()
    ui = Ui_combatSelectDialog()
    ui.setupUi(combatSelectDialog)
    combatSelectDialog.show()
    sys.exit(app.exec_())
