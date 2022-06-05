#
# Created by: philRG
#
import os
import pickle
import random
import sys
from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog

from dao_classes import Character, Weapon, Armor
from pyQTApp.character_dialog import Ui_character_Dialog


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


def save_character():
    global dialog, char
    print(f'Sauvegarde personnage {char.name}')
    path = os.path.dirname(__file__)
    with open(f'{path}/characters/{char.name}.dmp', 'wb') as f1:
        pickle.dump(char, f1)
    dialog.accept()


@pyqtSlot(str)
def change_weapon(value):
    global char
    char.weapon = [e for e in char.inventory if isinstance(e, Weapon) and e.name == value][0]
    debug(f'new equipped weapon: {char.weapon.name}')


@pyqtSlot(str)
def change_armor(value):
    global char
    char.armor = [e for e in char.inventory if isinstance(e, Armor) and e.name == value][0]
    debug(f'new equipped armor: {char.armor.name}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_character_Dialog()
    ui.setupUi(dialog)

    # roster: List[str] = ['Ghesh. Heskan', 'Henk', 'Mei']
    path = os.path.dirname(__file__)
    roster: List[str] = os.listdir(f'{path}/characters')
    debug(f'{len(roster)} characters in roster: \n{roster}')
    character_file: str = random.choice(roster)
    with open(f'{path}/characters/{character_file}', 'rb') as f1:
        char: Character = pickle.load(f1)

    dialog.setWindowTitle(f'{char.name}')

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
        # debug(f'equipment -> Type: {type(equipment)} - name : {equipment.name}')
        if isinstance(equipment, Weapon):
            ui.weapon_cbx.addItem(equipment.name)
        elif isinstance(equipment, Armor):
            ui.armor_cbx.addItem(equipment.name)
    weapon_index = ui.weapon_cbx.findData(char.weapon.name)
    debug(f'weapon_index = {weapon_index}')
    ui.weapon_cbx.setCurrentIndex(weapon_index)
    armor_index = ui.weapon_cbx.findData(char.armor.name)
    debug(f'armor_index = {armor_index}')
    ui.armor_cbx.setCurrentIndex(armor_index)

    dialog.show()

    ui.weapon_cbx.currentTextChanged.connect(change_weapon)
    ui.armor_cbx.currentTextChanged.connect(change_armor)

    ui.buttonBox.rejected.connect(dialog.reject)  # type: ignore
    ui.buttonBox.accepted.connect(save_character)  # type: ignore

    if ui.buttonBox.rejected:
        sys.exit(app.exec_())
