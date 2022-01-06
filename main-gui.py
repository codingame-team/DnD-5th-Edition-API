
#
# Created by: Fifi
#
import random
import sys
from typing import List

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont

from populate_functions import populate
from sample_dialog import Ui_Dialog


def populate_races_combo_box(ui: Ui_Dialog):
    _translate = QtCore.QCoreApplication.translate
    races_names: List[str] = populate(collection_name='races', key_name='results')
    ui.comboBox.addItems(races_names)


if __name__ == "__main__":
    font_policies = ['Rellanic', 'Davek', 'Iokharic', 'Barazhad']
    my_font = QFont(random.choice(font_policies))
    my_text = "Conan"
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    populate_races_combo_box(ui)
    dialog.show()
    # my_font = Font(family=random.choice(font_policies), size=64, weight='bold')
    # my_label = Label(top, text=text, font=my_font)
    # my_label.focus()
    # my_label.pack(pady=20)
    if ui.comboBox.currentIndexChanged:
        #ui.output.setFont(my_font)
        ui.output.setText(ui.comboBox.currentText())
        dialog.repaint()
        # dialog.show()
    if ui.buttonBox.rejected:
        sys.exit(app.exec_())