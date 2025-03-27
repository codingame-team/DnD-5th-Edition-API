#
# Created by: philRG
#
import os
import pickle
import random
import sys
from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QHeaderView

from dao_classes import Character, Weapon, Armor
from main import get_roster
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_designer_widgets.qt_common import addSpellItem, populate_spell_table
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
        weapons = [e for e in self.char.inventory if isinstance(e, Weapon)]

        if weapon_name == "None":
            # Unequip all weapons
            for weapon in weapons:
                weapon.equipped = False
            self.ui.damage_label.setText("1d2")
        else:
            # Find and equip selected weapon
            selected_weapon = next((w for w in weapons if w.name == weapon_name), None)
            if selected_weapon:
                for weapon in weapons:
                    weapon.equipped = weapon == selected_weapon
                self.ui.damage_label.setText(str(selected_weapon.damage_dice.dice))
            else:
                self.ui.damage_label.setText("1d2")

        self.modified_char = True

    @pyqtSlot(str)
    def change_armor(self, armor_name: str):
        if armor_name == "None":
            # Unequip all armor
            armors = [e for e in self.char.inventory if isinstance(e, Armor) and e.index != 'shield']
            for armor in armors:
                armor.equipped = False
        else:
            # Find and equip selected armor
            armors = [e for e in self.char.inventory if isinstance(e, Armor) and e.index != 'shield']
            selected_armor = next((a for a in armors if a.name == armor_name), None)
            if selected_armor:
                for armor in armors:
                    armor.equipped = armor == selected_armor

        self.ui.ac_label.setText(str(self.char.armor_class))
        self.modified_char = True

    @pyqtSlot(str)
    def change_shield(self, shield_name: str):
        if shield_name == "None":
            # Unequip all shields
            shields = [e for e in self.char.inventory if isinstance(e, Armor) and e.index == 'shield']
            for shield in shields:
                shield.equipped = False
        else:
            # Find and equip selected shield
            shields = [e for e in self.char.inventory if isinstance(e, Armor) and e.index == 'shield']
            selected_shield = next((s for s in shields if s.name == shield_name), None)
            if selected_shield:
                for shield in shields:
                    shield.equipped = shield == selected_shield

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
        self.setWindowTitle(f"{char.name}")
        path = os.path.dirname(__file__)
        # layout.addWidget(dialog)
        # Characteristics
        ui.name_label.setText(char.name)
        if char.subrace:
            ui.race_label.setText(char.subrace.name)
        else:
            ui.race_label.setText(char.race.name)
        for prof in char.proficiencies:
            ui.proficienciesView.addItem(prof.name)
        ui.class_label.setText(char.class_type.name)
        ui.gender_label.setText(char.gender)
        ui.ethnic_label.setText(char.ethnic)
        ui.height_label.setText(char.height)
        ui.weight_label.setText(char.weight)
        # Abilities
        ui.str_label.setText(str(char.strength))
        ui.dex_label.setText(str(char.dexterity))
        ui.con_label.setText(str(char.constitution))
        ui.int_label.setText(str(char.intelligence))
        ui.wis_label.setText(str(char.wisdom))
        ui.cha_label.setText(str(char.charism))
        # Combat
        if char.weapon and char.weapon.equipped:
            ui.damage_label.setText(str(char.weapon.damage_dice))
            ui.hp_label.setText(str(char.hit_points) + " / " + str(char.max_hit_points))
            ui.ac_label.setText(str(char.armor_class))
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
        for item in char.inventory:
            if isinstance(item, Weapon):
                ui.weapon_cbx.addItem(item.name)
            elif isinstance(item, Armor):
                if item.index == "shield":
                    ui.shield_cbx.addItem(item.name)
                else:
                    ui.armor_cbx.addItem(item.name)

        weapon_index = ui.weapon_cbx.findText(char.weapon.name) if char.weapon else -1
        ui.weapon_cbx.setCurrentIndex(weapon_index)

        #if hasattr(char, "armor"):
        armor_index = ui.armor_cbx.findText(char.armor.name) if char.armor else -1
        ui.armor_cbx.setCurrentIndex(armor_index)
        shield_index = ui.shield_cbx.findText(char.shield.name) if char.shield else -1
        ui.shield_cbx.setCurrentIndex(shield_index)

        # ui.weapon_cbx.currentTextChanged.connect(lambda: change_weapon(char))
        # ui.armor_cbx.currentTextChanged.connect(lambda: change_armor(char))
        ui.weapon_cbx.currentTextChanged.connect(partial(self.change_weapon))
        ui.armor_cbx.currentTextChanged.connect(partial(self.change_armor))
        ui.shield_cbx.currentTextChanged.connect(partial(self.change_shield))

        # Spellbook
        # Spells section
        if char.is_spell_caster:
            slots: str = "/".join(map(str, char.sc.spell_slots))
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
