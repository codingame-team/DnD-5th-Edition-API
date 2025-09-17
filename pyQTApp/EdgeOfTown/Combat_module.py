import os
import sys
from fractions import Fraction
from functools import partial
from random import randint, choice, sample
from typing import List, Optional

from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QCursor, QColor
from PyQt5.QtWidgets import (QMainWindow, QTableWidget, QHeaderView, QSizePolicy, QToolTip, QFrame, QDialog, QTableWidgetItem, QLabel, QWidget, QVBoxLayout, QPushButton, )

from dao_classes import Character, Monster, CharAction, ActionType, CharActionType, Spell, SpecialAbility, RangeType, Action
from main import (load_party, generate_encounter_levels, generate_encounter, load_encounter_table, load_encounter_gold_table, )
from populate_functions import populate, request_monster
from pyQTApp.common import color
from pyQTApp.qt_designer_widgets.combat_QFrame import Ui_combatFrame
from pyQTApp.qt_designer_widgets.combat_select_Dialog import Ui_combatSelectDialog

from pyQTApp.qt_designer_widgets.edgeOfTownWindow import Ui_EdgeOfTownWindow
from pyQTApp.qt_common import populate_table, populate_monsters_table
from pyQTApp.qt_designer_widgets.monsters_select_Dialog import Ui_monsters_select_Dialog
from pyQTApp.qt_designer_widgets.party_select_Dialog import Ui_party_select_Dialog
from pyQTApp.qt_designer_widgets.spell_select_Dialog import Ui_spells_select_Dialog
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


class Combat_UI(QMainWindow):
    def __init__(self, edge_of_town_window: QMainWindow, edge_of_town_ui: Ui_EdgeOfTownWindow):
        super().__init__()
        # self.ui = Ui_combatWindow()
        # self.ui.setupUi(self)
        self.combatFrame = QFrame()
        self.ui = Ui_combatFrame()
        self.ui.setupUi(self.combatFrame)
        layout = edge_of_town_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.combatFrame)
        # layout.addWidget(self.tavernFrame, alignment=Qt.AlignmentFlag.AlignRight)
        self.combatFrame.setGeometry(edge_of_town_ui.mazeFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.combatFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ui.combatButton.clicked.connect(self.combat)
        self.ui.fleeButton.clicked.connect(self.flee)
        self.ui.castleButton.clicked.connect(edge_of_town_window.return_to_castle)

        game_path = get_save_game_path()
        self.party: List[Character] = load_party(game_path)
        self.refresh_party_table()
        monster_names: List[str] = populate(collection_name="monsters", key_name="results")
        self.monsters_db: List[Monster] = [request_monster(name) for name in monster_names]
        path = os.path.dirname(__file__)
        self.token_images_dir = resource_path(f"{path}/../../images/monsters/tokens")
        self.monsters = self.load_monsters()
        self.display_monsters_groups()
        self.ui.char_actions_groupBox.setVisible(True)
        self.ui.fightButton.clicked.connect(partial(self.select_monsters, action_type=CharActionType.MELEE_ATTACK))
        self.ui.castButton.clicked.connect(self.cast_spell)
        self.ui.parryButton.clicked.connect(self.parry)
        self.party_table.itemSelectionChanged.connect(self.on_party_row_selected)
        self.index = 0
        self.actions: List[Optional[CharAction]] = [None] * len(self.party)
        self.action_column = self.party_table.model().columnCount() - 1
        self.party_table.setCurrentCell(self.index, self.action_column)
        self.setup_events_area()
        self.round_num = 0
        # self.exec()

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
        """Print colored message to events area"""

        # Create label with message
        label = QLabel(message)
        label.setWordWrap(True)

        # Insert label before the stretch
        self.events_layout.insertWidget(self.events_layout.count() - 1, label)

        # Auto scroll to bottom
        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the scroll area"""
        scrollbar = self.ui.event_scrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @pyqtSlot()
    def combat(self):
        if any([action is None for i, action in enumerate(self.actions) if not self.party[i].is_dead]):
            debug("Not all actions are selected")
            return
        debug(f"actions {self.actions}")
        attack_queue = [(c, randint(1, c.abilities.dex)) for c in self.party] + [(m, randint(1, m.abilities.dex)) for m in self.monsters]
        attack_queue.sort(key=lambda x: x[1], reverse=True)
        attackers = [c for c, init_roll in attack_queue]
        alive_monsters: List[Monster] = [c for c in self.monsters if c.hit_points > 0]
        alive_chars: List[Character] = [c for c in self.party if c.hit_points > 0]
        # Start of Round
        queue = [c for c in attackers if c.hit_points > 0]
        while queue:
            attacker = queue.pop()
            if attacker.hit_points > 0:
                if isinstance(attacker, Monster):
                    # check if monster can heal someone
                    healing_spells: List[Spell] = []
                    if attacker.is_spell_caster:
                        healing_spells: List[Spell] = [s for s in attacker.sc.learned_spells if s.heal_at_slot_level and attacker.sc.spell_slots[s.level - 1] > 0]
                        # cprint(f"{color.GREEN}{attacker.name}{color.END} has {len(healing_spells)} healing spells available!")
                    if any(c for c in alive_monsters if c.hit_points < 0.5 * c.max_hit_points) and healing_spells:
                        # spell = max(healing_spells, key=lambda s: s.level) # choose strongest spell (to be refined)
                        max_spell_level: int = max([s.level for s in healing_spells])
                        spell = choice([s for s in healing_spells if s.level == max_spell_level])
                        monster: Monster = min(alive_monsters, key=lambda c: c.hit_points)  # consider weakest char for optimal healing
                        if spell.range == 5:
                            attacker.cast_heal(spell, spell.level - 1, [monster])
                            self.cprint(f"{color.GREEN}{attacker.name}{color.END} heals {monster.name}")
                        else:
                            attacker.cast_heal(spell, spell.level - 1, alive_monsters)
                            self.cprint(f"{color.GREEN}{attacker.name}{color.END} heals all monsters")
                        if not spell.is_cantrip:
                            attacker.sc.spell_slots[spell.level - 1] -= 1
                    else:
                        # Monster attacks randomly
                        melee_chars: List[Character] = [c for i, c in enumerate(alive_chars) if i < 3]
                        ranged_chars: List[Character] = [c for i, c in enumerate(alive_chars) if i >= 3]
                        if not melee_chars + ranged_chars:
                            break
                        # Precalculate ready spells & special attacks
                        if attacker.is_spell_caster:
                            cantric_spells: List[Spell] = [s for s in attacker.sc.learned_spells if not s.level and s.damage_type]
                            slot_spells: List[Spell] = [s for s in attacker.sc.learned_spells if s.level and attacker.sc.spell_slots[s.level - 1] > 0 and s.damage_type]
                            castable_spells: List[Spell] = cantric_spells + slot_spells
                        if attacker.sa and self.round_num > 0:  # ou 1? (à vérifier)
                            for special_attack in attacker.sa:
                                if special_attack.recharge_on_roll:
                                    special_attack.ready = special_attack.recharge_success
                        available_special_attacks: List[SpecialAbility] = list(filter(lambda a: a.ready, attacker.sa))
                        # Main loop
                        if attacker.is_spell_caster and castable_spells:
                            target_char: Character = (choice(ranged_chars) if ranged_chars else choice(melee_chars))
                            attack_spell: Spell = max(castable_spells, key=lambda s: s.level)
                            target_char.hit_points -= attacker.cast_attack(target_char, attack_spell)
                            self.cprint(f"{color.GREEN}{attacker.name}{color.END} attacks {target_char.name} with ** {attack_spell.name.upper()} **")
                            if target_char.hit_points <= 0:
                                alive_chars.remove(target_char)
                                target_char.status = "DEAD"
                                self.cprint(f"{target_char.name} is ** KILLED **!")
                        elif available_special_attacks:
                            special_attack: SpecialAbility = max(available_special_attacks, key=lambda a: sum([damage.dd.score(success_type=a.dc_success) for damage in a.damages]), )
                            # cprint(special_attack)
                            if special_attack.targets_count >= len(self.party):
                                self.cprint(f"{color.GREEN}{attacker.name}{color.END} launches ** {special_attack.name.upper()} ** on whole party!")
                                target_chars: List[Character] = self.party
                            else:
                                if special_attack.range == RangeType.MELEE:
                                    target_chars: List[Character] = sample(melee_chars, special_attack.targets_count)
                                elif special_attack.range == RangeType.RANGED:
                                    target_chars: List[Character] = sample(ranged_chars, special_attack.targets_count)
                                else:
                                    target_chars: List[Character] = sample(self.party, special_attack.targets_count)
                                targets: str = ", ".join([char.name for char in target_chars])
                                # Replace all ' and ' with ', ' except for the last one
                                targets_split = targets.rsplit(", ", 1)  # Split at the last ', '
                                formatted_targets = " and ".join(targets_split)
                                self.cprint(f"{color.GREEN}{attacker.name}{color.END} launches ** {special_attack.name.upper()} ** on {formatted_targets}!")
                            # cprint('target chars: ' + '/'.join([c.name for c in target_chars]))
                            for target_char in target_chars:
                                if target_char in alive_chars:
                                    target_char.hit_points -= attacker.special_attack(target_char, special_attack)
                                    if target_char.hit_points <= 0:
                                        # cprint('/'.join([c.name for c in alive_chars]))
                                        # cprint(f'removing {char.name}')
                                        alive_chars.remove(target_char)
                                        target_char.status = "DEAD"
                                        self.cprint(f"{target_char.name} is ** KILLED **!")
                        else:
                            target_char: Character = choice(melee_chars)
                            melee_attacks: List[Action] = [a for a in attacker.actions if a.type in (ActionType.MELEE, ActionType.MIXED)] if attacker.actions else []
                            if melee_attacks:
                                target_char.hit_points -= attacker.attack(character=target_char, actions=melee_attacks)
                                self.cprint(f"{color.GREEN}{attacker.name}{color.END} attacks {target_char.name}")
                                if target_char.hit_points <= 0:
                                    alive_chars.remove(target_char)
                                    target_char.status = "DEAD"
                                    self.cprint(f"{target_char.name} is ** KILLED **!")
                            else:
                                self.cprint(f"** {attacker.name} ** has no MELEE attacks implemented!")
                else: # CHARACTER Attacks
                    attacker_index: int = self.party.index(attacker)
                    action = self.actions[attacker_index]
                    if action.type == CharActionType.PARRY:
                        self.cprint(f"{color.GREEN}{attacker.name}{color.END} parries!")
                        continue
                    monsters = list(filter(lambda m: m.hit_points > 0, action.targets))
                    if not monsters:
                        continue
                    monster: Monster = min(monsters, key=lambda m: m.hit_points)
                    if action.type == CharActionType.MELEE_ATTACK:
                        monster.hit_points -= attacker.attack(monster=monster)
                        self.cprint(f"{color.GREEN}{attacker.name}{color.END} attacks {monster.name.title()}!")
                        monster.hit_points -= attacker.attack(monster=monster, in_melee=(attacker in alive_chars[:3]))
                    elif action.type == CharActionType.SPELL_ATTACK:
                        monster: Monster = min(alive_monsters, key=lambda m: m.hit_points)
                        monster.hit_points -= attacker.cast_attack(action.spell, monster)
                        if not action.spell.is_cantrip:
                            attacker.update_spell_slots(spell=action.spell)
                        self.cprint(f"{color.GREEN}{attacker.name}{color.END} casts {action.spell.name} on {monster.name.title()}!")
                    elif action.type == CharActionType.SPELL_DEFENSE:
                        for char in action.targets:
                            best_slot_level: int = attacker.get_best_slot_level(heal_spell=action.spell, target=char)
                            if action.spell.range == 5:
                                attacker.cast_heal(action.spell, best_slot_level, [char])
                                self.cprint(f"{color.GREEN}{attacker.name}{color.END} casts {action.spell.name} on {char.name}!")
                            else:
                                attacker.cast_heal(action.spell, best_slot_level, self.party)
                                self.cprint(f"{color.GREEN}{attacker.name}{color.END} casts {action.spell.name} on PARTY!")
                        if not action.spell.is_cantrip:
                            attacker.update_spell_slots(action.spell, best_slot_level)
                    if monster.hit_points <= 0:
                        alive_monsters.remove(monster)
                        self.cprint(f"{color.RED}{monster.name.title()}{color.END} is ** KILLED **!")
                        attacker.victory(monster)
                        # attacker.treasure(weapons, armors, equipments, potions)
                        if not hasattr(attacker, "kills"): attacker.kills = []
                        attacker.kills.append(monster)
        self.round_num += 1

        # End of Round
        alive_chars: List[Character] = [c for c in self.party if c.hit_points > 0]
        alive_monsters: List[Monster] = [c for c in self.monsters if c.hit_points > 0]

        if not alive_chars:
            for target_char in self.party:
                target_char.conditions.clear()
            self.cprint(f"** DEFEAT! ALL PARTY HAS BEEN KILLED **")
            self.ui.party_action_groupBox.setVisible(False)
            self.ui.char_actions_groupBox.setVisible(False)
        elif not alive_monsters:
            self.cprint(f"** VICTORY! **")
            party_level: int = round(sum([c.level for c in self.party]) / len(self.party))
            encounter_gold_table: List[int] = load_encounter_gold_table()
            earned_gold: int = encounter_gold_table[party_level - 1]
            xp_gained: int = sum([m.xp for m in self.monsters])
            for target_char in alive_chars:
                target_char.gold += earned_gold // len(self.party)
                target_char.xp += xp_gained // len(alive_chars)
                target_char.conditions.clear()
            self.cprint(f"Party has earned {earned_gold} GP and gained {xp_gained} XP!")
            self.monsters = self.load_monsters()
            self.cprint(f"** New encounter **")

        self.refresh_party_table()
        # populate_table(table=self.party_table, char_list=self.party, in_dungeon=True, sorting=False)
        self.display_monsters_groups()

    def unselect_dead_chars(self):
        # Make party table row not selectable if char is dead
        for row, char in enumerate(self.party):
            for col in range(self.party_table.columnCount()):
                item = self.party_table.item(row, col)
                if item:
                    if char.hit_points <= 0:
                        # Remove selectable flag but keep item visible and enabled
                        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                    else:
                        # Restore normal flags (selectable, enabled, editable if it was)
                        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    @pyqtSlot()
    def flee(self):
        self.cprint(f"** Party successfully escaped! **")
        for row in range(self.party_table.rowCount()):
            self.update_cell(content='', row=row, col=self.action_column)
        self.monsters = self.load_monsters()
        self.display_monsters_groups()
        self.actions = [None] * len(self.party)
        self.round_num = 0

    # Add this method to handle row selection
    @pyqtSlot()
    def on_party_row_selected(self):
        """Update index when party member is selected"""
        self.index = self.party_table.currentRow()
        char: Character = self.party[self.index]
        if char.hit_points <= 0:
            debug(f"{char.name} is dead!")
            # Disable all buttons in char_actions_groupBox
            for button in self.ui.char_actions_groupBox.findChildren(QPushButton):
                button.setEnabled(False)
        else:
            # Enable all buttons in char_actions_groupBox
            for button in self.ui.char_actions_groupBox.findChildren(QPushButton):
                button.setEnabled(True)
        if self.index >= 0:  # Make sure a valid row is selected
            self.ui.char_actions_groupBox.show()
            title: str = f"{char.name}'s Options"
            self.ui.char_actions_groupBox.setTitle(title)
            if char.is_spell_caster:
                self.ui.castButton.show()
            else:
                self.ui.castButton.hide()

    def move_to_next_row(self):
        """Move cursor to the same column in the next row, skipping dead characters"""
        current_row = self.index
        while True:
            next_row = (current_row + 1) % len(self.party)
            if self.party[next_row].hit_points > 0:
                # Found a living character, move to their row
                self.party_table.setCurrentCell(next_row, self.action_column)
                self.index = next_row
                break
            current_row = next_row
            # If we've checked all rows and come back to start, break to prevent infinite loop
            if current_row == self.index:
                break

    @pyqtSlot()
    def parry(self):
        self.actions[self.index] = CharAction(type=CharActionType.PARRY)
        self.update_cell(content='PARRY', row=self.index, col=self.action_column)

    @pyqtSlot()
    def cast_spell(self):
        spell_dialog = QDialog(self)
        ui = Ui_spells_select_Dialog()
        ui.setupUi(spell_dialog)
        char: Character = self.party[self.index]
        spells = char.sc.learned_spells

        # Group spells by level
        spells_by_level = {i: [] for i in range(10)}  # Initialize dict for levels 0-9
        for spell in spells:
            if char.can_cast(spell):
                spells_by_level[spell.level].append(spell)

        # Store comboboxes for easier access
        combo_boxes = []

        # Populate comboboxes for each level
        for level in range(10):
            combo_box = getattr(ui, f'comboBox_{level}', None)
            if not spells_by_level[level]:
                frame = getattr(ui, f'frame_{level}', None)
                frame.hide()  # Hide empty comboboxes's frame
                continue
            if combo_box is not None:
                combo_boxes.append(combo_box)
                combo_box.clear()
                combo_box.addItem("")
                for spell in spells_by_level[level]:
                    combo_box.addItem(spell.name, spell)

                # Connect the currentIndexChanged signal
                combo_box.currentIndexChanged.connect(lambda idx, current_box=combo_box: self.on_spell_selected(current_box, combo_boxes))

        # Adjust dialog size after hiding frames
        spell_dialog.adjustSize()

        if spell_dialog.exec_():
            # Get the selected spell from any of the comboboxes
            for level in range(10):
                spell = self.get_selected_spell(ui, level)
                if spell:
                    debug(spell)
                    if not hasattr(spell, 'heal_at_slot_level') or not spell.heal_at_slot_level:
                        # debug(f"spell {spell.name} is not a healing spell")
                        self.select_monsters(action_type=CharActionType.SPELL_ATTACK, spell=spell)
                    else:
                        # debug(f"spell {spell.name} is a healing spell")
                        targets: List[Character] = self.select_characters() if spell.range == 5 else self.party
                        self.actions[self.index] = CharAction(type=CharActionType.SPELL_DEFENSE, targets=targets, spell=spell)
                        if spell.range > 5:
                            action: str = f"{spell.name} PARTY"
                        else:
                            targets: str = '|'.join([c.name for c in targets])
                            action = f"{spell.name} {targets}"
                        self.update_cell(content=action, row=self.index, col=self.action_column)
                    break

    def on_spell_selected(self, current_box, all_boxes):
        """Clear other comboboxes when one is selected"""
        if current_box.currentIndex() > 0:  # If an actual spell is selected
            for box in all_boxes:
                if box != current_box:
                    box.setCurrentIndex(0)  # Reset to empty option

    # Get selected spell from a specific combobox
    def get_selected_spell(self, ui, level):
        combo_box = getattr(ui, f'comboBox_{level}', None)
        if combo_box and combo_box.currentIndex() > 0:  # Skip empty option
            return combo_box.currentData()  # Returns the spell object
        return None

    def select_characters(self) -> List[Character]:
        """Select characters for spell defense"""
        select_dialog = QDialog(self)
        ui = Ui_party_select_Dialog()
        ui.setupUi(select_dialog)
        populate_table(table=ui.party_tableWidget, char_list=self.party, in_dungeon=True)
        if select_dialog.exec_():
            selected_row = ui.party_tableWidget.currentRow()
            return [self.party[selected_row]]

    @pyqtSlot()
    def select_monsters(self, action_type: CharActionType, spell: Optional[Spell] = None):
        """Select monsters for combat"""
        if len(self.monsters_dict) == 1:
            attack_type: str = action_type.value if action_type == CharActionType.MELEE_ATTACK else spell.name
            action = f"{attack_type} #1"
            targets = self.monsters
        else:
            select_dialog = QDialog(self)
            ui = Ui_monsters_select_Dialog()
            ui.setupUi(select_dialog)
            # Update monsters table
            populate_monsters_table(table=ui.monsters_tableWidget, monsters=self.monsters_dict)
            if select_dialog.exec_():
                selected_row = ui.monsters_tableWidget.currentRow()
                selected_monsters_name = ui.monsters_tableWidget.item(selected_row, 0).text().strip()
                content: str = f"{selected_monsters_name} #{selected_row + 1}"
                # debug(f"selected monster's group: {content}")
                attack_type: str = action_type.value if action_type == CharActionType.MELEE_ATTACK else spell.name
                action = f"{attack_type} #{selected_row + 1}"
                self.ui.char_actions_groupBox.setTitle(self.party[self.index].name)
                targets = [m for m in self.monsters if m.name == selected_monsters_name]
                # debug(f"targets: {targets}")
            else:
                return
        self.actions[self.index] = CharAction(type=action_type, targets=targets, spell=spell)
        self.update_cell(content=action, row=self.index, col=self.action_column)

    def update_cell(self, content: str, row: int, col: int):
        """Update the action column in the party table"""
        self.party_table.setItem(row, col, QTableWidgetItem(content))
        self.party_table.resizeColumnToContents(col)
        self.move_to_next_row()

    def refresh_party_table(self):
        """Setup and populate the party table"""
        # Sort party list - living characters first, dead characters last
        self.party.sort(key=lambda char: char.hit_points <= 0)

        self.party_table: QTableWidget = self.ui.party_tableWidget
        # Configure table
        populate_table(table=self.party_table, char_list=self.party, in_dungeon=True, sorting=False)
        self.party_table.horizontalHeader().setStretchLastSection(True)
        self.party_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.party_table.cellDoubleClicked.connect(self.inspect_char)

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
        monsters: List[Monster] = generate_encounter(
            available_crs=available_crs,
            encounter_table=encounter_table,
            encounter_level=encounter_level,
            monsters=self.monsters_db,
            monster_groups_count=monster_groups_count,
        )
        for m in monsters:
            m.hp_roll()
        return monsters

    def display_monsters_groups(self):
        # Get unique monsters and their counts
        monster_names = [m.name for m in self.monsters if m.hit_points > 0]
        if not monster_names:
            return
        unique_monsters = list(set(monster_names))
        self.monsters_dict = {unique_monsters[0]: monster_names.count(unique_monsters[0])}

        # Setup first monster
        monster_1_pixmap = QPixmap(self.load_monster_token(unique_monsters[0]))
        self.ui.monster_1_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_map = {monster_1_pixmap: (self.ui.monster_1_Label, unique_monsters[0])}

        # Setup second monster if exists, otherwise clear it
        if len(unique_monsters) == 2:
            self.monsters_dict[unique_monsters[1]] = monster_names.count(unique_monsters[1])
            monster_2_pixmap = QPixmap(self.load_monster_token(unique_monsters[1]))
            self.ui.monster_2_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.monster_2_Label.setVisible(True)
            label_map[monster_2_pixmap] = (self.ui.monster_2_Label, unique_monsters[1])
        else:
            self.ui.monster_2_Label.clear()
            self.ui.monster_2_Label.setVisible(False)

        # Update monsters table
        populate_monsters_table(table=self.ui.monsters_tableWidget, monsters=self.monsters_dict)

        # Update labels with pixmaps and tooltips
        for pixmap, (label, monster) in label_map.items():
            # Scale and set pixmap
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            label.setPixmap(scaled_pixmap)
            label.setScaledContents(True)

            # Update tooltip
            if hasattr(label, "tooltip_filter"):
                label.removeEventFilter(label.tooltip_filter)
                label.tooltip_filter.deleteLater()

            tooltip_filter = ToolTipFilter(label, str(monster))
            label.installEventFilter(tooltip_filter)
            label.tooltip_filter = tooltip_filter
            label.setMouseTracking(True)
