# importing the qtWidgets class from the PyQt5 class

from PyQt5 import QtWidgets as qtw


# creating a class of the main wndow and inheriting it from the QtWidgets QWidgrt class
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFrame

from pyQTApp.common import load_welcome


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Hello GUI')
        self.show()  # a method that displays everything on the screen


# instance of the QtWidget window
app = QApplication([])

# instance of the MainWindow() class
main = MainWindow()
layout = main.layout()

frame = qtw.QFrame
welcome_pixmap: QPixmap = load_welcome()
welcome_label = QLabel(main)
welcome_label.setPixmap(welcome_pixmap)

main.show()
# starting the application
app.exec_()