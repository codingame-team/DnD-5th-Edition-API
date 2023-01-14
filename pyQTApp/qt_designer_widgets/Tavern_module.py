from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot, QItemSelection
from PyQt5.QtWidgets import QFrame, QTableWidget, QMainWindow, QTableWidgetItem, QDialog, QWidget

from dao_classes import Character
from main import get_roster
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.common import debug, load_party
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame
# from pyQTApp.wizardry import populate
from pyQTApp.qt_designer_widgets.qt_common import populate, addItem


class Tavern_UI(QWidget):
    def __init__(self, characters_dir: str, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
        self.tavernFrame = QFrame()
        self.ui = Ui_tavernFrame()
        self.ui.setupUi(self.tavernFrame)
        layout = castle_window.layout()

        layout.addWidget(self.tavernFrame)
        self.tavernFrame.setGeometry(castle_ui.castleFrame.geometry())

        # Populate roster

        roster: List[Character] = get_roster(characters_dir)
        debug(f'{len(roster)} characters in roster: \n{roster}')
        table: QTableWidget = self.ui.gilgameshTavern_tableWidget
        populate(table, roster)
        table.selectionModel().selectionChanged.connect(partial(self.disable_remove_button, self.ui))
        self.ui.addToPartyButton.clicked.connect(self.add_char_to_party)

        # Populate party
        party: List[Character] = load_party()
        party_table: QTableWidget = castle_ui.party_tableWidget
        # populate(party_table, party)
        party_table.selectionModel().selectionChanged.connect(self.disable_add_button)
        self.ui.removeFromPartyButton.clicked.connect(self.remove_char_from_party)

        # table.itemDoubleClicked.connect(self.add_character)
        # party_table.itemDoubleClicked.connect(self.remove_character)

        # ui.inspectButton.clicked.connect(inspect_char)
        self.ui.inspectButton.clicked.connect(partial(self.inspect_char, castle_ui))

    @pyqtSlot(QTableWidgetItem)
    def add_character(self, value: QTableWidgetItem):
        global party_table, tg_table, party
        char_name: str = value.data(0)
        char: Character = [c for c in training_grounds if c.name == char_name][0]
        if len(party) == 6:
            debug(f'party is Full!!!')
            return False
        addItem(table=party_table, char=char, party=party)
        row = value.row()
        tg_table.removeRow(row)
        training_grounds.remove(char)
        party.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        debug(f'{len(party)} members in party!!!')

    @pyqtSlot(str)
    def remove_character(self, value: QTableWidgetItem):
        global party_table, tg_table, party, training_grounds
        char_name: str = value.data(0)
        char: Character = [c for c in party if c.name == char_name][0]
        row = value.row()
        party_table.removeRow(row)
        party.remove(char)
        addItem(table=tg_table, char=char, party=training_grounds)
        training_grounds.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        # debug(f'{len(party)} members in party!!!')

    def disable_remove_button(self, ui: Ui_tavernFrame, party: List[Character]):
        self.ui.removeFromPartyButton.setEnabled(False)
        if len(party) < 6:
            self.ui.addToPartyButton.setEnabled(True)

    def disable_add_button(self, ui: Ui_tavernFrame):
        self.ui.addToPartyButton.setEnabled(False)
        self.ui.removeFromPartyButton.setEnabled(True)

    @pyqtSlot()
    def inspect_char():
        global party_table, tg_table, training_grounds
        if party_table.selectedIndexes():
            row: int = party_table.currentRow()
            char_name: str = party_table.item(row, 0).text()
            char: Character = [c for c in party if c.name == char_name][0]
        else:
            row: int = tg_table.currentRow()
            char_name: str = tg_table.item(row, 0).text()
            char: Character = [c for c in training_grounds if c.name == char_name][0]
        character_Dialog = QDialog()
        ui = Ui_character_Dialog()
        ui.setupUi(character_Dialog)
        display_char_sheet(character_Dialog, ui, char)

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        global tg_ui
        debug(f'selected: {selected}')
        debug(f'deselected: {deselected}')
        if training_grounds:
            tg_ui.inspectButton.setEnabled(True)
        else:
            tg_ui.addToPartyButton.setEnabled(False)

    @pyqtSlot()
    def add_char_to_party(self):
        global party_table, tg_table, party, tg_ui
        row: int = tg_table.currentRow()
        char_name: str = tg_table.item(row, 0).text()
        char: Character = [c for c in training_grounds if c.name == char_name][0]
        # debug(f'selected char: {char}')
        if len(party) == 6:
            debug(f'party is Full!!!')
            return False
        addItem(table=party_table, char=char, party=party)
        tg_table.removeRow(row)
        training_grounds.remove(char)
        tg_table.setRowCount(len(training_grounds))
        party.append(char)
        self.disable_add_button()
        self.disable_remove_button()
        if training_grounds:
            tg_ui.inspectButton.setEnabled(True)
        else:
            tg_ui.addToPartyButton.setEnabled(False)
        # debug(f'{len(party)} members in party!!!')

    @pyqtSlot()
    def remove_char_from_party(self):
        global party_table, tg_table, training_grounds
        row: int = party_table.currentRow()
        char_name: str = party_table.item(row, 0).text()
        char: Character = [c for c in party if c.name == char_name][0]
        debug(f'selected char: {char}')
        addItem(table=tg_table, char=char, party=training_grounds)
        party_table.removeRow(row)
        party.remove(char)
        party_table.setRowCount(len(party))
        training_grounds.append(char)
        self.disable_add_button()
        if not party:
            self.disable_remove_button()
        # debug(f'{len(party)} members in party!!!')
