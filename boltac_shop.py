"""
Boltac's Trading Post - Shared Shop Management System
Persistent shop with inventory based on dnd-5e-core loader
"""
import os
import pickle
import sys
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add dnd-5e-core to path if in development mode
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)

# Import from dnd-5e-core
from dnd_5e_core.equipment import Equipment, Weapon, Armor, MagicItem
from dnd_5e_core.data.loader import (
    list_equipment, list_weapons, list_armors,
    load_equipment, load_weapon, load_armor
)
from dnd_5e_core.equipment import (
    get_magic_item, get_special_weapon, get_special_armor,
    MAGIC_ITEMS_REGISTRY, SPECIAL_WEAPONS, SPECIAL_ARMORS
)


class BoltacShop:
    """
    Manages Boltac's Trading Post with persistent inventory.

    Features:
    - Loads catalog from dnd-5e-core loader
    - Unlimited stock for non-magical items
    - Limited stock (starting at 1) for magical items
    - Persistent storage in shared save directory
    - Items sold by players are added to inventory
    """

    def __init__(self, save_dir: str = None):
        """
        Initialize Boltac's shop.

        Args:
            save_dir: Directory for shop saves (default: Saved_Games_DnD_5th/shop)
        """
        if save_dir is None:
            from tools.common import get_save_game_path
            save_dir = os.path.join(get_save_game_path(), 'shop')

        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

        self.inventory_file = os.path.join(save_dir, 'boltac_shop.pkl')

        # Inventory data structures
        self.magic_stock: Dict[str, int] = {}  # Magic item index -> stock count
        self.player_items: List[Equipment] = []  # Items sold by players
        self.shop_gold: int = 10000  # Shop's purchasing power
        self.shop_level: int = 1  # Shop tier (unlocks better items)

        # Cache for loaded items (avoid reloading from disk)
        self._catalog_cache: Dict[str, Equipment] = {}

        # Load saved state
        self.load()

    def load(self) -> bool:
        """
        Load shop state from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.inventory_file):
            self._initialize_default_stock()
            return False

        try:
            with open(self.inventory_file, 'rb') as f:
                data = pickle.load(f)
                self.magic_stock = data.get('magic_stock', {})
                self.player_items = data.get('player_items', [])
                self.shop_gold = data.get('shop_gold', 10000)
                self.shop_level = data.get('shop_level', 1)
            # Clean unknown magic_stock keys to avoid collisions with loader indices
            try:
                from dnd_5e_core.equipment.magic_item_factory import MAGIC_ITEMS_REGISTRY
                from dnd_5e_core.equipment.weapon_factory import SPECIAL_WEAPONS
                from dnd_5e_core.equipment.armor_factory import SPECIAL_ARMORS
                valid_keys = set(MAGIC_ITEMS_REGISTRY.keys()) | set(SPECIAL_WEAPONS.keys()) | set(SPECIAL_ARMORS.keys())
                unknown_keys = [k for k in list(self.magic_stock.keys()) if k not in valid_keys]
                if unknown_keys:
                    for k in unknown_keys:
                        # remove dubious keys silently
                        del self.magic_stock[k]
                    # persist cleaned state
                    with open(self.inventory_file, 'wb') as f2:
                        pickle.dump({'magic_stock': self.magic_stock, 'player_items': self.player_items, 'shop_gold': self.shop_gold, 'shop_level': self.shop_level}, f2)
            except Exception:
                # If registries cannot be inspected, keep existing magic_stock as-is
                pass
            return True
        except Exception as e:
            print(f"Error loading shop: {e}")
            self._initialize_default_stock()
            return False

    def save(self) -> bool:
        """
        Save shop state to file.

        Returns:
            True if saved successfully
        """
        try:
            data = {
                'magic_stock': self.magic_stock,
                'player_items': self.player_items,
                'shop_gold': self.shop_gold,
                'shop_level': self.shop_level,
            }
            with open(self.inventory_file, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving shop: {e}")
            return False

    def _initialize_default_stock(self):
        """Initialize shop with ALL magical items from registries."""
        self.magic_stock = {}

        # 1. Add ALL magic items from MAGIC_ITEMS_REGISTRY (43 items)
        from dnd_5e_core.equipment.magic_item_factory import MAGIC_ITEMS_REGISTRY
        for item_idx in MAGIC_ITEMS_REGISTRY.keys():
            # Higher stock for potions (consumables)
            if 'potion' in item_idx or 'antitoxin' in item_idx or 'elixir' in item_idx or 'oil' in item_idx:
                if 'healing' in item_idx:
                    self.magic_stock[item_idx] = 5  # Healing potions: 5 stock
                else:
                    self.magic_stock[item_idx] = 2  # Other potions: 2 stock
            else:
                self.magic_stock[item_idx] = 1  # Permanent items: 1 stock

        # 2. Add magic weapons (stock: 1 each)
        if SPECIAL_WEAPONS:
            for weapon_idx in SPECIAL_WEAPONS.keys():
                self.magic_stock[weapon_idx] = 1

        # 3. Add magic armors (stock: 1 each)
        if SPECIAL_ARMORS:
            for armor_idx in SPECIAL_ARMORS.keys():
                self.magic_stock[armor_idx] = 1


    def get_all_weapons(self) -> List[Weapon]:
        """
        Get all weapons from loader (unlimited stock).

        Returns:
            List of all available weapons
        """
        weapons = []
        for weapon_idx in list_weapons():
            weapon = load_weapon(weapon_idx)
            if weapon:
                weapons.append(weapon)

        # Stable sort: put unlimited-stock items (-1) first, then by name
        weapons.sort(key=lambda w: (self.get_item_stock(w) != -1, getattr(w, 'name', '')))
        return weapons

    def get_all_armors(self) -> List[Armor]:
        """
        Get all armors from loader (unlimited stock).

        Returns:
            List of all available armors
        """
        armors = []
        for armor_idx in list_armors():
            armor = load_armor(armor_idx)
            if armor:
                armors.append(armor)

        # Put unlimited stock armors first
        armors.sort(key=lambda a: (self.get_item_stock(a) != -1, getattr(a, 'name', '')))
        return armors

    def get_all_equipment(self) -> List[Equipment]:
        """
        Get all equipment from loader (unlimited stock).

        Returns:
            List of all available equipment (excluding weapons/armors)
        """
        equipment = []
        for equip_idx in list_equipment():
            item = load_equipment(equip_idx)
            if item and not isinstance(item, (Weapon, Armor)):
                equipment.append(item)

        # Put unlimited stock equipment first
        equipment.sort(key=lambda i: (self.get_item_stock(i) != -1, getattr(i, 'name', '')))
        return equipment

    def get_magic_items_in_stock(self) -> List[Tuple[Equipment, int]]:
        """
        Get all magical items currently in stock.

        Returns:
            List of tuples (item, stock_count)
        """
        items = []
        for item_idx, stock in self.magic_stock.items():
            if stock > 0:
                # Try loading from different sources
                item = get_magic_item(item_idx)
                if not item:
                    item = get_special_weapon(item_idx)
                if not item:
                    item = get_special_armor(item_idx)

                if item:
                    items.append((item, stock))

        return items

    def get_player_sold_items(self) -> List[Tuple[Equipment, int]]:
        """
        Get items sold by players.

        Returns:
            List of tuples (item, stock=1)
        """
        return [(item, 1) for item in self.player_items]

    def get_item_stock(self, item: Equipment) -> int:
        """
        Get stock count for an item.

        Args:
            item: Equipment to check

        Returns:
            Stock count (-1 for unlimited, 0 for out of stock, >0 for limited stock)
        """
        # Player-sold items take precedence
        if item in self.player_items:
            return 1

        # If item has an index and is listed in magic_stock, return stored stock (could be 0)
        if hasattr(item, 'index') and item.index in self.magic_stock:
            return self.magic_stock.get(item.index, 0)

        # Regular items have unlimited stock
        return -1

    def buy_item(self, item: Equipment, quantity: int = 1) -> bool:
        """
        Player buys an item from the shop.

        Args:
            item: Item to buy
            quantity: Number to buy

        Returns:
            True if purchase successful
        """
        stock = self.get_item_stock(item)

        # Unlimited stock items
        if stock == -1:
            return True

        # Limited stock items
        if stock >= quantity:
            if hasattr(item, 'index') and item.index in self.magic_stock:
                self.magic_stock[item.index] -= quantity
                if self.magic_stock[item.index] < 0:
                    self.magic_stock[item.index] = 0
            elif item in self.player_items:
                for _ in range(quantity):
                    if item in self.player_items:
                        self.player_items.remove(item)

            self.save()
            return True

        return False

    def sell_item(self, item: Equipment, sell_price_cp: int) -> bool:
        """
        Player sells an item to the shop.
        Shop has unlimited gold for buying items from players.

        Args:
            item: Item to sell
            sell_price_cp: Sell price in copper pieces

        Returns:
            Always True (shop accepts all items)
        """
        # Shop always accepts items (unlimited gold)
        self.player_items.append(item)
        self.save()
        return True

    def restock_magic_items(self, shop_tier: int = None):
        """
        Restock magical items based on shop tier.

        Args:
            shop_tier: Shop tier (1-4), uses current level if None
        """
        import random

        if shop_tier is None:
            shop_tier = self.shop_level

        tier_items = {
            1: [
                ('potion-of-healing', 5),
                ('antitoxin', 3),
                ('rope-of-climbing', 1),
            ],
            2: [
                ('potion-of-greater-healing', 3),
                ('ring-of-protection', 1),
                ('cloak-of-protection', 1),
                ('wand-of-magic-missiles', 1),
            ],
            3: [
                ('potion-of-superior-healing', 2),
                ('ring-of-spell-storing', 1),
                ('wand-of-fireballs', 1),
                ('bracers-of-defense', 1),
            ],
            4: [
                ('potion-of-supreme-healing', 1),
                ('ring-of-regeneration', 1),
                ('belt-of-giant-strength', 1),
            ],
        }

        # Add items for current tier
        for tier in range(1, min(shop_tier + 1, 5)):
            for item_idx, quantity in tier_items.get(tier, []):
                if item_idx in self.magic_stock:
                    self.magic_stock[item_idx] += quantity
                else:
                    self.magic_stock[item_idx] = quantity

        # Add some special armors at higher tiers
        if shop_tier >= 2:
            armor_indices = list(SPECIAL_ARMORS.keys())[:3]
            for armor_idx in armor_indices:
                if armor_idx not in self.magic_stock:
                    self.magic_stock[armor_idx] = 1

        self.save()

    def upgrade_shop(self):
        """Upgrade shop to next tier."""
        if self.shop_level < 4:
            self.shop_level += 1
            self.restock_magic_items(self.shop_level)
            print(f"Shop upgraded to level {self.shop_level}!")


# Global singleton instance
_shop_instance: Optional[BoltacShop] = None


def get_boltac_shop(save_dir: str = None) -> BoltacShop:
    """
    Get the global Boltac shop instance (singleton).

    Args:
        save_dir: Custom save directory (optional)

    Returns:
        BoltacShop instance
    """
    global _shop_instance
    if _shop_instance is None:
        _shop_instance = BoltacShop(save_dir)
    return _shop_instance


def reset_boltac_shop():
    """Reset the global shop instance (for testing)."""
    global _shop_instance
    _shop_instance = None


__all__ = [
    'BoltacShop',
    'get_boltac_shop',
    'reset_boltac_shop',
]
