from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from dao_classes import Character

def center_items(row: int, table: QTableWidget):
    for col in range(table.columnCount()):
        item = table.item(row, col)
        if item:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

def setItems(table: QTableWidget, char: Character, row: int):
    table.setItem(row, 0, QTableWidgetItem(char.name))
    table.setItem(row, 1, QTableWidgetItem(str(char.class_type)))
    table.setItem(row, 2, QTableWidgetItem(str(char.race)))
    table.setItem(row, 3, QTableWidgetItem(str(char.armor_class)))
    table.setItem(row, 4, QTableWidgetItem(str(char.hit_points)))
    table.setItem(row, 5, QTableWidgetItem(str(char.max_hit_points)))
    status = 'Alive' if char.hit_points > 0 else 'DEAD'
    table.setItem(row, 6, QTableWidgetItem(status))
    center_items(row, table)

def populate(table: QTableWidget, training_grounds: List[Character]):
    table.setRowCount(len(training_grounds))
    # table.insertRow(len(training_grounds))
    i = 0
    for char in training_grounds:
        setItems(table, char, i)
        i += 1
    table.adjustSize()


def addItem(table: QTableWidget, char: Character, char_list: List[Character]):
    table.setRowCount(len(char_list))
    table.insertRow(len(char_list))
    i = len(char_list)
    setItems(table, char, i)
