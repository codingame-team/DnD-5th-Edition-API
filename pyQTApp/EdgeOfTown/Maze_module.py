import os
import sys
from fractions import Fraction
from random import choice, randint
from typing import List

from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import (QMainWindow, QLabel, QTableWidget, QHeaderView, QSizePolicy, QToolTip, QFrame)

from dao_classes import Character, Monster
from main import load_party, save_character, save_party, generate_encounter_levels, generate_encounter, load_encounter_table
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
		self.monsters_db: List[Monster] = [request_monster(name) for name in monster_names]
		path = os.path.dirname(__file__)
		self.token_images_dir = resource_path(f'{path}/../../images/monsters/tokens')
		self.display_monsters_groups()

	def combat(self):
		"""Start combat"""
		self.ui.char_actions_groupBox.setEnabled(True)

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

	def load_monster_token(self, name: str) -> str:
		for filename in os.listdir(self.token_images_dir):
			monster_name, _ = os.path.splitext(filename)
			if monster_name == name:
				return os.path.join(self.token_images_dir, filename)

	def load_monsters(self) -> List[Monster]:
		party_level: int = round(sum([c.level for c in self.party]) / len(self.party))
		encounter_table: dict() = load_encounter_table()
		available_crs: List[Fraction] = [Fraction(str(m.challenge_rating)) for m in self.monsters_db]
		encounter_levels: List[int] = generate_encounter_levels(party_level=party_level)
		monster_groups_count: int = randint(1, 2)
		if not encounter_levels:
			encounter_levels: List[int] = generate_encounter_levels(party_level=party_level)
		encounter_level: int = encounter_levels.pop()
		monsters: List[Monster] = generate_encounter(available_crs=available_crs, encounter_table=encounter_table, encounter_level=encounter_level, monsters=self.monsters_db, monster_groups_count=monster_groups_count)
		return monsters


	def display_monsters_groups(self):
		# Get unique monsters and their counts
		monsters = self.load_monsters()
		monster_names = [m.name for m in monsters]
		unique_monsters = list(set(monster_names))
		monsters_dict = {unique_monsters[0]: monster_names.count(unique_monsters[0])}

		# Setup first monster
		monster_1_pixmap = QPixmap(self.load_monster_token(unique_monsters[0]))
		self.ui.monster_1_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		label_map = {monster_1_pixmap: (self.ui.monster_1_Label, unique_monsters[0])}

		# Setup second monster if exists, otherwise clear it
		if len(unique_monsters) == 2:
			monsters_dict[unique_monsters[1]] = monster_names.count(unique_monsters[1])
			monster_2_pixmap = QPixmap(self.load_monster_token(unique_monsters[1]))
			self.ui.monster_2_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
			self.ui.monster_2_Label.setVisible(True)
			label_map[monster_2_pixmap] = (self.ui.monster_2_Label, unique_monsters[1])
		else:
			self.ui.monster_2_Label.clear()
			self.ui.monster_2_Label.setVisible(False)

		# Update monsters table
		populate_monsters_table(table=self.ui.monsters_tableWidget, monsters=monsters_dict)

		# Update labels with pixmaps and tooltips
		for pixmap, (label, monster) in label_map.items():
			# Scale and set pixmap
			scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
			label.setPixmap(scaled_pixmap)
			label.setScaledContents(True)

			# Update tooltip
			if hasattr(label, 'tooltip_filter'):
				label.removeEventFilter(label.tooltip_filter)
				label.tooltip_filter.deleteLater()

			tooltip_filter = ToolTipFilter(label, str(monster))
			label.installEventFilter(tooltip_filter)
			label.tooltip_filter = tooltip_filter
			label.setMouseTracking(True)
