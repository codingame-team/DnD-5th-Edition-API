from __future__ import annotations

from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from dao_classes import Character, Spell, Equipment, Potion, Cost


class StringTableItem(QTableWidgetItem):
    def __lt__(self, other):
        return self.text().lower() < other.text().lower()


class IntegerTableItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return int(self.text()) < int(other.text())
        except ValueError:
            return super().__lt__(other)


class ClassTableItem(QTableWidgetItem):
    CLASS_ORDER = {
        "fighter": 1,
        "paladin": 2,
        "barbarian": 3,
        "ranger": 4,
        "rogue": 5,
        "cleric": 6,
        "druid": 7,
        "bard": 8,
        "monk": 9,
        "warlock": 10,
        "wizard": 11,
        "sorcerer": 12,
    }

    def __lt__(self, other):
        this_order = self.CLASS_ORDER.get(self.text(), 999)
        other_order = self.CLASS_ORDER.get(other.text(), 999)
        return (
            this_order < other_order
            if this_order != other_order
            else self.text().lower() < other.text().lower()
        )


class CostTableItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            # Convert the text values back to their copper piece equivalents
            this_text = self.text().split()
            other_text = other.text().split()

            if len(this_text) != 2 or len(other_text) != 2:
                return super().__lt__(other)

            this_quantity = int(this_text[0])
            this_unit = this_text[1]

            other_quantity = int(other_text[0])
            other_unit = other_text[1]

            # Recreate Cost objects to use their value property
            this_cost = Cost(this_quantity, this_unit)
            other_cost = Cost(other_quantity, other_unit)

            return this_cost.value < other_cost.value
        except (ValueError, IndexError):
            return super().__lt__(other)


def populate_spell_row(table: QTableWidget, spell: Spell, row: int) -> None:
    """Populate a single row with spell data."""
    column_items = [
        (spell.name, StringTableItem),
        (spell.level, IntegerTableItem),
        (spell.school, StringTableItem),
        (spell.range, StringTableItem),
    ]

    for col, (value, item_type) in enumerate(column_items):
        item = item_type(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)

    # Sort by level column (column index 1) in ascending order
    table.sortItems(1, Qt.SortOrder.AscendingOrder)


def populate_character_row(table: QTableWidget, char: Character, row: int) -> None:
    """Populate a single row with character data using appropriate sorting types."""
    column_items = [
        (char.name, StringTableItem),
        (char.class_type, ClassTableItem),
        (char.race, StringTableItem),
        (char.armor_class, IntegerTableItem),
        (char.hit_points, IntegerTableItem),
        (char.max_hit_points, IntegerTableItem),
        ("Alive" if char.hit_points > 0 else "DEAD", StringTableItem),
    ]

    for col, (value, item_type) in enumerate(column_items):
        item = item_type(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)


def populate_table(table: QTableWidget, training_grounds: List[Character]) -> None:
    """Populate the entire table with character data."""
    table.setRowCount(len(training_grounds))
    for i, char in enumerate(training_grounds):
        populate_character_row(table, char, i)
    table.adjustSize()
    table.setSortingEnabled(True)


def populate_spell_table(table: QTableWidget, spells: List[Spell]) -> None:
    """Populate the entire table with spell data."""
    table.setRowCount(len(spells))
    for i, spell in enumerate(spells):
        populate_spell_row(table, spell, i)
    table.adjustSize()
    table.setSortingEnabled(True)


def updateCharItem(table: QTableWidget, char: Character, char_index: int) -> None:
    """
    Update an existing character's data in the table.

    Args:
        table: QTableWidget containing character data
        char: Character object with updated data
        char_index: Row index of the character to update
    """
    if char_index < 0 or char_index >= table.rowCount():
        return  # Invalid index, do nothing

    # Reuse the populate_character_row function to update the row
    populate_character_row(table, char, char_index)


def addCharItem(table: QTableWidget, char: Character, char_list: List[Character]) -> None:
    """Add a new character to the table."""
    new_row = len(char_list)
    table.setRowCount(new_row + 1)
    populate_character_row(table, char, new_row)


def addSpellItem(table: QTableWidget, spell: Spell, spell_list: List[Spell]) -> None:
    """Add a new spell to the table."""
    new_row = len(spell_list)
    table.setRowCount(new_row + 1)
    populate_spell_row(table, spell, new_row)


def populate_equipment_row(
    table: QTableWidget,
    item: Equipment | Potion,
    row: int,
    for_sale: bool = False,
    selectable: bool = True,
):
    if not item:
        return
    item_price = item.cost if not for_sale else Cost(item.cost.quantity // 2, item.cost.unit)
    column_items = [
        (item.name, StringTableItem),
        # (item_price, IntegerTableItem),
        (str(item_price), CostTableItem),  # Changed to use CostTableItem
        (type(item).__name__, StringTableItem),
    ]

    for col, (value, item_type) in enumerate(column_items):
        item = item_type(str(value))
        if not selectable:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setForeground(QBrush(Qt.GlobalColor.gray))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)


def addItem(
    table: QTableWidget,
    item: Equipment | Potion,
    row: int,
    for_sale: bool = False,
    selectable: bool = True,
) -> None:
    """Add a new item to the table."""
    populate_equipment_row(table, item, row, for_sale, selectable)
