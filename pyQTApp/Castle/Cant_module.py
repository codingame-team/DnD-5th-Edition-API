from functools import partial
from functools import partial
from typing import List, Optional
import os
import sys

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QTableWidget,
    QMainWindow, QWidget,
    QHeaderView,
    QSizePolicy,
)

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
	sys.path.insert(0, _dnd_5e_core_path)

from dnd_5e_core.entities import Character
from dnd_5e_core.equipment import Equipment, Potion

# Import from persistence module
from persistence import load_party, save_character, save_party, get_roster

from populate_rpg_functions import load_potions_collections
from pyQTApp.common import update_buttons
from pyQTApp.qt_designer_widgets.boltac_Trading_Post_QFrame import Ui_boltacFrame
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow

from pyQTApp.qt_common import addItem, populate_table, populate_cant_table
from pyQTApp.qt_designer_widgets.templeOfCant_QFrame import Ui_cantFrame
from tools.common import get_save_game_path


class Cant_UI(QWidget):
    def __init__(self, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
        self.castle_window = castle_window
        self.castle_ui = castle_ui
        self.cantFrame = QFrame()
        self.ui = Ui_cantFrame()
        self.ui.setupUi(self.cantFrame)
        layout = castle_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.cantFrame)
        self.cantFrame.setGeometry(castle_ui.castleFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.cantFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ui.leaveCantButton.clicked.connect(self.leave_cant)
        self.castle_window.party_table.selectionModel().selectionChanged.connect(partial(self.select_char))
        # self.setup_connections()  # Connect this to radio buttons' toggled signal
        self.ui.saveButton.clicked.connect(self.save_char)

        self.setup_cant_table()

    def select_char(self):
        row = self.castle_window.party_table.currentRow()
        cant_row = self.cant_table.currentRow()
        if row >= 0 and cant_row >= 0:  # Make sure a row is selected
            char_to_contribute_name: str = self.castle_window.party_table.item(row, 0).text()
            char_to_contribute: Character = [c for c in self.castle_window.party if c.name == char_to_contribute_name][0]
            char_to_save_name: str = self.cant_table.item(cant_row, 0).text()
            char_to_save: Character = [c for c in self.cant_roster if c.name == char_to_save_name][0]
            # self.check_room_selection()
            cures_costs_per_level = {"PARALYZED": 100, "STONED": 200, "DEAD": 250, "ASHES": 500, "LOST": 10000}
            if char_to_contribute.gold < cures_costs_per_level[char_to_save.status] * char_to_save.level:
                self.ui.char_to_pay_label.setText("Go away! You don't have enough of money!")
                print("Go away! You don't have enough of money!")
            else:
                self.ui.char_to_pay_label.setText(f'Greetings, {char_to_contribute.name}!')
                self.ui.saveButton.setEnabled(True)

    def setup_cant_table(self):
        """Setup and populate the party table"""
        game_path = get_save_game_path()
        self.cant_roster: List[Character] = [c for c in get_roster(characters_dir=f"{game_path}/characters") if c.status != 'OK']
        self.cant_table: QTableWidget = self.ui.injured_char_table
        self.refresh_cant_table()

    def refresh_cant_table(self):
        # Configure table
        populate_cant_table(self.cant_table, self.cant_roster)
        self.cant_table.horizontalHeader().setStretchLastSection(True)
        self.cant_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cant_table.setSortingEnabled(True)
        # self.party_table.cellDoubleClicked.connect(self.inspect_char)

    @pyqtSlot()  # For button click
    def save_char(self):
        row = self.cant_table.currentRow()
        if row >= 0:  # Make sure a row is selected
            char_name: str = self.cant_table.item(row, 0).text()
            char: Character = [c for c in self.cant_roster if c.name == char_name][0]
            if char.status == "DEAD":
                success: bool = randint(1, 100) < 50 + 3 * char.constitution
                if success:
                    char.status = "OK"
                    char.hit_points = 1
                    char.age += randint(1, 52)
                    print(f"{char.name} ** LIVES! ***")
                    self.cant_roster.remove(char)
                else:
                    char.status = "ASHES"
                    print(f"{char.name} converts to ** ASHES! ***")
            elif char.status == "ASHES":
                success: bool = randint(1, 100) < 40 + 3 * char.constitution
                if success:
                    char.status = "OK"
                    char.hit_points = char.max_hit_points
                    char.age += randint(1, 52)
                    print(f"{char.name} ** LIVES! ***")
                else:
                    char.status = "LOST"
                    print(f"{char.name} is ** LOST! ***")
                self.cant_roster.remove(char)
            else:
                char.status = "OK"
                char.hit_points = char.max_hit_points
                char.age += randint(1, 52)
                print(f"{char.name} ** LIVES! ***")
                self.cant_roster.remove(char)
            game_path = get_save_game_path()
            save_character(char=char, _dir=f'{game_path}/characters')
            self.refresh_cant_table()

    @pyqtSlot()  # For button click
    def leave_cant(self):
        self.cantFrame.close()
        update_buttons(frame=self.castle_ui.nav_frame, enabled=True)
