#
# Created by: philRG
#
import random
import sys
from typing import List

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSpinBox

from populate_functions import populate
from pyQTApp.sample_dialog import Ui_Dialog
from tools.ability_scores_roll import ability_rolls


class SpinBox(QtWidgets.QSpinBox):
    upClicked = QtCore.pyqtSignal()
    downClicked = QtCore.pyqtSignal()

    def __init__(self, sp: QSpinBox, name: str):
        super().__init__(sp)
        self.name = name

    def mousePressEvent(self, event):
        last_value = self.value()
        super(SpinBox, self).mousePressEvent(event)
        if self.value() < last_value:
            self.downClicked.emit()
        elif self.value() > last_value:
            self.upClicked.emit()


def populate_races_combo_box(ui: Ui_Dialog):
    _translate = QtCore.QCoreApplication.translate
    races_names: List[str] = populate(collection_name='races', key_name='results')
    ui.race_cbx.addItems(races_names)
    class_names: List[str] = populate(collection_name='classes', key_name='results')
    ui.class_cbx.addItems(class_names)


def populate_abilities_group_box(ui: Ui_Dialog) -> List[int]:
    bonus_value: int = random.randint(5, 10)
    ui.bonus_label.setText(str(bonus_value))
    ability_scores: List[int] = ability_rolls()
    for i, ability_spinBox in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        ability_spinBox.value = ability_scores[i]
        ability_spinBox.setMinimum(ability_spinBox.value)
    return ability_scores, bonus_value


# Méthode initiale
def sp_callback(value):
    global bonus_value, ability_scores, ui
    # Step 1: modify bonus modifier label
    print(f'new value: {value}')
    bonus_table: List[int] = [0, 1, 2, 3, 4, 5, 7, 9]
    for i, sp in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        score: int = ability_scores[i]
        if score != int(sp.value):
            print(f'{sp.objectName()} - score = {score} - sp_value = {value}')
            bonus_value = bonus_value - bonus_table[score - 8] if score > int(sp.value) else bonus_value + bonus_table[score - 8]
            ability_scores[i] = int(sp.value)
    # Step 2: modify maximum spinBox values
    for i, sp in enumerate(ui.abilities_GroupBox.findChildren(QSpinBox)):
        max_value: int = ability_scores[i] + bonus_value
        sp.setMaximum(max_value)
    ui.bonus_label.setText(str(bonus_value))
    dialog.repaint()


# Méthode alternative
def callback(event):
    print(event)
    ui.bonus_label.setText("Up")
    ui.bonus_label.repaint()
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

    # Méthode initiale
    for sp in ui.abilities_GroupBox.findChildren(QSpinBox):
        print(f'nom de mon objet QSpinBox: {sp.objectName}')
        sp.valueChanged.connect(sp_callback)

    # Méthode avec super classe dérivée SpinBox: Ne marche pas non plus
    spin_boxes: List[SpinBox] = []
    for sp in ui.abilities_GroupBox.findChildren(QSpinBox):
        spin_boxes.append(SpinBox(sp=sp, name=sp.objectName().split('_')[0]))
    for sb in spin_boxes:
        # sb.downClicked.connect(lambda: ui.bonus_label.setText(int(ui.bonus_label.text()) + 1))
        # sb.upClicked.connect(lambda: ui.bonus_label.setText(int(ui.bonus_label.text()) - 1))
        # sb.downClicked.connect(lambda: ui.bonus_label.setText("Up"))
        # sb.upClicked.connect(lambda: ui.bonus_label.setText("Down"))
        sb.downClicked.connect(callback)
        sb.upClicked.connect(callback)

    if ui.buttonBox.rejected:
        sys.exit(app.exec_())
