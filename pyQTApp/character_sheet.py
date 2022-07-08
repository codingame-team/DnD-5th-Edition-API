#
# Created by: philRG
#
import os
import pickle
import random
import sys
from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog

from dao_classes import Character, Weapon, Armor
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


@pyqtSlot(Character, QDialog)
def save_character(char: Character, dialog: QDialog):
    print(f'Sauvegarde personnage {char.name}')
    path = os.path.dirname(__file__)
    with open(f'{path}/gameState/characters/{char.name}.dmp', 'wb') as f1:
        pickle.dump(char, f1)
    dialog.accept()


@pyqtSlot(Character, Ui_character_Dialog,  str)
def change_weapon(char: Character, ui: Ui_character_Dialog, weapon_name: str):
    char.weapon = [e for e in char.inventory if isinstance(e, Weapon) and e.name == weapon_name][0]
    ui.damage_label.setText(str(char.weapon.damage_dice))


@pyqtSlot(Character, Ui_character_Dialog, str)
def change_armor(char: Character, ui: Ui_character_Dialog, armor_name: str):
    char.armor = [e for e in char.inventory if isinstance(e, Armor) and e.name == armor_name][0]
    ui.ac_label.setText(str(char.armor_class))

def display_char_sheet(dialog: QDialog, ui: Ui_character_Dialog, char: Character):
    dialog.setModal(False)
    dialog.setWindowTitle(f'{char.name}')
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
    ui.damage_label.setText(str(char.weapon.damage_dice))
    ui.hp_label.setText(str(char.hit_points))
    ui.ac_label.setText(str(char.armor_class))
    # Picture
    # https://www.pythonguis.com/faq/adding-images-to-pyqt5-applications/
    image_file: str = f'{path}/images/{char.race}.png'
    if not os.path.isfile(image_file):
        image_file: str = f'{path}/images/Human.png'
    pixmap = QPixmap(image_file)
    debug(f'image file = {image_file}')
    ui.pictureLabel.setPixmap(pixmap)

    for equipment in char.inventory:
        if isinstance(equipment, Weapon):
            ui.weapon_cbx.addItem(equipment.name)
        elif isinstance(equipment, Armor):
            ui.armor_cbx.addItem(equipment.name)

    weapon_index = ui.weapon_cbx.findText(char.weapon.name)
    ui.weapon_cbx.setCurrentIndex(weapon_index)

    armor_index = ui.armor_cbx.findText(char.armor.name)
    ui.armor_cbx.setCurrentIndex(armor_index)

    # ui.weapon_cbx.currentTextChanged.connect(lambda: change_weapon(char))
    # ui.armor_cbx.currentTextChanged.connect(lambda: change_armor(char))
    ui.weapon_cbx.currentTextChanged.connect(partial(change_weapon, char, ui))
    ui.armor_cbx.currentTextChanged.connect(partial(change_armor, char, ui))

    ui.buttonBox.rejected.connect(dialog.reject)  # type: ignore
    ui.buttonBox.accepted.connect(partial(save_character, char, dialog))  # type: ignore

    dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    path = os.path.dirname(__file__)
    roster: List[str] = os.listdir(f'{path}/gameState/characters')
    debug(f'{len(roster)} characters in roster: \n{roster}')
    character_file: str = random.choice(roster)
    with open(f'{path}/gameState/characters/{character_file}', 'rb') as f1:
        debug(f'f1: {f1.name}')
        char: Character = pickle.load(f1)

    dialog = QDialog()
    ui = Ui_character_Dialog()
    ui.setupUi(dialog)
    display_char_sheet(ui, char)
    dialog.show()

    if ui.buttonBox.rejected:
        sys.exit(app.exec_())
