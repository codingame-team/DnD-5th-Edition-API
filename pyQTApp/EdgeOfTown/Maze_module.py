import os
import sys
from random import choice, randint
from typing import List

from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import (QMainWindow, QLabel, QTableWidget, QHeaderView, QSizePolicy, QToolTip, QFrame)

from dao_classes import Character, Monster
from main import load_party, save_character, save_party
from populate_functions import populate, request_monster

from pyQTApp.qt_designer_widgets.combat_window import Ui_combatWindow
from pyQTApp.qt_designer_widgets.edgeOfTownWindow import Ui_EdgeOfTownWindow
from pyQTApp.qt_designer_widgets.maze_QFrame import Ui_mazeFrame
from pyQTApp.qt_designer_widgets.qt_common import populate_table, populate_monsters_table
from tools.common import get_save_game_path, resource_path


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


# Create a new event filter class with the specific monster name
class ToolTipFilter(QObject):
    def __init__(self, parent, monster_name):
        super().__init__(parent)
        self.monster_name = monster_name

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            QToolTip.showText(QCursor.pos(), self.monster_name, obj)
        return super().eventFilter(obj, event)

class Maze_UI(QMainWindow):
    def __init__(self, edge_of_town_window: QMainWindow, edge_of_town_ui: Ui_EdgeOfTownWindow):
        super().__init__()
        # self.ui = Ui_combatWindow()
        # self.ui.setupUi(self)
        self.mazeFrame = QFrame()
        self.ui = Ui_mazeFrame()
        self.ui.setupUi(self.mazeFrame)
        layout = edge_of_town_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.mazeFrame)
        # layout.addWidget(self.tavernFrame, alignment=Qt.AlignmentFlag.AlignRight)
        self.mazeFrame.setGeometry(edge_of_town_ui.mazeFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.mazeFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ui.fightButton.clicked.connect(self.combat)
        self.ui.fleeButton.clicked.connect(self.display_monsters_groups)

        self.setup_party_table()
        monster_names: List[str] = populate(collection_name="monsters", key_name="results")
        self.monsters: List[Monster] = [request_monster(name) for name in monster_names]
        path = os.path.dirname(__file__)
        self.token_images_dir = resource_path(f'{path}/../../images/monsters/tokens')
        self.display_monsters_groups()

    def combat(self):
        """Start combat"""
        pass



    def setup_party_table(self):
        """Setup and populate the party table"""
        game_path = get_save_game_path()
        self.party: List[Character] = load_party(game_path)
        self.party_table: QTableWidget = self.ui.party_tableWidget
        # Configure table
        populate_table(table=self.party_table, char_list=self.party, in_dungeon=True)
        self.party_table.horizontalHeader().setStretchLastSection(True)
        self.party_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.party_table.setSortingEnabled(True)  # self.party_table.cellDoubleClicked.connect(self.inspect_char)

    def load_monster_token(self, monster: Monster) -> str:
        for filename in os.listdir(self.token_images_dir):
            monster_name, _ = os.path.splitext(filename)
            if monster_name == monster.name:
                return os.path.join(self.token_images_dir, filename)

    def display_monsters_groups(self):
        """Setup the welcome screen with scaled image"""
        monster_1: Monster = choice(self.monsters)
        monster_2: Monster = choice(self.monsters)
        # Populate self.monsters_tableWidget
        monsters_dict: dict = {monster_1.name: randint(1, 10), monster_2.name: randint(1, 10)}
        populate_monsters_table(table=self.ui.monsters_tableWidget, monsters=monsters_dict)
        monster_1_pixmap: QPixmap = QPixmap(self.load_monster_token(monster_1))
        monster_2_pixmap: QPixmap = QPixmap(self.load_monster_token(monster_2))

        # Set label properties
        # self.ui.monster_1_Label.setGeometry(self.ui.monster_1_Frame.rect())
        #self.ui.monster_1_Label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.monster_1_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.ui.monster_2_Label.setGeometry(self.ui.monster_2_Frame.rect())
        #self.ui.monster_2_Label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.monster_2_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a dictionary to map pixmaps to their corresponding labels
        label_map = {monster_1_pixmap: (self.ui.monster_1_Label, monster_1), monster_2_pixmap: (self.ui.monster_2_Label, monster_2)}
        # Scale and set the welcome image
        for pixmap, (label, monster) in label_map.items():
            frame_size = label.size()
            scaled_pixmap = pixmap.scaled(frame_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation, )
            label.setPixmap(scaled_pixmap)
            label.setScaledContents(True)

            # Remove old event filter if it exists
            if hasattr(label, 'tooltip_filter'):
                label.removeEventFilter(label.tooltip_filter)
                label.tooltip_filter.deleteLater()

            # Install the event filter with the specific monster name
            tooltip_filter = ToolTipFilter(label, str(monster))
            label.installEventFilter(tooltip_filter)

            # Store the filter as an attribute of the label to prevent garbage collection
            label.tooltip_filter = tooltip_filter

            # Enable mouse tracking
            label.setMouseTracking(True)