from functools import partial
from typing import List, Optional
import os
import sys

from PyQt5.QtCore import pyqtSlot, Qt, QTimer
from PyQt5.QtWidgets import (
    QFrame, QTableWidget, QMainWindow, QWidget,
    QRadioButton, QVBoxLayout, QLabel, QSizePolicy
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
from dnd_5e_core.mechanics import XP_LEVELS

# Import from persistence module
from persistence import load_party, save_character, save_party

# Import from main (project-specific)
from main import rest_character

# Compatibility alias
load_xp_levels = lambda: XP_LEVELS

from populate_rpg_functions import load_potions_collections
from pyQTApp.common import update_buttons, debug
from pyQTApp.qt_designer_widgets.adventurerInn_QFrame import Ui_innFrame
from pyQTApp.qt_designer_widgets.boltac_Trading_Post_QFrame import Ui_boltacFrame
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow

from pyQTApp.qt_common import addItem
from tools.common import get_save_game_path


class Inn_UI(QWidget):
    def __init__(self, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
        self.castle_window = castle_window
        self.castle_ui = castle_ui
        self.innFrame = QFrame()
        self.ui = Ui_innFrame()
        self.ui.setupUi(self.innFrame)
        layout = castle_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.innFrame)
        self.innFrame.setGeometry(castle_ui.castleFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.innFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.leaveInnButton.clicked.connect(self.leave_inn)
        self.castle_window.party_table.selectionModel().selectionChanged.connect(partial(self.select_char))
        self.setup_connections()  # Connect this to radio buttons' toggled signal
        self.ui.healButton.clicked.connect(self.heal_char)

        self.xp_levels = load_xp_levels()
        self.selected_char: Optional[Character] = None

        self.ui.event_scrollArea.hide()
        self.setup_events_area()

    def setup_events_area(self):
        """Initialize the scroll area with a widget and layout"""
        # Create widget to hold content
        self.events_widget = QWidget()
        # Create vertical layout
        self.events_layout = QVBoxLayout(self.events_widget)
        # Add stretch to keep messages at the top
        self.events_layout.addStretch()
        # Set widget as scroll area's widget
        self.ui.event_scrollArea.setWidget(self.events_widget)
        # Enable vertical scrolling
        self.ui.event_scrollArea.setWidgetResizable(True)

    def cprint(self, message: str):
        self.ui.event_scrollArea.show()
        """Print colored message to events area"""
        print(f"Debug: Attempting to print message: {message}")  # Debug line

        # Create label with message
        label = QLabel(message)
        label.setWordWrap(True)

        # Insert label before the stretch
        self.events_layout.insertWidget(self.events_layout.count() - 1, label)

        # Auto scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the scroll area"""
        scrollbar = self.ui.event_scrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def get_selected_room_index(self):
        radios = self.ui.rooms_groupBox.findChildren(QRadioButton)
        return next((i for i, radio in enumerate(radios) if radio.isChecked()), -1)

    @pyqtSlot()
    def heal_char(self):
        fees: List[int] = [0, 10, 100, 200, 500]
        weeks: List[int] = [0, 1, 3, 7, 10]
        room_number: int = self.get_selected_room_index()
        # print(f'{char.name} selected {room} - Fee is {fees[fee_no]} GP / Week!')
        display_msg = rest_character(char=self.selected_char, fee=fees[room_number], weeks=weeks[room_number], xp_levels=self.xp_levels, console_mode=False)
        self.cprint(display_msg)
        game_path = get_save_game_path()
        save_character(char=self.selected_char, _dir=f'{game_path}/characters')
        save_party(party=self.castle_window.party, _dir=game_path)
        self.castle_window.refresh_party_table()

    @pyqtSlot()
    def check_room_selection(self):
        if self.selected_char is None:
            return
        # Check if any radio button in rooms_groupBox is selected
        fees: List[int] = [0, 10, 100, 200, 500]
        for room_number, radio in enumerate(self.ui.rooms_groupBox.findChildren(QRadioButton)):
            if radio.isChecked() and fees[room_number] <= self.selected_char.gold:
                self.ui.healButton.setEnabled(True)
                return
        # If no radio button is selected, keep heal button disabled
        self.ui.healButton.setEnabled(False)

    # Connect this to radio buttons' toggled signal
    def setup_connections(self):
        for radio in self.ui.rooms_groupBox.findChildren(QRadioButton):
            radio.toggled.connect(partial(self.check_room_selection))

    def select_char(self):
        row = self.castle_window.party_table.currentRow()
        if row >= 0:  # Make sure a row is selected
            char_name: str = self.castle_window.party_table.item(row, 0).text()
            self.selected_char: Character = [c for c in self.castle_window.party if c.name == char_name][0]
            self.ui.hello_label.setText(f'Hello, {self.selected_char.name}! Please select a room below:')
            self.check_room_selection()

    @pyqtSlot()  # For button click
    def leave_inn(self):
        self.innFrame.close()
        update_buttons(frame=self.castle_ui.nav_frame, enabled=True)
