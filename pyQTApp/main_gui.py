#
# Created by: philRG
#
import random
import sys
from typing import List

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSpinBox

from populate_functions import populate
from pyQTApp.sample_dialog import Ui_Dialog
from tools.ability_scores_roll import ability_rolls


def populate_races_combo_box(ui: Ui_Dialog):
    _translate = QtCore.QCoreApplication.translate
    races_names: List[str] = populate(collection_name='races', key_name='results')
    ui.race_cbx.addItems(races_names)
    class_names: List[str] = populate(collection_name='classes', key_name='results')
    ui.class_cbx.addItems(class_names)


def populate_abilities_group_box(ui: Ui_Dialog) -> List[int]:
    # bonus_value: int = random.randint(5, 10)
    bonus_value: int = 27
    ui.bonus_label.setText(str(bonus_value))
    # ability_scores: List[int] = ability_rolls()
    ability_scores: List[int] = [8] * 6
    for i, ability_spinBox in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        ability_spinBox.value = ability_scores[i]
        ability_spinBox.setMinimum(ability_spinBox.value)
    return ability_scores, bonus_value


@pyqtSlot(int)
def sp_callback(value):
    global bonus_value, ui
    print(f'new value: {value}')
    # bonus_table: List[int] = [0, 1, 2, 3, 4, 5, 7, 9]
    ability_scores_current_sum: int = sum([sp.value for sp in ui.abilities_GroupBox.findChildren(QSpinBox)])
    print(f'ability_scores_current_sum: {ability_scores_current_sum}')
    bonus_value = initial_bonus_value - (ability_scores_current_sum - ability_scores_initial_sum)
    # Step 1: modify bonus modifier label
    print(f'new bonus_value: {bonus_value}')
    ui.bonus_label.setText(str(bonus_value))
    ui.bonus_label.repaint()
    # Step 2: modify maximum spinBox values
    for i, sp in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        sp.setMaximum(min(18, sp.value + bonus_value))
    dialog.repaint()


if __name__ == "__main__":
    font_policies = ['Rellanic', 'Davek', 'Iokharic', 'Barazhad']
    my_font = QFont(random.choice(font_policies))
    my_text = "Conan"
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    dialog.setWindowTitle('PyQT5 Demo')
    populate_races_combo_box(ui)
    ability_scores, bonus_value = populate_abilities_group_box(ui)
    dialog.show()
    if ui.race_cbx.currentIndexChanged:
        dialog.repaint()
    if ui.class_cbx.currentIndexChanged:
        dialog.repaint()

    # for sp in ui.abilities_GroupBox.findChildren(QSpinBox):
    #     print(sp.objectName())

    ability_scores_initial_sum = sum(ability_scores)
    initial_bonus_value = bonus_value

    for i, sp in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        sp.setMaximum(18)

    for sp in ui.abilities_GroupBox.findChildren(QSpinBox):
        sp.valueChanged.connect(sp_callback)

    if ui.buttonBox.rejected:
        sys.exit(app.exec_())
