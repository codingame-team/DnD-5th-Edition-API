import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QSpinBox, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Click in this window")
        self.str_spinBox = SpinBox()
        self.str_spinBox.setEnabled(True)
        self.setCentralWidget(self.str_spinBox)
        self.str_spinBox.downClicked.connect(lambda: self.setWindowTitle("Down"))
        self.str_spinBox.upClicked.connect(lambda: self.setWindowTitle("Up"))

    def mouseMoveEvent(self, e):
        self.label.setText("mouseMoveEvent")

    def mousePressEvent(self, e):
        self.label.setText("mousePressEvent")

    def mouseReleaseEvent(self, e):
        self.label.setText("mouseReleaseEvent")

    def mouseDoubleClickEvent(self, e):
        self.label.setText("mouseDoubleClickEvent")


class SpinBox(QSpinBox):
    upClicked = QtCore.pyqtSignal(int)
    downClicked = QtCore.pyqtSignal(int)

    def mousePressEvent(self, event):
        last_value = super().value()
        # print(f'clicked old value = {last_value}')
        super(SpinBox, self).mousePressEvent(event)
        # super().mousePressEvent(event)
        # print(f'clicked new value = {self.value()}')
        value = super().value()
        if value < last_value:
            print('decrement')
            self.downClicked.emit(self.singleStep())
        elif value > last_value:
            print('increment')
            self.upClicked.emit(self.singleStep())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
