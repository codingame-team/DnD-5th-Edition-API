"""
PyQt UI Models for Combat Actions
Specific to the PyQt frontend - not part of dnd-5e-core
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from dnd_5e_core.entities import Character, Monster
    from dnd_5e_core.spells import Spell


class CharActionType(Enum):
    """
    Types of actions a character can take in combat (PyQt UI specific).
    """
    MELEE_ATTACK = "Attack"
    RANGED_ATTACK = "Attack"
    SPELL_ATTACK = "Spell"
    SPELL_DEFENSE = "spell_defense"
    PARRY = "Parry"


@dataclass
class CharAction:
    """
    Represents a character's action in combat (PyQt UI specific).
    Used for UI state management in the combat module.
    """
    type: CharActionType
    spell: Optional['Spell'] = field(default=None)
    targets: Optional[List['Character' | 'Monster']] = field(default_factory=list)

    def __repr__(self):
        return f"{self.type.value} - {self.spell.name if self.spell else ''} - {self.targets[0].name if self.targets else ''}"

