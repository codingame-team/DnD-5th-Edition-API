import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QSpinBox


class SpinBox(QSpinBox):
    upClicked = QtCore.pyqtSignal(int, QSpinBox)
    downClicked = QtCore.pyqtSignal(int, QSpinBox)

    def mousePressEvent(self, event):
        last_value = super().value()
        super().mousePressEvent(event)
        value = super().value()
        if value < last_value:
            self.downClicked.emit(-self.singleStep(), self)
        elif value > last_value:
            self.upClicked.emit(self.singleStep(), self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
