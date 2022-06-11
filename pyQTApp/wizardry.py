import sys
from typing import List

from PyQt5.QtCore import pyqtSlot, QItemSelection
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QTableWidget, QTableWidgetItem, QDialog

from dao_classes import Character
from pyQTApp.castleWindow import Ui_castleWindow
from pyQTApp.character_dialog import Ui_character_Dialog
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.common import load_party, get_roster
from pyQTApp.gilgamesh_Tavern_QFrame import Ui_tavernFrame


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


def populate(table: QTableWidget, training_grounds: List[Character]):
    table.setRowCount(len(training_grounds))
    # table.insertRow(len(training_grounds))
    i = 0
    for char in training_grounds:
        table.setItem(i, 0, QTableWidgetItem(char.name))
        table.setItem(i, 1, QTableWidgetItem(f'{char.class_type}/{char.race}'))
        table.setItem(i, 2, QTableWidgetItem(char.armor_class))
        table.setItem(i, 3, QTableWidgetItem(f'{char.hit_points}/{char.max_hit_points}'))
        status = 'Alive' if char.hit_points > 0 else 'DEAD'
        table.setItem(i, 4, QTableWidgetItem(status))
        i += 1
    table.adjustSize()


def addItem(table: QTableWidget, char: Character, party: List[Character]):
    table.setRowCount(len(party))
    table.insertRow(len(party))
    i = len(party)
    table.setItem(i, 0, QTableWidgetItem(char.name))
    table.setItem(i, 1, QTableWidgetItem(f'{char.class_type}/{char.race}'))
    table.setItem(i, 2, QTableWidgetItem(char.armor_class))
    table.setItem(i, 3, QTableWidgetItem(f'{char.hit_points}/{char.max_hit_points}'))
    status = 'Alive' if char.hit_points > 0 else 'DEAD'
    table.setItem(i, 4, QTableWidgetItem(status))


@pyqtSlot(str)
def add_character(value: QTableWidgetItem):
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
    debug(f'{len(party)} members in party!!!')


@pyqtSlot(str)
def remove_character(value: QTableWidgetItem):
    global party_table, tg_table, party, training_grounds
    char_name: str = value.data(0)
    char: Character = [c for c in party if c.name == char_name][0]
    row = value.row()
    party_table.removeRow(row)
    party.remove(char)
    addItem(table=tg_table, char=char, party=training_grounds)
    training_grounds.append(char)
    debug(f'{len(party)} members in party!!!')


@pyqtSlot(QItemSelection, QItemSelection)
def on_selection_changed(selected: QItemSelection, deselected: QItemSelection):
    global ui
    debug(f'selected: {selected}')
    debug(f'deselected: {deselected}')

@pyqtSlot()
def add_char_to_party():
    global party_table, tg_table, party
    row: int = tg_table.currentRow()
    char_name: str = tg_table.item(row, 0).text()
    debug(f'name: {char_name}')
    char: Character = [c for c in training_grounds if c.name == char_name][0]
    debug(f'selected char: {char}')
    if len(party) == 6:
        debug(f'party is Full!!!')
        return False
    addItem(table=party_table, char=char, party=party)
    tg_table.removeRow(row)
    training_grounds.remove(char)
    tg_table.setRowCount(len(training_grounds))
    party.append(char)
    disable_add_button()
    debug(f'{len(party)} members in party!!!')

@pyqtSlot()
def remove_char_from_party():
    global party_table, tg_table, training_grounds
    row: int = party_table.currentRow()
    char_name: str = party_table.item(row, 0).text()
    debug(f'name: {char_name}')
    char: Character = [c for c in party if c.name == char_name][0]
    debug(f'selected char: {char}')
    addItem(table=tg_table, char=char, party=training_grounds)
    party_table.removeRow(row)
    party.remove(char)
    party_table.setRowCount(len(party))
    training_grounds.append(char)
    disable_remove_button()
    debug(f'{len(party)} members in party!!!')

def disable_remove_button():
    global ui2
    ui2.removeFromPartyButton.setEnabled(False)
    if len(party) < 6:
        ui2.addToPartyButton.setEnabled(True)

def disable_add_button():
    global ui2
    ui2.addToPartyButton.setEnabled(False)
    ui2.removeFromPartyButton.setEnabled(True)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    castleWindow = QMainWindow()
    ui = Ui_castleWindow()
    ui.setupUi(castleWindow)

    tavernFrame = QFrame()
    ui2 = Ui_tavernFrame()
    ui2.setupUi(tavernFrame)

    layout = castleWindow.layout()
    layout.addWidget(tavernFrame)
    tavernFrame.setGeometry(ui.castleFrame.geometry())

    # Populate roster
    training_grounds: List[Character] = get_roster()
    debug(f'{len(training_grounds)} characters in roster: \n{training_grounds}')
    tg_table: QTableWidget = ui2.gilgameshTavern_tableWidget
    populate(tg_table, training_grounds)
    tg_table.selectionModel().selectionChanged.connect(disable_remove_button)
    ui2.addToPartyButton.clicked.connect(add_char_to_party)

    # Populate party
    party: List[Character] = load_party()
    party_table: QTableWidget = ui.party_tableWidget
    # populate(party_table, party)
    party_table.selectionModel().selectionChanged.connect(disable_add_button)
    ui2.removeFromPartyButton.clicked.connect(remove_char_from_party)

    tg_table.itemDoubleClicked.connect(add_character)
    party_table.itemDoubleClicked.connect(remove_character)

    ui2.inspectButton.clicked.connect(inspect_char)
    castleWindow.show()
    sys.exit(app.exec_())
