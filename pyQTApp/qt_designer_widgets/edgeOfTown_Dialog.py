# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edgeOfTown_Dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_edgeOfTownDialog(object):
    def setupUi(self, edgeOfTownDialog):
        edgeOfTownDialog.setObjectName("edgeOfTownDialog")
        edgeOfTownDialog.resize(210, 218)
        self.gridLayout_2 = QtWidgets.QGridLayout(edgeOfTownDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.nav_frame = QtWidgets.QFrame(edgeOfTownDialog)
        self.nav_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.nav_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.nav_frame.setObjectName("nav_frame")
        self.gridLayout = QtWidgets.QGridLayout(self.nav_frame)
        self.gridLayout.setObjectName("gridLayout")
        self.restartOutPartyButton = QtWidgets.QPushButton(self.nav_frame)
        self.restartOutPartyButton.setEnabled(False)
        self.restartOutPartyButton.setObjectName("restartOutPartyButton")
        self.gridLayout.addWidget(self.restartOutPartyButton, 2, 0, 1, 1)
        self.dungeonButton = QtWidgets.QPushButton(self.nav_frame)
        self.dungeonButton.setObjectName("dungeonButton")
        self.gridLayout.addWidget(self.dungeonButton, 1, 0, 1, 1)
        self.castleButton = QtWidgets.QPushButton(self.nav_frame)
        self.castleButton.setObjectName("castleButton")
        self.gridLayout.addWidget(self.castleButton, 3, 0, 1, 1)
        self.tgButton = QtWidgets.QPushButton(self.nav_frame)
        self.tgButton.setObjectName("tgButton")
        self.gridLayout.addWidget(self.tgButton, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.nav_frame, 0, 0, 1, 1)

        self.retranslateUi(edgeOfTownDialog)
        QtCore.QMetaObject.connectSlotsByName(edgeOfTownDialog)

    def retranslateUi(self, edgeOfTownDialog):
        _translate = QtCore.QCoreApplication.translate
        edgeOfTownDialog.setWindowTitle(_translate("edgeOfTownDialog", "** Edge of Town **"))
        self.restartOutPartyButton.setText(_translate("edgeOfTownDialog", "Restart an \'Out\' Party"))
        self.dungeonButton.setText(_translate("edgeOfTownDialog", "Enter Dungeon"))
        self.castleButton.setText(_translate("edgeOfTownDialog", "Return to Castle"))
        self.tgButton.setText(_translate("edgeOfTownDialog", "Training Grounds"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    edgeOfTownDialog = QtWidgets.QDialog()
    ui = Ui_edgeOfTownDialog()
    ui.setupUi(edgeOfTownDialog)
    edgeOfTownDialog.show()
    sys.exit(app.exec_())
