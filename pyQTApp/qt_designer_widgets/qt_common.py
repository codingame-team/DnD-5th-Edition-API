from typing import List

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from dao_classes import Character


def populate(table: QTableWidget, training_grounds: List[Character]):
    table.setRowCount(len(training_grounds))
    # table.insertRow(len(training_grounds))
    i = 0
    for char in training_grounds:
        table.setItem(i, 0, QTableWidgetItem(char.name))
        table.setItem(i, 1, QTableWidgetItem(f'{char.class_type}/{char.race}'))
        table.setItem(i, 2, QTableWidgetItem(char.armor_class))
        table.setItem(i, 3, QTableWidgetItem(f'{char.hit_points}/{char.max_hit_points}'))
        status = 'Alive' if char.hit_points > 0 else 'DEAD'
        table.setItem(i, 4, QTableWidgetItem(status))
        i += 1
    table.adjustSize()


def addItem(table: QTableWidget, char: Character, party: List[Character]):
    table.setRowCount(len(party))
    table.insertRow(len(party))
    i = len(party)
    table.setItem(i, 0, QTableWidgetItem(char.name))
    table.setItem(i, 1, QTableWidgetItem(f'{char.class_type}/{char.race}'))
    table.setItem(i, 2, QTableWidgetItem(char.armor_class))
    table.setItem(i, 3, QTableWidgetItem(f'{char.hit_points}/{char.max_hit_points}'))
    status = 'Alive' if char.hit_points > 0 else 'DEAD'
    table.setItem(i, 4, QTableWidgetItem(status))