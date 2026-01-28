from functools import partial
from typing import List, Optional
import os
import sys

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QTableWidget,
    QMainWindow, QWidget,
    QHeaderView,
    QSizePolicy,
)

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)

from dnd_5e_core.entities import Character
from dnd_5e_core.equipment import Equipment, Potion

# Import BoltacShop for shared catalog
try:
    from boltac_shop import get_boltac_shop
    BOLTAC_SHOP_AVAILABLE = True
except ImportError:
    BOLTAC_SHOP_AVAILABLE = False

# Import from persistence module
from persistence import load_party, save_character, save_party

from populate_rpg_functions import load_potions_collections
from pyQTApp.common import update_buttons
from pyQTApp.qt_designer_widgets.boltac_Trading_Post_QFrame import Ui_boltacFrame
from pyQTApp.qt_designer_widgets.castleWindow import Ui_castleWindow

from pyQTApp.qt_common import addItem
from tools.common import get_save_game_path


class Boltac_UI(QWidget):
    def __init__(self, castle_window: QMainWindow, castle_ui: Ui_castleWindow):
        super().__init__()
        self.castle_ui = castle_ui
        self.boltacFrame = QFrame()
        self.ui = Ui_boltacFrame()
        self.ui.setupUi(self.boltacFrame)
        layout = castle_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.boltacFrame)
        # layout.addWidget(self.tavernFrame, alignment=Qt.AlignmentFlag.AlignRight)
        self.boltacFrame.setGeometry(castle_ui.castleFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.boltacFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Populate party
        self.party = castle_window.party
        self.party_table = castle_ui.party_tableWidget

        self.potions = load_potions_collections()

        self.buy_table: QTableWidget = self.ui.boltacBuy_tableWidget
        # Make table expand to fill container
        self.buy_table.horizontalHeader().setStretchLastSection(True)
        self.buy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.buy_table.setSortingEnabled(True)
        self.buy_table.verticalHeader().setVisible(False)  # This will hide the row numbers
        self.buy_table.selectionModel().selectionChanged.connect(self.disable_sell_button)

        self.sell_table: QTableWidget = self.ui.boltacSell_tableWidget
        # Make table expand to fill container
        self.sell_table.horizontalHeader().setStretchLastSection(True)
        self.sell_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sell_table.setSortingEnabled(True)
        self.sell_table.verticalHeader().setVisible(False)  # This will hide the row numbers
        self.sell_table.selectionModel().selectionChanged.connect(self.disable_buy_button)

        # self.party_table.cellDoubleClicked.connect(self.inspect_char)
        # self.ui.inspectButton.clicked.connect(partial(self.inspect_char))

        self.party_table.selectionModel().selectionChanged.connect(partial(self.populate_items))

        self.ui.buyButton.clicked.connect(self.buy_item)
        self.ui.sellButton.clicked.connect(self.sell_item)
        self.ui.poolGoldButton.clicked.connect(self.pool_gold)
        self.ui.divvyGoldButton.clicked.connect(self.divvy_gold)

        self.ui.leaveBoltacButton.setEnabled(True)
        self.ui.leaveBoltacButton.clicked.connect(self.leave_boltac)

        self.equipment_list: List[Equipment] = []
        self.selected_char: Optional[Character] = None

        self.characters_dir = f"{get_save_game_path()}/characters"

    def populate_buy_table(self, char: Character):
        self.buy_table: QTableWidget = self.ui.boltacBuy_tableWidget
        self.buy_table.clearContents()

        # Get items from BoltacShop if available
        if BOLTAC_SHOP_AVAILABLE:
            try:
                shop = get_boltac_shop()

                # Get all weapons and armors
                all_weapons = shop.get_all_weapons()
                all_armors = shop.get_all_armors()

                # Filter by proficiencies (compare by index)
                prof_weapon_indices = {w.index for w in char.prof_weapons if hasattr(w, 'index')}
                prof_armor_indices = {a.index for a in char.prof_armors if hasattr(a, 'index')}

                weapons = [w for w in all_weapons if hasattr(w, 'index') and w.index in prof_weapon_indices]
                armors = [a for a in all_armors if hasattr(a, 'index') and a.index in prof_armor_indices]

                # Get magic items with stock
                magic_items = [item for item, stock in shop.get_magic_items_in_stock() if stock > 0]

                # Combine all items
                self.equipment_list = weapons + armors + self.potions + magic_items
            except Exception as e:
                # Fallback to old system
                self.equipment_list = char.prof_armors + char.prof_weapons + self.potions
        else:
            # Old system
            self.equipment_list = char.prof_armors + char.prof_weapons + self.potions

        self.buy_table.setRowCount(len(self.equipment_list))
        # Ensure table is visible and has proper size
        self.buy_table.setVisible(True)
        self.buy_table.resizeColumnsToContents()
        self.buy_table.resizeRowsToContents()
        for i, item in enumerate(self.equipment_list):
            selectable: bool = item.cost.value <= char.gold * 100
            addItem(table=self.buy_table, item=item, row=i, selectable=selectable)
        self.buy_table.resizeColumnsToContents()
        self.buy_table.resizeRowsToContents()

    def populate_sell_table(self, char: Character):
        self.sell_table: QTableWidget = self.ui.boltacSell_tableWidget
        self.sell_table.clearContents()
        # Filter out None values
        inventory = [item for item in char.inventory if item is not None]
        self.sell_table.setRowCount(len(inventory))
        for i, item in enumerate(inventory):
            # Potions don't have equipped attribute, only Equipment does
            selectable: bool = isinstance(item, Potion) or (hasattr(item, 'equipped') and not item.equipped)
            addItem(table=self.sell_table, item=item, row=i, for_sale=True, selectable=selectable)
        self.sell_table.resizeColumnsToContents()
        self.sell_table.resizeRowsToContents()

    @pyqtSlot()
    def populate_items(self):
        row = self.party_table.currentRow()
        if row >= 0:  # Make sure a row is selected
            char_name: str = self.party_table.item(row, 0).text()
            char: Character = [c for c in self.party if c.name == char_name][0]
            self.populate_buy_table(char)
            self.populate_sell_table(char)
            self.selected_char = char
            self.ui.poolGoldButton.setEnabled(True)
            self.ui.divvyGoldButton.setEnabled(True)
            self.ui.character_label.setText(f'{char.name} - Gold: {char.gold} gp')

    def update_gold_info(self):
        self.ui.character_label.setText(f'{self.selected_char.name} - Gold: {self.selected_char.gold} gp')

    @pyqtSlot()  # For button click
    def buy_item(self):
        row = self.buy_table.currentRow()
        if row >= 0:  # Make sure a row is selected
            self.buy_item_logic(row)
            self.ui.buyButton.setEnabled(True)
            self.update_gold_info()

    @pyqtSlot()  # For button click
    def sell_item(self):
        row = self.sell_table.currentRow()
        if row >= 0:  # Make sure a row is selected
            self.sell_item_logic(row)
            self.ui.sellButton.setEnabled(True)
            self.update_gold_info()

    def _get_gp_cost(self, item) -> int:
        # Robust cost extraction: prefer Cost.quantity (gp), else Cost.value interpreted as cp
        if hasattr(item, 'cost'):
            cost = item.cost
            if hasattr(cost, 'quantity'):
                return int(cost.quantity)
            if hasattr(cost, 'value'):
                # assume value is in copper pieces
                return int(cost.value) // 100
        # Fallbacks
        if isinstance(getattr(item, 'cost', None), int):
            return int(item.cost)
        return 0

    def buy_item_logic(self, row: int):
        """Common logic for buying an item (uses shared BoltacShop when available)"""
        item_name: str = self.buy_table.item(row, 0).text()
        item: Equipment = [c for c in self.equipment_list if c.name == item_name][0]
        shop = None
        if BOLTAC_SHOP_AVAILABLE:
            try:
                shop = get_boltac_shop()
            except Exception:
                shop = None

        # Determine gp cost
        gp_cost = self._get_gp_cost(item)

        # Check funds
        if self.selected_char.gold < gp_cost:
            # insufficient funds - should not happen if UI disabled correctly
            return

        # If it's a magic item with limited stock, ask shop to buy
        is_limited = False
        if shop is not None and hasattr(item, 'index') and item.index in shop.magic_stock:
            is_limited = True

        if is_limited:
            if not shop.buy_item(item, quantity=1):
                # out of stock
                return

        # Add to character inventory
        inventory = list(filter(None, self.selected_char.inventory))
        min_slot: int = min([i for i, it in enumerate(self.selected_char.inventory) if it is None])
        # deep copy for non-magical unlimited items to avoid shared refs
        from copy import deepcopy
        self.selected_char.inventory[min_slot] = deepcopy(item)
        self.selected_char.gold -= gp_cost
        save_character(char=self.selected_char, _dir=self.characters_dir)
        save_party(self.party, get_save_game_path())
        self.populate_sell_table(char=self.selected_char)
        # refresh buy table if limited stock changed
        if is_limited and shop is not None:
            self.populate_buy_table(self.selected_char)

    def sell_item_logic(self, row: int):
        """Common logic for selling an item (uses shared BoltacShop when available)"""
        item_name: str = self.sell_table.item(row, 0).text()
        item: Equipment = [c for c in self.selected_char.inventory if c and c.name == item_name][0]
        shop = None
        if BOLTAC_SHOP_AVAILABLE:
            try:
                shop = get_boltac_shop()
            except Exception:
                shop = None

        # compute sell price: default quarter of gp value in cp
        cost_value = 0
        if hasattr(item, 'cost') and hasattr(item.cost, 'quantity'):
            cost_value = int(item.cost.quantity)
        elif hasattr(item, 'cost') and hasattr(item.cost, 'value'):
            cost_value = int(item.cost.value) // 100
        elif isinstance(getattr(item, 'cost', None), int):
            cost_value = int(item.cost)

        sell_price_cp = cost_value * 100 // 4 if cost_value else 0

        # Give gold to character and remove from inventory
        slot: int = self.selected_char.inventory.index(item)
        self.selected_char.inventory[slot] = None
        self.selected_char.gold += sell_price_cp / 100

        # If shop available, record player-sold item in shop (shop accepts everything)
        if shop is not None:
            try:
                shop.sell_item(item, sell_price_cp=int(sell_price_cp))
            except Exception:
                pass

        self.sell_table.removeRow(row)
        save_character(char=self.selected_char, _dir=self.characters_dir)
        save_party(self.party, get_save_game_path())

    def disable_sell_button(self):
        self.ui.sellButton.setEnabled(False)
        self.ui.buyButton.setEnabled(True)

    def disable_buy_button(self):
        self.ui.buyButton.setEnabled(False)
        self.ui.sellButton.setEnabled(True)

    @pyqtSlot()  # For button click
    def pool_gold(self):
        self.selected_char.gold = sum([c.gold for c in self.party])
        for c in self.party:
            if c != self.selected_char:
                c.gold = 0
            save_character(char=c, _dir=self.characters_dir)
        self.ui.character_label.setText(f'{self.selected_char.name} - Gold: {self.selected_char.gold:g} gp')

    @pyqtSlot()  # For button click
    def divvy_gold(self):
        total_gold: int = sum([c.gold for c in self.party])
        for c in self.party:
            c.gold = total_gold / len(self.party)
            save_character(char=c, _dir=self.characters_dir)
        self.ui.character_label.setText(f'{self.selected_char.name} - Gold: {self.selected_char.gold:g} gp')

    @pyqtSlot()  # For button click
    def leave_boltac(self):
        self.boltacFrame.close()
        save_party(self.party, get_save_game_path())
        update_buttons(frame=self.castle_ui.nav_frame, enabled=True)

