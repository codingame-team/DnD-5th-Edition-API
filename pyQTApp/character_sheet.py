#
# Created by: philRG
#
import os
import pickle
import random
import sys
from functools import partial
from typing import List, Optional

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QListWidgetItem

# ============================================
# MIGRATION: Add dnd-5e-core to path
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)

from dnd_5e_core.entities import Character
from dnd_5e_core.equipment.weapon import WeaponData
from dnd_5e_core.equipment.armor import ArmorData
from dnd_5e_core.equipment.magic_item import MagicItem

print("✅ [MIGRATION v2] character_sheet.py - Using dnd-5e-core package")

# Import from persistence module
from persistence import get_roster

from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_common import populate_spell_table
from pyQTApp.qt_designer_widgets.spells_dialog import Ui_spellsDialog
from tools.common import get_save_game_path


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


class CharacterDialog(QDialog):
    def __init__(self, char: Character):
        super().__init__()
        self.ui = Ui_character_Dialog()
        self.char = char
        self.modified_char = False  # Add flag to track modifications
        self.ui.setupUi(self)
        if not self.char.sc:
            self.ui.spells_groupBox.setVisible(False)

    @pyqtSlot()
    def save_char(self):
        self.modified_char = True  # Set modification flag
        self.accept()

    @pyqtSlot()
    def view_spellbook(self):
        spells_dialog = QDialog(self)
        ui = Ui_spellsDialog()
        ui.setupUi(spells_dialog)
        self.display_spellbook(spells_dialog, ui)

    @pyqtSlot(str)
    def change_weapon(self, weapon_name: str):
        weapons = [e for e in self.char.inventory if e and isinstance(e, WeaponData)]

        if weapon_name == "None":
            # Unequip all weapons
            for weapon in weapons:
                weapon.equipped = False
            self.ui.damage_label.setText("1d2")
        else:
            # Find and equip selected weapon
            selected_weapon = next((w for w in weapons if w.name == weapon_name), None)
            if selected_weapon:
                # Check if weapon is two-handed
                is_two_handed = any(prop.index == 'two-handed' for prop in selected_weapon.properties)

                # Check if shield is equipped
                shield_equipped = self.char.shield is not None

                if is_two_handed and shield_equipped:
                    # Show warning and revert to current weapon
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self,
                        "Cannot Equip",
                        f"Cannot equip {selected_weapon.name} (two-handed weapon) while wearing a shield!\n\n"
                        "Please unequip the shield first."
                    )
                    # Revert to current weapon
                    current_weapon_name = self.char.weapon.name if self.char.weapon else "None"
                    self.ui.weapon_cbx.blockSignals(True)
                    weapon_index = self.ui.weapon_cbx.findText(current_weapon_name)
                    self.ui.weapon_cbx.setCurrentIndex(weapon_index if weapon_index >= 0 else 0)
                    self.ui.weapon_cbx.blockSignals(False)
                    return

                # Equip the weapon
                for weapon in weapons:
                    weapon.equipped = weapon == selected_weapon
                self.ui.damage_label.setText(str(selected_weapon.damage_dice))
            else:
                self.ui.damage_label.setText("1d2")

        self.modified_char = True

    @pyqtSlot(str)
    def change_armor(self, armor_name: str):
        if armor_name == "None":
            # Unequip all armor (exclude shields by category)
            armors = [e for e in self.char.inventory if e and isinstance(e, ArmorData) and not (hasattr(e, 'category') and getattr(e.category, 'index', None) == 'shield')]
            for armor in armors:
                armor.equipped = False
        else:
            # Find and equip selected armor (exclude shields by category)
            armors = [e for e in self.char.inventory if e and isinstance(e, ArmorData) and not (hasattr(e, 'category') and getattr(e.category, 'index', None) == 'shield')]
            selected_armor = next((a for a in armors if a.name == armor_name), None)
            if selected_armor:
                for armor in armors:
                    armor.equipped = armor == selected_armor

        self.ui.ac_label.setText(str(self.char.armor_class))
        self.modified_char = True

    @pyqtSlot(str)
    def change_shield(self, shield_name: str):
        if shield_name == "None":
            # Unequip all shields (detect by category)
            shields = [e for e in self.char.inventory if e and isinstance(e, ArmorData) and hasattr(e, 'category') and getattr(e.category, 'index', None) == 'shield']
            for shield in shields:
                shield.equipped = False
        else:
            # Check if current weapon is two-handed
            if self.char.weapon:
                is_two_handed = any(prop.index == 'two-handed' for prop in self.char.weapon.properties)

                if is_two_handed:
                    # Show warning and keep shield unequipped
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self,
                        "Cannot Equip",
                        f"Cannot equip shield while wielding {self.char.weapon.name} (two-handed weapon)!\n\n"
                        "Please unequip the two-handed weapon first."
                    )
                    # Revert to "None"
                    self.ui.shield_cbx.blockSignals(True)
                    self.ui.shield_cbx.setCurrentIndex(0)  # "None" is always at index 0
                    self.ui.shield_cbx.blockSignals(False)
                    return

            # Find and equip selected shield (detect by category)
            shields = [e for e in self.char.inventory if e and isinstance(e, ArmorData) and hasattr(e, 'category') and getattr(e.category, 'index', None) == 'shield']
            selected_shield = next((s for s in shields if s.name == shield_name), None)
            if selected_shield:
                for shield in shields:
                    shield.equipped = shield == selected_shield

        # Update AC display
        self.ui.ac_label.setText(str(self.char.armor_class))

        # Update damage display (for versatile weapons that have different damage with/without shield)
        # Examples: Longsword (1d8/1d10), Trident of Fish Command, etc.
        if self.char.weapon:
            self.ui.damage_label.setText(str(self.char.damage_dice.dice))

        self.modified_char = True

    @pyqtSlot(QListWidgetItem)
    def misc_item_double_clicked(self, item):
        """Equip/unequip non-weapon/non-armor magic items from the misc list."""
        name = item.text()
        # Find item in inventory by name
        m_item = next((it for it in self.char.inventory if it and getattr(it, 'name', None) == name), None)
        if not m_item:
            return
        # Toggle equipped state via equip_magic_item or remove
        from PyQt5.QtWidgets import QMessageBox
        if hasattr(m_item, 'is_magic') and getattr(m_item, 'is_magic', False):
            # If already equipped, unequip and remove effects
            if getattr(m_item, 'equipped', False):
                m_item.equipped = False
                if hasattr(m_item, 'remove_from_character'):
                    m_item.remove_from_character(self.char)
            else:
                # Try to equip through Character.equip_magic_item (handles attunement/slot rules)
                msg, ok = self.char.equip_magic_item(m_item)
                if not ok:
                    QMessageBox.warning(self, 'Cannot Equip', msg)
        # Update AC and UI
        self.ui.ac_label.setText(str(self.char.armor_class))
        self.modified_char = True

    def display_spellbook(self, dialog: QDialog, ui: Ui_spellsDialog):
        dialog.setModal(False)
        dialog.setWindowTitle(f"{self.char.name} / {self.char.class_type}")
        spells_table: QTableWidget = ui.spells_tableWidget
        spells_table.verticalHeader().setVisible(
            False
        )  # This will hide the row numbers
        spells_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        spells_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )  # Force scrollbar to always show
        # Populate spells
        if self.char.sc:
            populate_spell_table(spells_table, self.char.sc.learned_spells)

        ui.buttonBox.rejected.connect(dialog.reject)  # type: ignore
        ui.buttonBox.accepted.connect(partial(dialog.accept))  # type: ignore

        dialog.exec_()

    def display_sheet(self):
        char, ui = self.char, self.ui
        self.setModal(False)
        self.setWindowTitle(f"{char.name} (Level {char.level} {char.race} {char.class_type})")
        path = os.path.dirname(__file__)
        # layout.addWidget(dialog)
        # Characteristics
        ui.name_label.setText(char.name)
        ui.level_label.setText(str(char.level))
        if char.subrace:
            ui.race_label.setText(char.subrace.name)
        else:
            ui.race_label.setText(char.race.name)
        for prof in char.proficiencies:
            ui.proficienciesView.addItem(prof.name)
        ui.class_label.setText(char.class_type.name)
        ui.gender_label.setText(char.gender)
        ui.age_label.setText(str(char.age // 52))
        ui.ethnic_label.setText(char.ethnic)
        ui.height_label.setText(char.height)
        ui.weight_label.setText(char.weight)
        # Abilities
        ui.str_label.setText(str(char.abilities.str))
        ui.dex_label.setText(str(char.abilities.dex))
        ui.con_label.setText(str(char.abilities.con))
        ui.int_label.setText(str(char.abilities.int))
        ui.wis_label.setText(str(char.abilities.wis))
        ui.cha_label.setText(str(char.abilities.cha))
        # Combat
        ui.hp_label.setText(str(char.hit_points) + " / " + str(char.max_hit_points))
        ui.ac_label.setText(str(char.armor_class))
        if char.weapon:
            # ui.damage_label.setText(str(char.weapon.damage_dice.dice))
            ui.damage_label.setText(str(char.damage_dice))
        else:
            ui.damage_label.setText("1d2")
        # Picture
        # https://www.pythonguis.com/faq/adding-images-to-pyqt5-applications/
        image_file: str = f"{path}/images/{char.race}.png"
        if not os.path.isfile(image_file):
            image_file: str = f"{path}/images/Human.png"
        pixmap = QPixmap(image_file)
        # debug(f'image file = {image_file}')
        ui.pictureLabel.setPixmap(pixmap)

        # Equipment
        # First add "None" option to each combobox
        ui.weapon_cbx.addItem("None")
        ui.shield_cbx.addItem("None")
        ui.armor_cbx.addItem("None")

        # Filter out None items from inventory
        for item in filter(None, char.inventory):
             if isinstance(item, WeaponData):
                 ui.weapon_cbx.addItem(item.name)
             elif isinstance(item, ArmorData):
                # Use category to detect shields
                cat_idx = getattr(item.category, 'index', None) if hasattr(item, 'category') else None
                if cat_idx == 'shield':
                    ui.shield_cbx.addItem(item.name)
                else:
                    ui.armor_cbx.addItem(item.name)
             elif isinstance(item, MagicItem):
                # Ensure we have a misc items list widget created only once
                if not hasattr(self, 'misc_list'):
                    from PyQt5.QtWidgets import QListWidget
                    self.misc_list = QListWidget(self.ui.equipment_groupBox)
                    # place misc_list under existing layout (row 4)
                    try:
                        self.ui.gridLayout_6.addWidget(self.misc_list, 4, 0, 1, 2)
                    except Exception:
                        # fallback: add to equipment_groupBox
                        self.ui.gridLayout_6.addWidget(self.misc_list)
                    self.misc_list.itemDoubleClicked.connect(self.misc_item_double_clicked)
                # Add magic item to misc list if not armor/weapon
                self.misc_list.addItem(item.name)

        weapon_index = ui.weapon_cbx.findText(char.weapon.name) if char.weapon else 0
        ui.weapon_cbx.setCurrentIndex(weapon_index if weapon_index >= 0 else 0)

        armor_index = ui.armor_cbx.findText(char.armor.name) if char.armor else 0
        ui.armor_cbx.setCurrentIndex(armor_index if armor_index >= 0 else 0)

        shield_index = ui.shield_cbx.findText(char.shield.name) if char.shield else 0
        ui.shield_cbx.setCurrentIndex(shield_index if shield_index >= 0 else 0)

        # ui.weapon_cbx.currentTextChanged.connect(lambda: change_weapon(char))
        # ui.armor_cbx.currentTextChanged.connect(lambda: change_armor(char))
        ui.weapon_cbx.currentTextChanged.connect(partial(self.change_weapon))
        ui.armor_cbx.currentTextChanged.connect(partial(self.change_armor))
        ui.shield_cbx.currentTextChanged.connect(partial(self.change_shield))

        # Spellbook
        # Spells section
        if char.is_spell_caster and char.sc:
            # Safety check for spell_slots
            if char.sc.spell_slots:
                slots: str = "/".join(map(str, char.sc.spell_slots))
            else:
                slots: str = "No spell slots"
            ui.slots_label.setText(slots)

        ui.spellBookButton.clicked.connect(partial(self.view_spellbook))

        ui.buttonBox.rejected.connect(self.reject)  # type: ignore
        ui.buttonBox.accepted.connect(partial(self.accept))  # type: ignore

        if self.exec() == QDialog.DialogCode.Accepted:
            return self.modified_char
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)

    game_path = get_save_game_path()
    characters_dir = f"{game_path}/characters"
    roster: List[Character] = get_roster(characters_dir)
    debug(f"{len(roster)} characters in roster! \n")
    char: Character = random.choice(roster)
    # char: Character = [c for c in roster if c.name == 'Brottor'][0]
    with open(f"{characters_dir}/{char.name}.dmp", "rb") as f1:
        # debug(f'f1: {f1.name}')
        char: Character = pickle.load(f1)

    character_dialog = CharacterDialog(char)
    character_dialog.display_sheet()
    # dialog.show()
