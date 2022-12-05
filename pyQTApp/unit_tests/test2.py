import sys
from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider,
    QVBoxLayout, QApplication)


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def printLabel(self, str):
        print(str)

    def logLabel(self, str):
        '''log to a file'''
        pass

    def initUI(self):

        lcd = QLCDNumber(self)
        sld = QSlider(Qt.Horizontal, self)

        vbox = QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(sld)

        self.setLayout(vbox)

        #redundant connections
        sld.valueChanged.connect(lcd.display)
        sld.valueChanged.connect(self.printLabel)
        sld.valueChanged.connect(self.logLabel)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Signal & slot')
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())