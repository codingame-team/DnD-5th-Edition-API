"""
Game-specific wrapper for dnd-5e-core entities
Adds positioning and rendering capabilities for pygame without polluting core classes
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Union

# Import core entities from dnd-5e-core
from dnd_5e_core.entities import Character, Monster
from dnd_5e_core.equipment import Weapon, Armor, Potion

# Type variable for the wrapped entity
T = TypeVar('T', Character, Monster, Weapon, Armor, Potion)


@dataclass
class GameEntity(Generic[T]):
    """
    Wrapper for dnd-5e-core entities that adds game-specific positioning.

    This uses the Composition pattern instead of inheritance to keep
    the core business logic (Character, Monster, etc.) independent
    from the presentation layer (pygame positioning and rendering).

    Pattern: Adapter/Wrapper
    - Core entity: Character, Monster, Weapon, Armor, Potion
    - Game layer: Adds x, y, image_name, etc.
    """
    entity: T  # The core business entity
    x: int = 0
    y: int = 0
    old_x: int = 0
    old_y: int = 0
    image_name: Optional[str] = None
    id: int = -1

    @property
    def pos(self) -> tuple[int, int]:
        """Current position as (x, y) tuple"""
        return self.x, self.y

    @property
    def old_pos(self) -> tuple[int, int]:
        """Previous position as (x, y) tuple"""
        return self.old_x, self.old_y

    def move(self, dx: int, dy: int):
        """Move entity by delta x and delta y"""
        self.old_x, self.old_y = self.x, self.y
        self.x += dx
        self.y += dy

    def set_position(self, x: int, y: int):
        """Set absolute position"""
        self.old_x, self.old_y = self.x, self.y
        self.x, self.y = x, y

    def check_collision(self, other: 'GameEntity') -> bool:
        """Check if this entity collides with another"""
        return self.x == other.x and self.y == other.y

    def draw(self, screen, image, tile_size: int, vp_x: int, vp_y: int, vp_width: int, vp_height: int):
        """
        Draw the entity on the pygame screen.

        Args:
            screen: Pygame screen surface
            image: Pygame surface to draw
            tile_size: Size of each tile in pixels
            vp_x: Viewport X offset
            vp_y: Viewport Y offset
            vp_width: Viewport width in tiles
            vp_height: Viewport height in tiles
        """
        # Calculate screen position based on viewport
        screen_x = (self.x - vp_x) * tile_size
        screen_y = (self.y - vp_y) * tile_size

        # Draw the image at the calculated position
        screen.blit(image, (screen_x, screen_y))

    def __repr__(self):
        return f"GameEntity({self.entity}, pos=({self.x}, {self.y}))"

    def __getattr__(self, name: str):
        """
        Delegate attribute access to the wrapped entity.

        This allows transparent access to all attributes of the wrapped
        Character, Monster, Weapon, etc. without having to define them all.

        Example:
            hero = GameEntity(entity=character, x=10, y=20)
            hero.class_type  # Automatically delegates to character.class_type
            hero.hit_points  # Automatically delegates to character.hit_points
        """
        # Avoid infinite recursion
        if name == 'entity':
            raise AttributeError(f"'GameEntity' object has no attribute '{name}'")

        # Delegate to the wrapped entity
        return getattr(self.entity, name)

    def __setattr__(self, name: str, value):
        """
        Delegate attribute setting to the wrapped entity.

        This ensures that when methods like drink() modify hit_points,
        the change is applied to the wrapped Character object, not the GameEntity wrapper.

        GameEntity's own attributes (x, y, id, image_name, entity) are handled normally.
        All other attributes are delegated to the wrapped entity.
        """
        # GameEntity's own attributes - set directly on self
        if name in ('x', 'y', 'old_x', 'old_y', 'id', 'image_name', 'entity'):
            object.__setattr__(self, name, value)
        else:
            # Delegate to the wrapped entity
            if hasattr(self, 'entity'):
                setattr(self.entity, name, value)
            else:
                # During __init__, entity doesn't exist yet
                object.__setattr__(self, name, value)

    # Delegate common attributes to the wrapped entity
    @property
    def name(self) -> str:
        """Get name from wrapped entity"""
        return self.entity.name if hasattr(self.entity, 'name') else "Unknown"

    @property
    def is_alive(self) -> property | bool:
        """Check if entity is alive (for Character/Monster)"""
        if hasattr(self.entity, 'is_alive'):
            return self.entity.is_alive
        if hasattr(self.entity, 'hit_points'):
            return self.entity.hit_points > 0
        return True


# Convenience type aliases for common game entities
GameCharacter = GameEntity[Character]
GameMonster = GameEntity[Monster]
GameWeapon = GameEntity[Weapon]
GameArmor = GameEntity[Armor]
GamePotion = GameEntity[Potion]
GameItem = GameEntity  # Generic item (weapon, armor, potion in dungeon)


def create_game_character(character: Character, x: int = 0, y: int = 0,
                         image_name: Optional[str] = None, char_id: int = -1) -> GameCharacter:
    """Factory function to create a positionable game character"""
    return GameEntity(entity=character, x=x, y=y, image_name=image_name, id=char_id)


def create_game_monster(monster: Monster, x: int = 0, y: int = 0,
                       image_name: Optional[str] = None, monster_id: int = -1) -> GameMonster:
    """Factory function to create a positionable game monster"""
    return GameEntity(entity=monster, x=x, y=y, image_name=image_name, id=monster_id)


def create_game_weapon(weapon: Weapon, x: int = 0, y: int = 0,
                      image_name: Optional[str] = None, item_id: int = -1) -> GameWeapon:
    """Factory function to create a positionable game weapon"""
    return GameEntity(entity=weapon, x=x, y=y, image_name=image_name, id=item_id)


def create_game_armor(armor: Armor, x: int = 0, y: int = 0,
                     image_name: Optional[str] = None, item_id: int = -1) -> GameArmor:
    """Factory function to create a positionable game armor"""
    return GameEntity(entity=armor, x=x, y=y, image_name=image_name, id=item_id)


def create_game_potion(potion: Potion, x: int = 0, y: int = 0,
                      image_name: Optional[str] = None, item_id: int = -1) -> GamePotion:
    """Factory function to create a positionable game potion"""
    return GameEntity(entity=potion, x=x, y=y, image_name=image_name, id=item_id)


# Aliases for dungeon-specific naming (backward compatibility)
create_dungeon_character = create_game_character
create_dungeon_monster = create_game_monster
create_dungeon_item = create_game_weapon  # Generic item creator
