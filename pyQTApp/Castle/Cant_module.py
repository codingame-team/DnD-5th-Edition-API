from functools import partial
from typing import List, Optional

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QTableWidget,
    QMainWindow, QWidget,
    QHeaderView,
    QSizePolicy,
)

from dao_classes import Character, Equipment, Potion
from main import load_party, save_character, save_party
from populate_rpg_functions import load_potions_collections
from pyQTApp.common import update_buttons
from pyQTApp.qt_designer_widgets.boltac_Trading_Post_QFrame import Ui_boltacFrame
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow

from pyQTApp.qt_common import addItem
from pyQTApp.qt_designer_widgets.templeOfCant_QFrame import Ui_cantFrame
from tools.common import get_save_game_path


class Cant_UI(QWidget):
    def __init__(self, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
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

    @pyqtSlot()  # For button click
    def leave_cant(self):
        self.cantFrame.close()
        update_buttons(frame=self.castle_ui.nav_frame, enabled=True)
