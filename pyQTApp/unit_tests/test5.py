import sys
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import *
from PyQt5.QtCore import QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QMenu


class Window(QMainWindow):

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)

        self.model = QStandardItemModel(8, 4)
        table = QTableView()
        table.setModel(self.model)

        actionMenu = QMenu(self.tr("&Actions"), self)
        fillAction = actionMenu.addAction(self.tr("&Fill Selection"))
        clearAction = actionMenu.addAction(self.tr("&Clear Selection"))
        selectAllAction = actionMenu.addAction(self.tr("&Select All"))
        self.menuBar().addMenu(actionMenu)

        fillAction.triggered.connect(self.fillSelection)
        clearAction.triggered.connect(self.clearSelection)
        selectAllAction.triggered.connect(self.selectAll)

        self.selectionModel = table.selectionModel()

        self.statusBar()
        self.setCentralWidget(table)

        self.setWindowTitle(self.tr("Selected Items in a Table Model"))

    def fillSelection(self):

        indexes = self.selectionModel.selectedIndexes()

        for index in indexes:
            text = u"(%i,%i)" % (index.row(), index.column())
            self.model.setData(index, text)

    def clearSelection(self):

        indexes = self.selectionModel.selectedIndexes()

        for index in indexes:
            self.model.setData(index, "")

    def selectAll(self):

        parent = QModelIndex()

        topLeft = self.model.index(0, 0, parent)
        bottomRight = self.model.index(
            self.model.rowCount(parent) - 1,
            self.model.columnCount(parent) - 1, parent)

        selection = QItemSelection(topLeft, bottomRight)
        self.selectionModel.select(selection, QItemSelectionModel.Select)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())