from functools import partial
from typing import List
import os
import sys

from PyQt5.QtCore import pyqtSlot, QItemSelection, Qt
from PyQt5.QtWidgets import (QFrame, QTableWidget, QMainWindow, QWidget, QHeaderView, QSizePolicy, )

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
	sys.path.insert(0, _dnd_5e_core_path)

from dnd_5e_core.entities import Character

# Import from persistence module
from persistence import get_roster, save_party, load_party, save_character

from pyQTApp.character_sheet import CharacterDialog
from pyQTApp.common import debug, update_buttons
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame

from pyQTApp.qt_common import addCharItem, populate_table
from tools.common import get_save_game_path


class Tavern_UI(QWidget):
    def __init__(self, characters_dir: str, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
        self.castle_window = castle_window
        self.castle_ui = castle_ui
        self.tavernFrame = QFrame()
        self.ui = Ui_tavernFrame()
        self.ui.setupUi(self.tavernFrame)
        layout = castle_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.tavernFrame)
        # layout.addWidget(self.tavernFrame, alignment=Qt.AlignmentFlag.AlignRight)
        self.tavernFrame.setGeometry(castle_ui.castleFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.tavernFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Populate party
        # self.party = castle_window.party
        # self.party_table = castle_ui.party_tableWidget

        self.castle_window.party_table.selectionModel().selectionChanged.connect(self.disable_add_button)
        self.ui.removeFromPartyButton.clicked.connect(self.remove_char_from_party)

        # Populate roster
        self.roster: List[Character] = get_roster(characters_dir)
        self.roster = [c for c in self.roster if c not in self.castle_window.party and c.status == 'OK']
        # debug(f"{len(self.roster)} characters in roster: \n{'\n'.join(map(str, self.roster))}")
        self.tg_table: QTableWidget = self.ui.gilgameshTavern_tableWidget
        # Make table expand to fill container
        self.tg_table.horizontalHeader().setStretchLastSection(True)
        self.tg_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tg_table.setSortingEnabled(True)
        # If you want to set an initial sort on a specific column (e.g., column 0)
        # self.tg_table.sortItems(0, Qt.SortOrder.AscendingOrder)  # or Qt.SortOrder.DescendingOrder
        self.tg_table.verticalHeader().setVisible(False)  # This will hide the row numbers
        self.tg_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        populate_table(self.tg_table, self.roster)
        self.tg_table.selectionModel().selectionChanged.connect(partial(self.disable_remove_button))
        self.ui.addToPartyButton.clicked.connect(self.add_character_from_button)
        self.ui.leaveTavernButton.clicked.connect(self.leave_tavern)

        # self.tg_table.cellDoubleClicked.connect(self.add_character_from_cell)
        # self.party_table.cellDoubleClicked.connect(self.remove_character)
        self.tg_table.cellDoubleClicked.connect(self.inspect_char)

    @pyqtSlot()  # For button click
    def leave_tavern(self):
        game_path = get_save_game_path()
        save_party(self.castle_window.party, game_path)
        self.tavernFrame.close()
        if self.castle_window.party:
            update_buttons(frame=self.castle_ui.nav_frame, enabled=True)
        else:
            self.castle_ui.tavernButton.setEnabled(True)

    @pyqtSlot()  # For button click
    def add_character_from_button(self):
        row = self.tg_table.currentRow()
        if row >= 0:  # Make sure a row is selected
            self.add_character_logic(row)

    @pyqtSlot(int, int)  # For cell double-click
    def add_character_from_cell(self, row: int, column: int):
        self.add_character_logic(row)

    def add_character_logic(self, row: int):
        """Common logic for adding a character"""
        char_name: str = self.tg_table.item(row, 0).text()
        char: Character = [c for c in self.roster if c.name == char_name][0]
        if len(self.castle_window.party) == 6:
            debug(f'party is Full!!!')
            return False
        addCharItem(table=self.castle_window.party_table, char=char, char_list=self.castle_window.party)
        self.tg_table.removeRow(row)
        self.roster.remove(char)
        self.castle_window.party.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        self.castle_window.refresh_party_table()
        # if self.roster:
        #     self.ui.addToPartyButton.setEnabled(False)
        # debug(f'{len(self.party)} members in party!!!')

    @pyqtSlot(int, int)
    def remove_character(self, row: int, column: int):
        char_name: str = self.castle_window.party_table.item(row, 0).text()  # Get text from first column
        # debug(f'removing {char_name}')
        char: Character = [c for c in self.castle_window.party if c.name == char_name][0]
        self.castle_window.party_table.removeRow(row)
        self.castle_window.party.remove(char)
        addCharItem(table=self.tg_table, char=char, char_list=self.roster)
        self.roster.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        # if self.roster:
        #     self.ui.addToPartyButton.setEnabled(False)
        # debug(f'{len(self.party)} members in party!!!')

    def disable_remove_button(self):
        self.ui.removeFromPartyButton.setEnabled(False)
        if len(self.castle_window.party) < 6:
            self.ui.addToPartyButton.setEnabled(True)

    def disable_add_button(self):
        self.ui.addToPartyButton.setEnabled(False)
        self.ui.removeFromPartyButton.setEnabled(True)

    @pyqtSlot(int, int)
    def inspect_char(self, row: int, column: int):
        char_name: str = self.tg_table.item(row, 0).text()
        char: Character = [c for c in self.roster if c.name == char_name][0]

        character_dialog = CharacterDialog(char)
        character_dialog.display_sheet()
        if character_dialog.char:
            game_path = get_save_game_path()
            characters_dir = f"{game_path}/characters"
            save_character(character_dialog.char, characters_dir)

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        debug(f"selected: {selected}")
        debug(f"deselected: {deselected}")
        if self.castle_window.party:
            self.ui.inspectButton.setEnabled(True)
        else:
            self.ui.addToPartyButton.setEnabled(False)

    @pyqtSlot()
    def add_char_to_party(self):
        row: int = self.tg_table.currentRow()
        # debug(f"row: {row}")
        char_name: str = self.tg_table.item(row, 0).text()
        char: Character = [c for c in self.roster if c.name == char_name][0]
        # debug(f'selected char: {char}')
        if len(self.castle_window.party) == 6:
            debug(f"party is Full!!!")
            return False
        addCharItem(table=self.castle_window.party_table, char=char, char_list=self.castle_window.party)
        self.tg_table.removeRow(row)
        self.roster.remove(char)
        self.tg_table.setRowCount(len(self.roster))
        self.castle_window.party.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        if self.roster:
            self.ui.inspectButton.setEnabled(True)
        else:
            self.ui.addToPartyButton.setEnabled(False)
        self.castle_window.refresh_party_table()
        # debug(f'{len(party)} members in party!!!')

    @pyqtSlot()
    def remove_char_from_party(self):
        row: int = self.castle_window.party_table.currentRow()
        char_name: str = self.castle_window.party_table.item(row, 0).text()
        char: Character = [c for c in self.castle_window.party if c.name == char_name][0]
        # debug(f"selected char: {char}")
        addCharItem(table=self.tg_table, char=char, char_list=self.roster)
        self.castle_window.party_table.removeRow(row)
        self.castle_window.party.remove(char)
        self.castle_window.party_table.setRowCount(len(self.castle_window.party))
        self.roster.append(char)
        self.disable_add_button()
        if not self.castle_window.party:
            self.disable_remove_button()
            update_buttons(frame=self.castle_ui.nav_frame, enabled=False)
            # self.castle_ui.tavernButton.setEnabled(True)
