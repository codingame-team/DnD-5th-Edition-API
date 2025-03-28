# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edgeOfTownWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EdgeOfTownWindow(object):
    def setupUi(self, EdgeOfTownWindow):
        EdgeOfTownWindow.setObjectName("EdgeOfTownWindow")
        EdgeOfTownWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(EdgeOfTownWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mazeFrame = QtWidgets.QFrame(self.centralwidget)
        self.mazeFrame.setGeometry(QtCore.QRect(0, 0, 801, 561))
        self.mazeFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mazeFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mazeFrame.setObjectName("mazeFrame")
        EdgeOfTownWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(EdgeOfTownWindow)
        self.statusbar.setObjectName("statusbar")
        EdgeOfTownWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(EdgeOfTownWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuEdge_of_Town = QtWidgets.QMenu(self.menubar)
        self.menuEdge_of_Town.setObjectName("menuEdge_of_Town")
        EdgeOfTownWindow.setMenuBar(self.menubar)
        self.actionMaze = QtWidgets.QAction(EdgeOfTownWindow)
        self.actionMaze.setObjectName("actionMaze")
        self.actionRestart_an_OUT_party = QtWidgets.QAction(EdgeOfTownWindow)
        self.actionRestart_an_OUT_party.setObjectName("actionRestart_an_OUT_party")
        self.actionTraining_grounds = QtWidgets.QAction(EdgeOfTownWindow)
        self.actionTraining_grounds.setObjectName("actionTraining_grounds")
        self.actionLeave_game = QtWidgets.QAction(EdgeOfTownWindow)
        self.actionLeave_game.setObjectName("actionLeave_game")
        self.actionCastle = QtWidgets.QAction(EdgeOfTownWindow)
        self.actionCastle.setObjectName("actionCastle")
        self.menuEdge_of_Town.addAction(self.actionMaze)
        self.menuEdge_of_Town.addAction(self.actionRestart_an_OUT_party)
        self.menuEdge_of_Town.addAction(self.actionTraining_grounds)
        self.menuEdge_of_Town.addAction(self.actionLeave_game)
        self.menuEdge_of_Town.addAction(self.actionCastle)
        self.menubar.addAction(self.menuEdge_of_Town.menuAction())

        self.retranslateUi(EdgeOfTownWindow)
        QtCore.QMetaObject.connectSlotsByName(EdgeOfTownWindow)

    def retranslateUi(self, EdgeOfTownWindow):
        _translate = QtCore.QCoreApplication.translate
        EdgeOfTownWindow.setWindowTitle(_translate("EdgeOfTownWindow", "Edge of Town"))
        self.menuEdge_of_Town.setTitle(_translate("EdgeOfTownWindow", "Edge of Town"))
        self.actionMaze.setText(_translate("EdgeOfTownWindow", "Maze"))
        self.actionRestart_an_OUT_party.setText(_translate("EdgeOfTownWindow", "Restart an OUT party"))
        self.actionTraining_grounds.setText(_translate("EdgeOfTownWindow", "Training grounds"))
        self.actionLeave_game.setText(_translate("EdgeOfTownWindow", "Leave game"))
        self.actionCastle.setText(_translate("EdgeOfTownWindow", "Return to Castle"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EdgeOfTownWindow = QtWidgets.QMainWindow()
    ui = Ui_EdgeOfTownWindow()
    ui.setupUi(EdgeOfTownWindow)
    EdgeOfTownWindow.show()
    sys.exit(app.exec_())
