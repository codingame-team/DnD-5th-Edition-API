import sys
import pygame
from PyQt5 import QtWidgets, QtCore, QtGui
from my_gui import Ui_MainWindow  # Import the generated form class

class PygameWidget(QtWidgets.QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        # self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        # self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        # self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # roughly 60 FPS
        pygame.init()
        self.screen = pygame.Surface((640, 480))

    def paintEvent(self, event):
        self.screen.fill((0, 0, 0))
        pygame.draw.circle(self.screen, (255, 0, 0), (320, 240), 50)
        image = pygame.image.tostring(self.screen, 'RGB')
        qimage = QtGui.QImage(image, 640, 480, QtGui.QImage.Format_RGB888)
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, qimage)

    def sizeHint(self):
        return QtCore.QSize(640, 480)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def _init_(self):
        super()._init_()
        self.setupUi(self)
        self.pygame_widget = PygameWidget(self)
        self.setCentralWidget(self.pygame_widget)

if __name__ == "_main_":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())