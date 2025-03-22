import os
import sys
from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QTableWidget, QHeaderView, QSizePolicy, QDialog

from dao_classes import Character
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.common import load_welcome, load_party
from pyQTApp.qt_designer_widgets import castleWindow
from pyQTApp.Tavern_module import Tavern_UI

from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame
from pyQTApp.qt_designer_widgets.qt_common import populate_table


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

@pyqtSlot(int, int)
def inspect_char(row: int, column: int):
    # Determine which table was double-clicked
    char_name: str = party_table.item(row, 0).text()
    char: Character = [c for c in party if c.name == char_name][0]
    character_Dialog = QDialog()
    ui = Ui_character_Dialog()
    ui.setupUi(character_Dialog)
    display_char_sheet(character_Dialog, ui, char)

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
    # Set label to fill the entire frame
    castle_ui.welcome_label.setGeometry(castle_ui.castleFrame.rect())
    # Make label resize with frame
    castle_ui.welcome_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    # Ensure label stays aligned with frame
    castle_ui.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    # castle_ui.welcome_label.setPixmap(welcome_pixmap)
    # Get the frame size
    frame_size = castle_ui.welcome_label.size()
    # Scale the pixmap to fit the frame while keeping aspect ratio
    scaled_pixmap = welcome_pixmap.scaled(frame_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    # Set the scaled pixmap
    castle_ui.welcome_label.setPixmap(scaled_pixmap)
    # Make sure the label scales with the frame
    castle_ui.welcome_label.setScaledContents(True)

    castle_ui.actionGilgamesh_Tavern.triggered.connect(partial(gilgamesh_tavern, castle_ui, castle_window))
    castle_ui.actionBoltac_Trading_Post.triggered.connect(partial(boltac_trading_post, castle_ui, castle_window))

    # Populate party
    party: List[Character] = load_party()
    party_table: QTableWidget = castle_ui.party_tableWidget
    populate_table(party_table, party)
    # Make table expand to fill container
    party_table.horizontalHeader().setStretchLastSection(True)
    party_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    party_table.setSortingEnabled(True)
    party_table.cellDoubleClicked.connect(inspect_char)

    castle_window.show()
    sys.exit(app.exec_())
