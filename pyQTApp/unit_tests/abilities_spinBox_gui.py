#
# Created by: philRG
#
import sys
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QSpinBox, QApplication, QDialog

from populate_functions import populate
from pyQTApp.qt_designer_widgets.sample_dialog import Ui_Dialog


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


@pyqtSlot(int, QSpinBox)
def sp_callback(value: int, spinBox: QSpinBox):
    global bonus_value, ui
    bonus_value -= value
    spinBox.value += value
    # Step 1: modify bonus modifier label
    ui.bonus_label.setText(str(bonus_value))
    # Step 2: modify maximum spinBox values
    for i, sp in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        sp.setMaximum(min(18, sp.value + bonus_value))
    dialog.repaint()


if __name__ == "__main__":
    global bonus_value, ui
    # font_policies = ['Rellanic', 'Davek', 'Iokharic', 'Barazhad']
    # my_font = QFont(random.choice(font_policies))
    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    dialog.setWindowTitle('PyQT5 Demo')

    """ 1. Choose a race """
    populate_races_combo_box(ui)
    ability_scores, bonus_value = populate_abilities_group_box(ui)
    dialog.show()
    if ui.race_cbx.currentIndexChanged:
        dialog.repaint()
    if ui.class_cbx.currentIndexChanged:
        dialog.repaint()

    ability_scores_initial_sum = sum(ability_scores)
    initial_bonus_value = bonus_value

    for i, sp in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        sp.setMaximum(18)

    for sp in ui.abilities_GroupBox.findChildren(QSpinBox):
        sp.downClicked.connect(sp_callback)
        sp.upClicked.connect(sp_callback)

    if ui.buttonBox.rejected:
        sys.exit(app.exec_())
