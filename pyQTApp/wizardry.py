import os
import sys
from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFrame,
    QLabel,
    QTableWidget,
    QHeaderView,
    QSizePolicy,
    QDialog,
)

from dao_classes import Character
from main import load_party, save_character, save_party
from pyQTApp.Boltac_module import Boltac_UI
from pyQTApp.character_sheet import CharacterDialog
from pyQTApp.common import load_welcome
from pyQTApp.qt_designer_widgets import castleWindow
from pyQTApp.Tavern_module import Tavern_UI

from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_designer_widgets.combat_window import Ui_combatWindow
from pyQTApp.qt_designer_widgets.edgeOfTownWindow import Ui_EdgeOfTownWindow
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame
from pyQTApp.qt_designer_widgets.qt_common import populate_table, updateCharItem
from tools.common import get_save_game_path


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


class Maze_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_combatWindow()
        self.ui.setupUi(self)


class EdgeOfTown_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_EdgeOfTownWindow()
        self.ui.setupUi(self)


class Castle_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.edge_of_town_window = None
        self.boltac_window = None
        self.tavern_window = None
        self.ui = Ui_castleWindow()
        self.ui.setupUi(self)
        self.setup_welcome_screen()
        self.setup_menu_actions()
        self.setup_party_table()

    def setup_welcome_screen(self):
        """Setup the welcome screen with scaled image"""
        welcome_pixmap: QPixmap = load_welcome()
        self.ui.welcome_label = QLabel(self.ui.castleFrame)

        # Set label properties
        self.ui.welcome_label.setGeometry(self.ui.castleFrame.rect())
        self.ui.welcome_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.ui.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Scale and set the welcome image
        frame_size = self.ui.welcome_label.size()
        scaled_pixmap = welcome_pixmap.scaled(
            frame_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.ui.welcome_label.setPixmap(scaled_pixmap)
        self.ui.welcome_label.setScaledContents(True)

    @pyqtSlot(str)
    def boltac_trading_post(
        self, castle_ui: Ui_castleWindow, castle_window: QMainWindow, value
    ):
        # debug(f"value boltac_trading_post = {value}")
        self.boltac_window = Boltac_UI(
            castle_window=self.castle_window, castle_ui=self.castle_ui
        )

    @pyqtSlot(str)
    def gilgamesh_tavern(self, value):
        # debug(f"value gilgamesh_tavern = {value}")
        # castle_ui.welcome_label.destroy()
        self.tavern_window = Tavern_UI(
            characters_dir=characters_dir,
            castle_window=self.castle_window,
            castle_ui=self.castle_ui,
        )

    @pyqtSlot()
    def edge_of_town(self):
        self.close()
        self.combat_window = Maze_UI()
        self.combat_window.show()
        # self.edge_of_town_window = EdgeOfTown_UI()
        # self.edge_of_town_window.show()

    def setup_menu_actions(self):
        """Setup menu action connections"""
        self.ui.actionGilgamesh_Tavern.triggered.connect(
            partial(self.gilgamesh_tavern, self.ui, self)
        )
        self.ui.actionBoltac_Trading_Post.triggered.connect(
            partial(self.boltac_trading_post, self.ui, self)
        )
        self.ui.actionEdge_of_Town.triggered.connect(self.edge_of_town)

    def setup_party_table(self):
        """Setup and populate the party table"""
        game_path = get_save_game_path()
        self.party: List[Character] = load_party(game_path)
        self.party_table: QTableWidget = self.ui.party_tableWidget

        # Configure table
        populate_table(self.party_table, self.party)
        self.party_table.horizontalHeader().setStretchLastSection(True)
        self.party_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.party_table.setSortingEnabled(True)
        self.party_table.cellDoubleClicked.connect(self.inspect_char)

    @pyqtSlot(int, int)
    def inspect_char(self, row: int, column: int):
        # Determine which table was double-clicked
        char_name: str = self.party_table.item(row, 0).text()
        char: Character = [c for c in self.party if c.name == char_name][0]
        character_dialog = CharacterDialog(char)
        if character_dialog.display_sheet():
            debug(f"saving character {char.name}")
            save_character(character_dialog.char, characters_dir)
            save_party(self.party, game_path)
            updateCharItem(table=self.party_table, char=char, char_index=row)


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    game_path = get_save_game_path()
    characters_dir = f"{game_path}/characters"

    app = QApplication(sys.argv)
    castle_window = Castle_UI()
    castle_window.show()
    sys.exit(app.exec_())
