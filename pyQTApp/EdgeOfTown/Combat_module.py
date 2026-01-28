import os
import sys
from fractions import Fraction
from functools import partial
from random import randint, choice, sample
from typing import List, Optional

from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSlot, QTimer, QRectF
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QHeaderView,
    QSizePolicy,
    QToolTip,
    QFrame,
    QDialog,
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidgetItem,
)

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
	sys.path.insert(0, _dnd_5e_core_path)

from dnd_5e_core.entities import Character, Monster
from dnd_5e_core.combat import Action, ActionType, SpecialAbility, RangeType
from dnd_5e_core.spells import Spell
from dnd_5e_core.classes import Proficiency

# UI-specific combat models (not in dnd-5e-core)
from pyQTApp.combat_models import CharAction, CharActionType

# Import from persistence module
from persistence import load_party

# Import D&D 5e rules from package
from dnd_5e_core.mechanics import (
    generate_encounter_distribution,
    ENCOUNTER_TABLE,
    ENCOUNTER_GOLD_TABLE,
)
from dnd_5e_core.mechanics.encounter_builder import select_monsters_by_encounter_table

# Compatibility aliases
generate_encounter_levels = generate_encounter_distribution
load_encounter_table = lambda: ENCOUNTER_TABLE
load_encounter_gold_table = lambda: ENCOUNTER_GOLD_TABLE
generate_encounter = select_monsters_by_encounter_table

from populate_functions import populate, request_monster
from pyQTApp.common import color
from pyQTApp.qt_designer_widgets.combat_QFrame import Ui_combatFrame
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
        self.party: List[Character] = load_party(_dir=game_path)

        # Initialize party_table reference early
        self.party_table: QTableWidget = self.ui.party_tableWidget
        self.index = 0

        monster_names: List[str] = populate(collection_name="monsters", key_name="results")
        self.monsters_db: List[Monster] = [request_monster(name) for name in monster_names]
        path = os.path.dirname(__file__)
        self.token_images_dir = resource_path(f"{path}/../../images/monsters/tokens")
        self.monsters = self.load_monsters()
        self.display_monsters_groups()
        self.ui.char_actions_groupBox.setVisible(True)

        # Connect fight button to prepare_action so user can click a token to pick the group
        self.ui.fightButton.clicked.connect(lambda: self.prepare_action(CharActionType.MELEE_ATTACK))
        self.ui.castButton.clicked.connect(self.cast_spell)
        self.ui.parryButton.clicked.connect(self.parry)
        # Add use item button if it exists in UI, otherwise add it dynamically
        if hasattr(self.ui, 'useItemButton'):
            self.ui.useItemButton.clicked.connect(self.use_item)

        self.actions: List[Optional[CharAction]] = [None] * len(self.party)
        self.setup_events_area()
        self.round_num = 0
        # Pending action holds a tuple (action_type, spell) when user pressed an action button and awaits target click
        self.pending_action = None

        # Now refresh party table and connect signals after initialization
        self.refresh_party_table()

        # Connect party table signals after refresh
        self.party_table.itemSelectionChanged.connect(self.on_party_row_selected)
        self.action_column = self.party_table.model().columnCount() - 1
        self.party_table.setCurrentCell(self.index, self.action_column)

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
        import re

        # Remove ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_message = ansi_escape.sub('', message)

        # Create label with message
        label = QLabel(clean_message)
        label.setWordWrap(True)

        # Insert label before the stretch
        self.events_layout.insertWidget(self.events_layout.count() - 1, label)

        # Auto scroll to bottom
        QTimer.singleShot(0, self.scroll_to_bottom)

        # Also print to console for debugging
        debug(clean_message)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the scroll area"""
        scrollbar = self.ui.event_scrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @pyqtSlot()
    def combat(self):
        if any([action is None for i, action in enumerate(self.actions) if self.party[i].hit_points > 0]):
            debug("Not all actions are selected")
            self.cprint("⚠️ Please select an action for all living party members!")
            return
        debug(f"actions {self.actions}")
        self.cprint(f"=== ROUND {self.round_num + 1} ===")
        attack_queue = [(c, randint(1, c.abilities.dex)) for c in self.party] + [(m, randint(1, m.abilities.dex)) for m in self.monsters]
        attack_queue.sort(key=lambda x: x[1], reverse=True)
        attackers = [c for c, init_roll in attack_queue]
        alive_monsters: List[Monster] = [c for c in self.monsters if c.hit_points > 0]
        alive_chars: List[Character] = [c for c in self.party if c.hit_points > 0]
        debug(f"Queue size: {len(attackers)}, Alive monsters: {len(alive_monsters)}, Alive chars: {len(alive_chars)}")
        # Start of Round
        queue = [c for c in attackers if c.hit_points > 0]
        debug(f"Starting combat loop with {len(queue)} attackers in queue")
        while queue:
            try:
                attacker = queue.pop()
                debug(f"Processing attacker: {attacker.name if hasattr(attacker, 'name') else 'Unknown'} (HP: {attacker.hit_points})")
                if attacker.hit_points > 0:
                    debug(f"  → Attacker is alive, checking type...")
                    if isinstance(attacker, Monster):
                        debug(f"  → {attacker.name} is a Monster")
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
                            # Precompute castable spells safely
                            castable_spells: List[Spell] = []
                            if attacker.is_spell_caster:
                                cantric_spells: List[Spell] = [s for s in attacker.sc.learned_spells if not s.level and s.damage_type]
                                slot_spells: List[Spell] = [
                                    s
                                    for s in attacker.sc.learned_spells
                                    if s.level and attacker.sc.spell_slots[s.level - 1] > 0 and s.damage_type
                                ]
                                castable_spells = cantric_spells + slot_spells
                            if attacker.sa and self.round_num > 0:  # ou 1? (à vérifier)
                                for special_attack in attacker.sa:
                                    if special_attack.recharge_on_roll:
                                        special_attack.ready = special_attack.recharge_success
                            available_special_attacks: List[SpecialAbility] = list(filter(lambda a: a.ready, attacker.sa)) if attacker.sa else []
                            # Main loop
                            if attacker.is_spell_caster and castable_spells:
                                target_char: Character = (choice(ranged_chars) if ranged_chars else choice(melee_chars))
                                attack_spell: Spell = max(castable_spells, key=lambda s: s.level)
                                attack_msg, damage = attacker.cast_attack(target_char, attack_spell, verbose=False)
                                target_char.hit_points -= damage
                                self.cprint(attack_msg)
                                self.cprint(f"{color.GREEN}{attacker.name}{color.END} attacks {target_char.name} with ** {attack_spell.name.upper()} **")
                                if target_char.hit_points <= 0:
                                    alive_chars.remove(target_char)
                                    target_char.status = "DEAD"
                                    self.cprint(f"{target_char.name} is ** KILLED **!")
                                # Refresh party table to show updated conditions
                                self.refresh_party_table()
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
                                        attack_msg, damage = attacker.special_attack(target_char, special_attack, verbose=False)
                                        target_char.hit_points -= damage
                                        self.cprint(attack_msg)
                                        if target_char.hit_points <= 0:
                                            # cprint('/'.join([c.name for c in alive_chars]))
                                            # cprint(f'removing {char.name}');
                                            alive_chars.remove(target_char)
                                            target_char.status = "DEAD"
                                            self.cprint(f"{target_char.name} is ** KILLED **!")
                                # Refresh party table to show updated conditions
                                self.refresh_party_table()
                            else:
                                # Monster attacks with any available action
                                if melee_chars:
                                    target_char: Character = choice(melee_chars)
                                    # Try melee first, then mixed, then ranged
                                    melee_attacks: List[Action] = [a for a in attacker.actions if a.type in (ActionType.MELEE, ActionType.MIXED)] if attacker.actions else []
                                    if not melee_attacks:
                                        # If no melee, try ranged attacks on ranged chars
                                        ranged_attacks: List[Action] = [a for a in attacker.actions if a.type == ActionType.RANGED] if attacker.actions else []
                                        if ranged_attacks and ranged_chars:
                                            target_char = choice(ranged_chars)
                                            melee_attacks = ranged_attacks

                                    if melee_attacks:
                                        attack_msg, damage, damage_type = attacker.attack(target=target_char, actions=melee_attacks, verbose=False)
                                        # Use take_damage to apply resistances/immunities
                                        actual_damage = target_char.take_damage(damage, damage_type)
                                        self.cprint(attack_msg)
                                        if actual_damage < damage:
                                            self.cprint(f"   {color.CYAN}(Reduced from {damage} to {actual_damage} due to resistance/immunity){color.END}")
                                        self.cprint(f"{color.GREEN}{attacker.name}{color.END} attacks {target_char.name}")
                                        if target_char.hit_points <= 0:
                                            alive_chars.remove(target_char)
                                            target_char.status = "DEAD"
                                            self.cprint(f"{target_char.name} is ** KILLED **!")
                                        # Refresh party table to show updated conditions
                                        self.refresh_party_table()
                                    else:
                                        self.cprint(f"** {attacker.name} ** has no attacks available!")
                                        debug(f"  → {attacker.name} actions: {attacker.actions}")
                                else:
                                    debug(f"  → No targets available for {attacker.name}")
                    elif isinstance(attacker, Character): # CHARACTER Attacks
                        debug(f"  → {attacker.name} is a Character")
                        attacker_index: int = self.party.index(attacker)
                        action = self.actions[attacker_index]
                        debug(f"  → Character action: {action.type if action else 'None'}")
                        if action.type == CharActionType.PARRY:
                            self.cprint(f"{color.GREEN}{attacker.name}{color.END} parries!")
                            continue
                        monsters = list(filter(lambda m: m.hit_points > 0, action.targets))
                        if not monsters:
                            continue
                        monster: Monster = min(monsters, key=lambda m: m.hit_points)
                        if action.type == CharActionType.MELEE_ATTACK:
                            attack_msg, damage = attacker.attack(monster=monster, in_melee=(attacker in alive_chars[:3]), verbose=False)
                            monster.hit_points -= damage
                            self.cprint(attack_msg)
                            self.cprint(f"{color.GREEN}{attacker.name}{color.END} attacks {monster.name.title()}!")
                            if monster.hit_points <= 0:
                                alive_monsters.remove(monster)
                                self.cprint(f"{color.RED}{monster.name.title()}{color.END} is ** KILLED **!")
                                victory_msg, xp, gold = attacker.victory(monster, verbose=False)
                                self.cprint(victory_msg)
                                # attacker.treasure(weapons, armors, equipments, potions)
                                if not hasattr(attacker, "kills"): attacker.kills = []
                                attacker.kills.append(monster)
                        elif action.type == CharActionType.SPELL_ATTACK:
                            monster: Monster = min(alive_monsters, key=lambda m: m.hit_points)
                            attack_msg, damage = attacker.cast_attack(action.spell, monster, verbose=False)
                            monster.hit_points -= damage
                            self.cprint(attack_msg)
                            if not action.spell.is_cantrip:
                                attacker.update_spell_slots(spell=action.spell)
                            self.cprint(f"{color.GREEN}{attacker.name}{color.END} casts {action.spell.name} on {monster.name.title()}!")
                            if monster.hit_points <= 0:
                                alive_monsters.remove(monster)
                                self.cprint(f"{color.RED}{monster.name.title()}{color.END} is ** KILLED **!")
                                victory_msg, xp, gold = attacker.victory(monster, verbose=False)
                                self.cprint(victory_msg)
                                # attacker.treasure(weapons, armors, equipments, potions)
                                if not hasattr(attacker, "kills"): attacker.kills = []
                                attacker.kills.append(monster)
                        elif action.type == CharActionType.SPELL_DEFENSE:
                            # Ensure best_slot_level exists even if loop doesn't run
                            best_slot_level = 0
                            for char in action.targets:
                                best_slot_level = attacker.get_best_slot_level(heal_spell=action.spell, target=char)
                                if action.spell.range == 5:
                                    attacker.cast_heal(action.spell, best_slot_level, [char])
                                    self.cprint(f"{color.GREEN}{attacker.name}{color.END} casts {action.spell.name} on {char.name}!")
                                else:
                                    attacker.cast_heal(action.spell, best_slot_level, self.party)
                                    self.cprint(f"{color.GREEN}{attacker.name}{color.END} casts {action.spell.name} on PARTY!")
                            if not action.spell.is_cantrip:
                                attacker.update_spell_slots(action.spell, best_slot_level)
            except Exception as e:
                debug(f"ERROR in combat loop: {type(e).__name__}: {str(e)}")
                import traceback
                debug(traceback.format_exc())
                self.cprint(f"ERROR: {type(e).__name__}: {str(e)}")
        debug(f"Combat loop finished. Round {self.round_num + 1} complete")
        self.round_num += 1

        # End of Round
        alive_chars: List[Character] = [c for c in self.party if c.hit_points > 0]
        alive_monsters: List[Monster] = [c for c in self.monsters if c.hit_points > 0]

        if not alive_chars:
            # Clear conditions from all party members after defeat
            for target_char in self.party:
                if hasattr(target_char, 'conditions'):
                    if target_char.conditions is None:
                        target_char.conditions = []
                    else:
                        target_char.conditions.clear()
            self.cprint(f"** DEFEAT! ALL PARTY HAS BEEN KILLED **")
            self.ui.party_action_groupBox.setVisible(False)
            self.ui.char_actions_groupBox.setVisible(False)
        elif not alive_monsters:
            self.cprint(f"** VICTORY! **")
            party_level: int = round(sum([c.level for c in self.party]) / len(self.party))
            encounter_gold_table: List[int] = load_encounter_gold_table()
            earned_gold: int = encounter_gold_table[party_level]
            xp_gained: int = sum([m.xp for m in self.monsters])

            # Clear conditions from surviving party members after victory
            for target_char in alive_chars:
                target_char.gold += earned_gold // len(self.party)
                target_char.xp += xp_gained // len(alive_chars)
                if hasattr(target_char, 'conditions'):
                    if target_char.conditions is None:
                        target_char.conditions = []
                    else:
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
                        # Cast to Qt.ItemFlags to satisfy type checkers
                        item.setFlags(Qt.ItemFlags(int(item.flags()) & ~int(Qt.ItemIsSelectable)))
                    else:
                        # Restore normal flags (selectable, enabled, editable if it was)
                        item.setFlags(Qt.ItemFlags(int(Qt.ItemIsEnabled) | int(Qt.ItemIsSelectable)))

    @pyqtSlot()
    def flee(self):
        self.cprint(f"** Party successfully escaped! **")

        # Clear conditions from all party members when fleeing
        for char in self.party:
            if hasattr(char, 'conditions') and char.conditions:
                char.conditions.clear()

        for row in range(self.party_table.rowCount()):
            self.update_cell(content='', row=row, col=self.action_column)
        self.monsters = self.load_monsters()
        self.display_monsters_groups()
        self.actions = [None] * len(self.party)
        self.round_num = 0

        # Refresh party table to show cleared conditions
        self.refresh_party_table()

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
            # Enable buttons based on character conditions
            self.update_action_buttons_state()
        if self.index >= 0:  # Make sure a valid row is selected
            self.ui.char_actions_groupBox.show()
            title: str = f"{char.name}'s Options"
            self.ui.char_actions_groupBox.setTitle(title)
            if char.is_spell_caster:
                self.ui.castButton.show()
            else:
                self.ui.castButton.hide()

    def update_action_buttons_state(self):
        """Enable/disable action buttons based on character conditions"""
        if self.index < 0 or self.index >= len(self.party):
            return

        char: Character = self.party[self.index]

        # Check if character has incapacitating conditions
        can_attack = True
        can_cast = True

        if hasattr(char, 'conditions') and char.conditions:
            for condition in char.conditions:
                condition_type = condition.type if hasattr(condition, 'type') else str(condition)
                # Check for incapacitating conditions
                if condition_type in ['INCAPACITATED', 'PARALYZED', 'PETRIFIED', 'STUNNED', 'UNCONSCIOUS']:
                    can_attack = False
                    can_cast = False
                    break
                # Restrained gives disadvantage but doesn't prevent actions
                elif condition_type == 'RESTRAINED':
                    # Still can attack/cast but with disadvantage (handled in combat logic)
                    pass
                # Blinded gives disadvantage on attacks
                elif condition_type == 'BLINDED':
                    # Still can attack but with disadvantage
                    pass

        # Enable/disable buttons
        self.ui.fightButton.setEnabled(can_attack and char.hit_points > 0)
        self.ui.castButton.setEnabled(can_cast and char.hit_points > 0 and char.is_spell_caster)
        self.ui.parryButton.setEnabled(char.hit_points > 0)

        # Add visual feedback
        if not can_attack:
            self.cprint(f"⚠️ {char.name} is incapacitated and cannot attack!")
        if not can_cast and char.is_spell_caster:
            self.cprint(f"⚠️ {char.name} is incapacitated and cannot cast spells!")

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
                        self.prepare_action(action_type=CharActionType.SPELL_ATTACK, spell=spell)
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

        selected_chars = []

        # Multi-selection: return all selected rows when OK is clicked
        def on_ok():
            selected_rows = set()
            for item in ui.party_tableWidget.selectedItems():
                selected_rows.add(item.row())
            for row in sorted(selected_rows):
                char_name = ui.party_tableWidget.item(row, 0).text()
                char = next((c for c in self.party if c.name == char_name), None)
                if char:
                    selected_chars.append(char)
            select_dialog.accept()

        ui.buttonBox.accepted.connect(on_ok)
        select_dialog.exec_()
        return selected_chars

    @pyqtSlot()
    def use_item(self):
        """Allow character to use a potion or item from inventory"""
        if self.index < 0 or self.index >= len(self.party):
            return

        char: Character = self.party[self.index]

        # Check if character has inventory
        if not hasattr(char, 'inventory') or not char.inventory:
            self.cprint(f"{char.name} has no items in inventory!")
            return

        # Filter usable items (potions)
        from dnd_5e_core.equipment import HealingPotion
        usable_items = [item for item in char.inventory if item and isinstance(item, HealingPotion)]

        if not usable_items:
            self.cprint(f"{char.name} has no usable items (potions)!")
            return

        # Create dialog to select item
        item_dialog = QDialog(self)
        item_dialog.setWindowTitle(f"{char.name}'s Inventory")
        layout = QVBoxLayout(item_dialog)

        # Add label
        label = QLabel(f"Select an item to use:")
        layout.addWidget(label)

        # Create table with items
        item_table = QTableWidget(len(usable_items), 2)
        item_table.setHorizontalHeaderLabels(["Item", "Effect"])
        item_table.horizontalHeader().setStretchLastSection(True)
        item_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        item_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        for i, item in enumerate(usable_items):
            item_table.setItem(i, 0, QTableWidgetItem(item.name))
            if isinstance(item, HealingPotion):
                effect = f"Heals {item.hit_dice}+{item.bonus} HP"
                item_table.setItem(i, 1, QTableWidgetItem(effect))

        layout.addWidget(item_table)

        # Add buttons
        button_layout = QVBoxLayout()
        use_button = QPushButton("Use Item")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(use_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        selected_item = None

        def on_use():
            nonlocal selected_item
            if item_table.currentRow() >= 0:
                selected_item = usable_items[item_table.currentRow()]
                item_dialog.accept()

        def on_cancel():
            item_dialog.reject()

        use_button.clicked.connect(on_use)
        cancel_button.clicked.connect(on_cancel)

        if item_dialog.exec_() == QDialog.DialogCode.Accepted and selected_item:
            # Use the item
            if isinstance(selected_item, HealingPotion):
                # Heal the character
                healing = selected_item.heal()
                old_hp = char.hit_points
                char.hit_points = min(char.hit_points + healing, char.max_hit_points)
                actual_healing = char.hit_points - old_hp

                # Remove item from inventory
                char.inventory.remove(selected_item)

                # Update action and display
                self.actions[self.index] = CharAction(type=CharActionType.PARRY, targets=[], spell=None)
                self.update_cell(content=f"Used {selected_item.name} (+{actual_healing} HP)", row=self.index, col=self.action_column)
                self.cprint(f"✨ {char.name} used {selected_item.name} and healed {actual_healing} HP!")

                # Refresh table to show updated HP
                self.refresh_party_table()
            else:
                self.cprint(f"⚠️ {selected_item.name} cannot be used in combat!")

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
        # Guard against invalid indices (table may be reconfigured)
        if row < 0 or col < 0:
            debug(f"update_cell: invalid row/col {row}/{col}")
            return
        if row >= self.party_table.rowCount() or col >= self.party_table.columnCount():
            debug(f"update_cell: indices out of range ({row}/{self.party_table.rowCount() - 1}), ({col}/{self.party_table.columnCount() - 1})")
            return
        self.party_table.setItem(row, col, QTableWidgetItem(content))
        try:
            self.party_table.resizeColumnToContents(col)
        except Exception:
            pass
        # Advance to next living character row
        self.move_to_next_row()

    def prepare_action(self, action_type: CharActionType, spell: Optional[Spell] = None):
        """Set a pending action and allow the user to click a monster token to select the group.
        If only one monster group exists, behave as before and assign immediately.
        """
        if not hasattr(self, 'monsters_dict') or not self.monsters_dict:
            # No monsters available
            self.cprint("No monsters to target")
            return
        if len(self.monsters_dict) == 1:
            # Only one group: perform selection immediately
            self.select_monsters(action_type, spell)
            return
        # Multiple groups: set pending action and give user feedback
        self.pending_action = (action_type, spell)
        self.cprint(f"Click on a monster token to target (action: {action_type.value if action_type == CharActionType.MELEE_ATTACK else (spell.name if spell else 'SPELL')})")
        # Optionally highlight labels to show they are clickable
        for lbl_name in ("monster_1_Label", "monster_2_Label"):
            lbl = getattr(self.ui, lbl_name, None)
            if lbl and not (lbl.pixmap() is None):
                lbl.setStyleSheet("border: 2px solid yellow;")

    def on_monster_label_clicked(self, monster_name: str, group_index: int):
        """Called when a monster token label is clicked."""
        if not self.pending_action:
            # No action pending: ignore click or inform user
            self.cprint("Please select an action first (Fight / Cast) before clicking a monster token.")
            return
        action_type, spell = self.pending_action
        self.assign_action_to_group(action_type, spell, monster_name, group_index)
        # Clear pending action and remove highlight
        self.pending_action = None
        for lbl_name in ("monster_1_Label", "monster_2_Label"):
            lbl = getattr(self.ui, lbl_name, None)
            if lbl:
                lbl.setStyleSheet("")

    def assign_action_to_group(self, action_type: CharActionType, spell: Optional[Spell], monster_name: str, group_index: int):
        """Assign the specified action to the current party member targeting the named group."""
        # Determine targets: all monsters with this name
        targets = [m for m in self.monsters if m.name == monster_name]
        attack_type = action_type.value if action_type == CharActionType.MELEE_ATTACK else (spell.name if spell else action_type.value)
        action = f"{attack_type} #{group_index + 1}"
        self.actions[self.index] = CharAction(type=action_type, targets=targets, spell=spell)
        self.update_cell(content=action, row=self.index, col=self.action_column)

    def refresh_party_table(self):
        """Setup and populate the party table"""
        # Sort party list - living characters first, dead characters last
        self.party.sort(key=lambda char: char.hit_points <= 0)

        # Configure table (party_table is already initialized in __init__)
        populate_table(table=self.party_table, char_list=self.party, in_dungeon=True, sorting=False)

        # Set column resize modes - Status column (6) should resize to contents
        header = self.party_table.horizontalHeader()
        header.setStretchLastSection(True)

        # Set most columns to Stretch mode
        for col in range(self.party_table.columnCount() - 1):
            if col == 6:  # Status column
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        # Update disabled state for action buttons based on conditions
        self.update_action_buttons_state()
        # self.party_table.cellDoubleClicked.connect(self.inspect_char)

    def load_monster_token(self, name: str) -> Optional[str]:
        for filename in os.listdir(self.token_images_dir):
            monster_name = filename.replace('.webp', '').replace('.png', '').replace('_', ' ').replace('-', ' ').title()
            if monster_name == name:
                 return os.path.join(self.token_images_dir, filename)
        return None

    def add_source_badge(self, pixmap: QPixmap, source: str) -> QPixmap:
        """
        Add a source badge to the monster token pixmap.

        Args:
            pixmap: Original pixmap
            source: Source book code (e.g., "MM", "MPMM", "SKT")

        Returns:
            Pixmap with badge
        """
        # Create a copy to not modify the original
        result = QPixmap(pixmap)


        # Create painter
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Badge dimensions (top-right corner)
        badge_width = min(60, result.width() // 3)
        badge_height = 20
        margin = 5

        # Badge position (top-right)
        badge_x = result.width() - badge_width - margin
        badge_y = margin

        # Choose color based on source
        source_colors = {
            'MM': QColor(70, 130, 180),      # Steel blue (official)
            'MPMM': QColor(46, 139, 87),     # Sea green (updated)
            'SKT': QColor(218, 165, 32),     # Golden rod
            'VGM': QColor(138, 43, 226),     # Blue violet
            'MTF': QColor(220, 20, 60),      # Crimson
            'ERLW': QColor(255, 140, 0),     # Dark orange
            'TCE': QColor(148, 0, 211),      # Dark violet
            'BGDIA': QColor(178, 34, 34),    # Firebrick
        }
        badge_color = source_colors.get(source, QColor(105, 105, 105))  # Dim gray default

        # Draw rounded rectangle background
        painter.setBrush(badge_color)
        painter.setPen(QPen(QColor(255, 255, 255), 1))  # White border
        badge_rect = QRectF(badge_x, badge_y, badge_width, badge_height)
        painter.drawRoundedRect(badge_rect, 3, 3)

        # Draw text
        font = QFont("Arial", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, source)

        painter.end()

        return result

    def load_monsters(self) -> List[Monster]:
        # Default to level 1 if party is empty
        if not self.party:
            party_level = 1
        else:
            party_level: int = round(sum([c.level for c in self.party]) / len(self.party))

        encounter_levels: List[int] = generate_encounter_levels(party_level=party_level)
        if not encounter_levels:
            encounter_levels = generate_encounter_levels(party_level=party_level)
        encounter_level: int = encounter_levels.pop() if encounter_levels else party_level

        # Use new API: select_monsters_by_encounter_table returns (monsters, encounter_type)
        monsters, encounter_type = generate_encounter(
            encounter_level=encounter_level,
            available_monsters=self.monsters_db,
            allow_pairs=True
        )

        for m in monsters:
            m.hp_roll()
        return monsters

    def display_monsters_groups(self):
        # Get unique monsters and their counts
        monster_names = [m.name for m in self.monsters if m.hit_points > 0]
        if not monster_names:
            return

        # Preserve order of appearance when computing unique monsters
        unique_monsters = []
        for n in monster_names:
            if n not in unique_monsters:
                unique_monsters.append(n)

        # Build ordered monsters_dict so the table and labels match the same order
        self.monsters_dict = {m: monster_names.count(m) for m in unique_monsters}

        # Setup labels for each unique monster and map them to their name + index
        label_map = []  # list of tuples: (pixmap, label_widget, monster_name, index)
        if len(unique_monsters) >= 1:
            token_path = self.load_monster_token(unique_monsters[0])
            if token_path:
                monster_1_pixmap = QPixmap(token_path)
                # Add source badge if monster has source
                monster_obj = next((m for m in self.monsters if m.name == unique_monsters[0]), None)
                if monster_obj and hasattr(monster_obj, 'source') and monster_obj.source:
                    monster_1_pixmap = self.add_source_badge(monster_1_pixmap, monster_obj.source)
                self.ui.monster_1_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_map.append((monster_1_pixmap, self.ui.monster_1_Label, unique_monsters[0], 0))
        if len(unique_monsters) >= 2:
            token_path = self.load_monster_token(unique_monsters[1])
            if token_path:
                monster_2_pixmap = QPixmap(token_path)
                # Add source badge if monster has source
                monster_obj = next((m for m in self.monsters if m.name == unique_monsters[1]), None)
                if monster_obj and hasattr(monster_obj, 'source') and monster_obj.source:
                    monster_2_pixmap = self.add_source_badge(monster_2_pixmap, monster_obj.source)
                self.ui.monster_2_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.monster_2_Label.setVisible(True)
                label_map.append((monster_2_pixmap, self.ui.monster_2_Label, unique_monsters[1], 1))
        else:
            self.ui.monster_2_Label.clear()
            self.ui.monster_2_Label.setVisible(False)

        # Update monsters table
        populate_monsters_table(table=self.ui.monsters_tableWidget, monsters=self.monsters_dict)

        # Update labels with pixmaps and tooltips
        for pixmap, label, monster, idx in label_map:
            # Scale and set pixmap
            scaled_pixmap = pixmap.scaled(
                label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
            label.setScaledContents(True)

            # Update tooltip (hover)
            if hasattr(label, "tooltip_filter"):
                label.removeEventFilter(label.tooltip_filter)
                label.tooltip_filter.deleteLater()

            tooltip_filter = ToolTipFilter(label, str(monster))
            label.installEventFilter(tooltip_filter)
            label.tooltip_filter = tooltip_filter
            label.setMouseTracking(True)

            # Make label clickable: override mousePressEvent to route to our handler
            # Use a bound lambda capturing monster name and index
            def make_mouse_press(mon_name, mon_idx):
                return lambda event: self.on_monster_label_clicked(mon_name, mon_idx)

            label.mousePressEvent = make_mouse_press(monster, idx)
