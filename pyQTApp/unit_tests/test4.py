import sys

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from pyQTApp.unit_tests.additional_qt_classes import SpinBox


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

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()