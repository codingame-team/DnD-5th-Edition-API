from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot, QItemSelection, Qt
from PyQt5.QtWidgets import (QFrame, QTableWidget, QMainWindow, QTableWidgetItem, QDialog, QWidget, QHeaderView, QSizePolicy, )

from dao_classes import Character
from main import get_roster
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.common import debug, load_party, save_party
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame

from pyQTApp.qt_designer_widgets.qt_common import addItem, populate_table


class Tavern_UI(QWidget):
    def __init__(self, characters_dir: str, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
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
        # Set background color to white
        self.tavernFrame.setStyleSheet("background-color: gray;")
        # Populate roster
        self.roster: List[Character] = get_roster(characters_dir)
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

        # Populate party
        self.party: List[Character] = load_party()
        self.party_table: QTableWidget = castle_ui.party_tableWidget
        # Make table expand to fill container
        self.party_table.horizontalHeader().setStretchLastSection(True)
        self.party_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.party_table.setSortingEnabled(True)
        # populate_table(self.party_table, self.party)
        self.party_table.selectionModel().selectionChanged.connect(self.disable_add_button)
        self.ui.removeFromPartyButton.clicked.connect(self.remove_char_from_party)

        # self.tg_table.cellDoubleClicked.connect(self.add_character_from_cell)
        # self.party_table.cellDoubleClicked.connect(self.remove_character)
        self.tg_table.cellDoubleClicked.connect(self.inspect_char)
        self.party_table.cellDoubleClicked.connect(self.inspect_char)

        # self.ui.inspectButton.clicked.connect(partial(self.inspect_char))

    @pyqtSlot()  # For button click
    def leave_tavern(self):
        save_party(self.party)
        self.tavernFrame.close()

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
        if len(self.party) == 6:
            debug(f'party is Full!!!')
            return False
        addItem(table=self.party_table, char=char, char_list=self.party)
        self.tg_table.removeRow(row)
        self.roster.remove(char)
        self.party.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        # if self.roster:
        #     self.ui.addToPartyButton.setEnabled(False)
        # debug(f'{len(self.party)} members in party!!!')

    @pyqtSlot(int, int)
    def remove_character(self, row: int, column: int):
        char_name: str = self.party_table.item(row, 0).text()  # Get text from first column
        # debug(f'removing {char_name}')
        char: Character = [c for c in self.party if c.name == char_name][0]
        self.party_table.removeRow(row)
        self.party.remove(char)
        addItem(table=self.tg_table, char=char, char_list=self.roster)
        self.roster.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        # if self.roster:
        #     self.ui.addToPartyButton.setEnabled(False)
        # debug(f'{len(self.party)} members in party!!!')

    def disable_remove_button(self):
        self.ui.removeFromPartyButton.setEnabled(False)
        if len(self.party) < 6:
            self.ui.addToPartyButton.setEnabled(True)

    def disable_add_button(self):
        self.ui.addToPartyButton.setEnabled(False)
        self.ui.removeFromPartyButton.setEnabled(True)

    @pyqtSlot(int, int)
    def inspect_char(self, row: int, column: int):
        # Determine which table was double-clicked
        sender = self.sender()
        if sender == self.party_table:
            char_name: str = self.party_table.item(row, 0).text()
            char: Character = [c for c in self.party if c.name == char_name][0]
        else:  # sender == self.tg_table
            char_name: str = self.tg_table.item(row, 0).text()
            char: Character = [c for c in self.roster if c.name == char_name][0]

        character_Dialog = QDialog()
        ui = Ui_character_Dialog()
        ui.setupUi(character_Dialog)
        display_char_sheet(character_Dialog, ui, char)


    @pyqtSlot(QItemSelection, QItemSelection)
    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        debug(f"selected: {selected}")
        debug(f"deselected: {deselected}")
        if self.party:
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
        if len(self.party) == 6:
            debug(f"party is Full!!!")
            return False
        addItem(table=self.party_table, char=char, char_list=self.party)
        self.tg_table.removeRow(row)
        self.roster.remove(char)
        self.tg_table.setRowCount(len(self.roster))
        self.party.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        if self.roster:
            self.ui.inspectButton.setEnabled(True)
        else:
            self.ui.addToPartyButton.setEnabled(False)
        # debug(f'{len(party)} members in party!!!')

    @pyqtSlot()
    def remove_char_from_party(self):
        row: int = self.party_table.currentRow()
        char_name: str = self.party_table.item(row, 0).text()
        char: Character = [c for c in self.party if c.name == char_name][0]
        # debug(f"selected char: {char}")
        addItem(table=self.tg_table, char=char, char_list=self.roster)
        self.party_table.removeRow(row)
        self.party.remove(char)
        self.party_table.setRowCount(len(self.party))
        self.roster.append(char)
        self.disable_add_button()
        if not self.party:
            self.disable_remove_button()
