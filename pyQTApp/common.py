import os
import pickle
import sys
from enum import Enum
from typing import List

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QFrame

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
	sys.path.insert(0, _dnd_5e_core_path)

from dnd_5e_core.entities import Character


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


def load_welcome() -> QPixmap:
    path = os.path.dirname(__file__)
    image_file: str = f"{path}/images/welcome.png"
    pixmap = QPixmap(image_file)
    return pixmap


class color:
    RED = '<span style="color: red">'
    GREEN = '<span style="color: green">'
    END = "</span>"


def update_buttons(frame: QFrame, enabled: bool):
    for widget in frame.findChildren(QPushButton):
        widget.setEnabled(enabled)
