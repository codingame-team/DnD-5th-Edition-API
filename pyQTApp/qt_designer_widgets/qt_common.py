from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from dao_classes import Character, Spell


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
        "sorcerer": 12
    }

    def __lt__(self, other):
        this_order = self.CLASS_ORDER.get(self.text(), 999)
        other_order = self.CLASS_ORDER.get(other.text(), 999)
        return (
            this_order < other_order
            if this_order != other_order
            else self.text().lower() < other.text().lower()
        )

def populate_spell_row(table: QTableWidget, spell: Spell, row: int) -> None:
    """Populate a single row with spell data."""
    column_items = [
        (spell.name, StringTableItem),
        (spell.level, IntegerTableItem),
        (spell.school, StringTableItem),
        (spell.range, StringTableItem)
    ]

    for col, (value, item_type) in enumerate(column_items):
        item = item_type(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)

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

def addItem(table: QTableWidget, char: Character, char_list: List[Character]) -> None:
    """Add a new character to the table."""
    new_row = len(char_list)
    table.setRowCount(new_row + 1)
    populate_character_row(table, char, new_row)

def addSpellItem(table: QTableWidget, spell: Spell, spell_list: List[Spell]) -> None:
    """Add a new spell to the table."""
    new_row = len(spell_list)
    table.setRowCount(new_row + 1)
    populate_spell_row(table, spell, new_row)
