import os
import sys
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QTableWidget,
    QHeaderView,
    QSizePolicy,
    QDialog,
    QMessageBox,
)

from dao_classes import Character
from main import (
    load_party,
    save_character,
    save_party,
    load_character_collections,
    generate_random_character,
    display_character_sheet,
    get_roster,
)
from pyQTApp.Castle.Boltac_module import Boltac_UI
from pyQTApp.Castle.Cant_module import Cant_UI
from pyQTApp.Castle.Inn_module import Inn_UI
from pyQTApp.EdgeOfTown.Combat_module import Combat_UI
from pyQTApp.EdgeOfTown.Maze_module_Filigrane_Walls import Maze_UI
from pyQTApp.character_sheet import CharacterDialog
from pyQTApp.common import load_welcome, update_buttons
from pyQTApp.Castle.Tavern_module import Tavern_UI

from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.edgeOfTownWindow import Ui_EdgeOfTownWindow
from pyQTApp.qt_common import populate_table, updateCharItem
from pyQTApp.qt_designer_widgets.edgeOfTown_Dialog import Ui_edgeOfTownDialog
from pyQTApp.qt_designer_widgets.training_Grounds_Dialog import (
    Ui_TrainingGrounds_Dialog,
)
from tools.common import get_save_game_path


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


class EdgeOfTown_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_EdgeOfTownWindow()
        self.ui.setupUi(self)
        self.setup_menu_actions()
        # self.maze()
        self.combat()

    @pyqtSlot()
    def combat(self):
        self.combat_window = Combat_UI(edge_of_town_window=self, edge_of_town_ui=self.ui)
        # self.maze_window.show()

    @pyqtSlot()
    def maze(self):
        self.maze_window = Maze_UI(edge_of_town_window=self, edge_of_town_ui=self.ui)
        self.maze_window.show()

    @pyqtSlot()
    def return_to_castle(self):
        game_path: str = get_save_game_path()
        for c in self.combat_window.party:
            char_dir: str = f"{game_path}/characters"
            save_character(c, char_dir)
        save_party(party=self.combat_window.party, _dir=game_path)
        self.close()
        self.castle_window = Castle_UI()
        self.castle_window.show()

    def setup_menu_actions(self):
        """Setup menu action connections"""
        self.ui.actionMaze.triggered.connect(self.maze)
        self.ui.actionCastle.triggered.connect(self.return_to_castle)
        self.ui.actionLeave_game.triggered.connect(self.close)


class Castle_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.edge_of_town_window = None
        self.boltac_window = None
        self.tavern_window = None
        self.ui = Ui_castleWindow()
        self.ui.setupUi(self)
        # self.setup_welcome_screen()
        self.setup_button_actions()
        self.setup_menu_actions()
        self.setup_party_table()
        self.party_table.cellDoubleClicked.connect(self.inspect_char)

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

    @pyqtSlot()
    def boltac_trading_post(self):
        # debug(f"value boltac_trading_post = {value}")
        update_buttons(frame=self.ui.nav_frame, enabled=False)
        self.boltac_window = Boltac_UI(castle_window=self, castle_ui=self.ui)

    @pyqtSlot()
    def gilgamesh_tavern(self):
        # debug(f"value gilgamesh_tavern = {value}")
        # castle_ui.welcome_label.destroy()
        update_buttons(frame=self.ui.nav_frame, enabled=False)
        self.tavern_window = Tavern_UI(
            characters_dir=characters_dir, castle_window=self, castle_ui=self.ui
        )

    @pyqtSlot()
    def edge_of_town(self):
        # self.close()
        self.edgeOfTown_dialog = QDialog(self)  # Store as instance variable
        self.ui_edge = Ui_edgeOfTownDialog()  # Store as instance variable
        self.ui_edge.setupUi(self.edgeOfTown_dialog)

        # Connect signals without lambda
        self.ui_edge.tgButton.clicked.connect(self.training_grounds)
        self.ui_edge.dungeonButton.clicked.connect(self.enter_combat)
        self.ui_edge.castleButton.clicked.connect(self.edgeOfTown_dialog.close)

        self.edgeOfTown_dialog.show()
        # self.edge_of_town_window = EdgeOfTown_UI()
        # self.edge_of_town_window.show()

    @pyqtSlot()
    def training_grounds(self):
        self.edgeOfTown_dialog.close()
        self.tg_dialog = QDialog(self)  # Store as instance variable
        self.ui_tg = Ui_TrainingGrounds_Dialog()  # Store as instance variable
        self.ui_tg.setupUi(self.tg_dialog)

        # Connect signals without lambda
        self.ui_tg.newCharButton.clicked.connect(self.new_character)
        self.ui_tg.randomCharButton.clicked.connect(self.random_character)
        self.ui_tg.charStatusButton.clicked.connect(self.char_status)
        self.ui_tg.deleteCharButton.clicked.connect(self.delete_character)
        self.ui_tg.renameCharButton.clicked.connect(self.rename_character)
        self.ui_tg.classChangeButton.clicked.connect(self.class_change)
        self.ui_tg.castleButton.clicked.connect(self.tg_dialog.close)

        self.tg_dialog.show()

    def new_character(self):
        debug(f"new_character clicked")

    def confirm_character(self, random_char: Character):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Character")
        msg_box.setText(f"Keep {random_char.name}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        result = msg_box.exec_()  # This makes it modal

        if result == QMessageBox.Yes:
            save_character(random_char, _dir=characters_dir)

            # Success message
            QMessageBox.information(
                self,
                "Success",
                f"{random_char.name} successfully added to roster!",
                QMessageBox.Ok,
            )
        else:
            # Discard message
            QMessageBox.information(
                self, "Discarded", "Character discarded.", QMessageBox.Ok
            )

    def random_character(self):
        debug(f"random_character clicked")
        (
            races,
            subraces,
            classes,
            alignments,
            equipments,
            proficiencies,
            names,
            human_names,
            spells,
        ) = load_character_collections()
        roster = get_roster(characters_dir)
        random_char: Character = generate_random_character(
            roster, races, subraces, classes, names, human_names, spells
        )
        character_dialog = CharacterDialog(random_char)
        character_dialog.display_sheet()
        display_character_sheet(char=random_char)
        self.confirm_character(random_char)

    def char_status(self):
        debug(f"char_status clicked")

    def delete_character(self):
        debug(f"delete_character clicked")

    def rename_character(self):
        debug(f"rename_character clicked")

    def class_change(self):
        debug(f"class_change clicked")

    @pyqtSlot()
    def enter_combat(self):
        self.close()
        self.edgeOfTown_dialog.close()
        self.edge_of_town_window = EdgeOfTown_UI()
        self.edge_of_town_window.show()

    @pyqtSlot()
    def adventurer_inn(self):
        update_buttons(frame=self.ui.nav_frame, enabled=False)
        self.inn_window = Inn_UI(castle_window=self, castle_ui=self.ui)

    @pyqtSlot()
    def temple_of_cant(self):
        update_buttons(frame=self.ui.nav_frame, enabled=False)
        self.cant_window = Cant_UI(castle_window=self, castle_ui=self.ui)

    def setup_button_actions(self):
        """Setup button action connections"""
        self.ui.boltacButton.clicked.connect(self.boltac_trading_post)
        self.ui.tavernButton.clicked.connect(self.gilgamesh_tavern)
        self.ui.edgeButton.clicked.connect(self.edge_of_town)
        self.ui.innButton.clicked.connect(self.adventurer_inn)
        self.ui.cantButton.clicked.connect(self.temple_of_cant)

    def setup_menu_actions(self):
        """Setup menu action connections"""
        self.ui.actionGilgamesh_Tavern.triggered.connect(self.gilgamesh_tavern)
        self.ui.actionBoltac_Trading_Post.triggered.connect(self.boltac_trading_post)
        self.ui.actionEdge_of_Town.triggered.connect(self.edge_of_town)

    def setup_party_table(self):
        """Setup and populate the party table"""
        game_path = get_save_game_path()
        self.party: List[Character] = load_party(game_path)
        self.party_table: QTableWidget = self.ui.party_tableWidget
        if self.party:
            self.refresh_party_table()
        else:
            update_buttons(frame=self.ui.nav_frame, enabled=False)
            self.ui.tavernButton.setEnabled(True)

    def refresh_party_table(self):
        # Configure table
        self.party = list(filter(lambda c: c.status == "OK", self.party))
        populate_table(self.party_table, self.party)
        self.party_table.horizontalHeader().setStretchLastSection(True)
        self.party_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.party_table.setSortingEnabled(True)
        # buttons = [
        #     self.ui.edgeButton,
        #     self.ui.innButton,
        #     self.ui.cantButton,
        #     self.ui.boltacButton,
        # ]
        # for button in buttons:
        #     flag: bool = len(self.party) > 0
        #     button.setEnabled(flag)

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
