import sys
from functools import partial
from typing import List

from PyQt5.QtCore import pyqtSlot, QItemSelection
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QTableWidget, QTableWidgetItem, QDialog, QLabel

from dao_classes import Character
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.common import load_party, get_roster, load_welcome
from pyQTApp.qt_designer_widgets.Tavern_module import Tavern_UI
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from pyQTApp.qt_designer_widgets.gilgamesh_Tavern_QFrame import Ui_tavernFrame


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)






@pyqtSlot(Ui_castleWindow, str)
def boltac_trading_post(castle_ui, value):
    debug(f'value gilgamesh_tavern = {value}')

    layout = castleWindow.layout()
    castle_ui.welcome_label.destroy()

    tavernFrame = QFrame()
    ui = Ui_tavernFrame()
    ui.setupUi(tavernFrame)

    layout.addWidget(tavernFrame)
    tavernFrame.setGeometry(castle_ui.castleFrame.geometry())


@pyqtSlot(Ui_castleWindow, QMainWindow, str)
def gilgamesh_tavern(castle_ui: Ui_castleWindow, castle_window: QMainWindow, value):
    debug(f'value gilgamesh_tavern = {value}')
    # castle_ui.welcome_label.destroy()

    tavernFrame = QFrame()
    ui = Tavern_UI(castle_window=castle_window, castle_ui=castle_ui)
    # ui = Ui_tavernFrame()
    # ui.setupUi(tavernFrame)
    #
    # layout.addWidget(tavernFrame)
    # tavernFrame.setGeometry(castle_ui.castleFrame.geometry())
    #
    # # Populate roster
    # training_grounds: List[Character] = get_roster()
    # debug(f'{len(training_grounds)} characters in roster: \n{training_grounds}')
    # table: QTableWidget = ui.gilgameshTavern_tableWidget
    # populate(table, training_grounds)
    # table.selectionModel().selectionChanged.connect(partial(disable_remove_button, ui))
    # ui.addToPartyButton.clicked.connect(add_char_to_party)
    #
    # # Populate party
    # party: List[Character] = load_party()
    # party_table: QTableWidget = castle_ui.party_tableWidget
    # # populate(party_table, party)
    # party_table.selectionModel().selectionChanged.connect(disable_add_button)
    # ui.removeFromPartyButton.clicked.connect(remove_char_from_party)
    #
    # table.itemDoubleClicked.connect(add_character)
    # party_table.itemDoubleClicked.connect(remove_character)
    #
    # # ui.inspectButton.clicked.connect(inspect_char)
    # ui.inspectButton.clicked.connect(partial(inspect_char, castle_ui))

    # castleWindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    castle_window = QMainWindow()
    castle_ui = Ui_castleWindow()
    castle_ui.setupUi(castle_window)

    layout = castle_window.layout()

    welcome_pixmap: QPixmap = load_welcome()
    castle_ui.welcome_label = QLabel(castle_ui.castleFrame)
    castle_ui.welcome_label.setPixmap(welcome_pixmap)

    castle_ui.actionGilgamesh_Tavern.triggered.connect(partial(gilgamesh_tavern, castle_ui, castle_window))
    # castle_ui.actionBoltac_Trading_Post.triggered.connect(boltac_trading_post)

    castle_window.show()
    sys.exit(app.exec_())
