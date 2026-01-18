from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTableWidget, QHeaderView, QTableWidgetItem

from dao_classes import Character, CharAction, Monster
from pyQTApp.common import debug
from pyQTApp.qt_common import populate_table, populate_monsters_table
from pyQTApp.qt_designer_widgets.combat_select_Dialog import Ui_combatSelectDialog
from pyQTApp.qt_designer_widgets.monsters_select_Dialog import Ui_monsters_select_Dialog
from tools.common import get_save_game_path


class CombatDialog(QDialog):
    def __init__(self, party: List[Character], monsters: List[Monster]):
        super().__init__()
        self.party = party
        self.monsters = monsters
        self.ui = Ui_combatSelectDialog()
        self.actions: dict[str, CharAction] = {}  # Add flag to track modifications
        self.ui.setupUi(self)
        self.setup_party_table()
        self.ui.char_actions_groupBox.setTitle(self.party[0].name)
        self.ui.fight_radioButton.clicked.connect(self.select_monsters)
        self.index = 0
        self.exec()

    @pyqtSlot()
    def select_monsters(self):
        """Select monsters for combat"""
        select_dialog = QDialog(self)
        ui = Ui_monsters_select_Dialog()
        ui.setupUi(self)
        monster_names = [m.name for m in self.monsters]
        unique_monsters = list(set(monster_names))
        monsters_dict = {unique_monsters[0]: monster_names.count(unique_monsters[0])}
        # Update monsters table
        populate_monsters_table(table=ui.monsters_tableWidget, monsters=monsters_dict)
        if select_dialog.exec_() == QDialog.Accepted:
            selected_row = ui.monsters_tableWidget.currentRow()
            action = f'Attack #{selected_row + 1}'
            action_column = self.party_table.model().columnCount() - 1
            self.party_table.setItem(self.index, action_column, QTableWidgetItem(action))
            # if selected_row >= 0:
            #     monster_name = ui.monsters_tableWidget.item(selected_row, 0).text()
            #     debug(monster_name)
        self.index += 1
        self.ui.char_actions_groupBox.setTitle(self.party[self.index].name)

    def setup_party_table(self):
        """Setup and populate the party table"""
        game_path = get_save_game_path()
        self.party_table: QTableWidget = self.ui.party_tableWidget

        # Configure table
        populate_table(self.party_table, self.party)
        self.party_table.horizontalHeader().setStretchLastSection(True)
        self.party_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.party_table.setSortingEnabled(True)
        # self.party_table.cellDoubleClicked.connect(self.inspect_char)