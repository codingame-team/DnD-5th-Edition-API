import os
import sys
from functools import partial

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel

from pyQTApp.common import load_welcome
from pyQTApp.qt_designer_widgets import castleWindow
from pyQTApp.Tavern_module import Tavern_UI

from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


# @pyqtSlot(Ui_castleWindow, str)
# def boltac_trading_post(castle_ui, value):
#     debug(f"value gilgamesh_tavern = {value}")
#
#     layout = castleWindow.layout()
#     castle_ui.welcome_label.destroy()
#
#     tavernFrame = QFrame()
#     ui = Ui_tavernFrame()
#     ui.setupUi(tavernFrame)
#
#     layout.addWidget(tavernFrame)
#     tavernFrame.setGeometry(castle_ui.castleFrame.geometry())

@pyqtSlot(Ui_castleWindow, QMainWindow, str)
def boltac_trading_post(castle_ui: Ui_castleWindow, castle_window: QMainWindow, value):
    debug(f"value boltac_trading_post = {value}")
    return
    ui = Tavern_UI(characters_dir=characters_dir, castle_window=castle_window, castle_ui=castle_ui)

@pyqtSlot(Ui_castleWindow, QMainWindow, str)
def gilgamesh_tavern(castle_ui: Ui_castleWindow, castle_window: QMainWindow, value):
    debug(f"value gilgamesh_tavern = {value}")
    # castle_ui.welcome_label.destroy()

    tavernFrame = QFrame()
    ui = Tavern_UI(characters_dir=characters_dir, castle_window=castle_window, castle_ui=castle_ui)


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    characters_dir = f"{path}/../gameState/characters"

    app = QApplication(sys.argv)
    castle_window = QMainWindow()
    castle_ui = Ui_castleWindow()
    castle_ui.setupUi(castle_window)

    layout = castle_window.layout()

    welcome_pixmap: QPixmap = load_welcome()
    castle_ui.welcome_label = QLabel(castle_ui.castleFrame)
    castle_ui.welcome_label.setPixmap(welcome_pixmap)

    castle_ui.actionGilgamesh_Tavern.triggered.connect(partial(gilgamesh_tavern, castle_ui, castle_window))
    castle_ui.actionBoltac_Trading_Post.triggered.connect(partial(boltac_trading_post, castle_ui, castle_window))

    castle_window.show()
    sys.exit(app.exec_())
