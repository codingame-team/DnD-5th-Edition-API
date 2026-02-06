"""
Boltac's Trading Post - Shared Inventory System
Persistent shop inventory that can be shared across all frontends
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
from dnd_5e_core.equipment import Equipment, Weapon, Armor
from dnd_5e_core.equipment import get_magic_item, get_special_weapon, get_special_armor
from dnd_5e_core.equipment import MAGIC_ITEMS_REGISTRY, SPECIAL_WEAPONS, SPECIAL_ARMORS


class BoltacInventory:
    """
    Manages Boltac's shop inventory with persistence.

    The shop has:
    - A base stock of standard weapons and armors (always available)
    - A special inventory of items bought from players
    - Magic items that can appear based on shop level
    """

    def __init__(self, save_dir: str = None):
        """
        Initialize Boltac's inventory.

        Args:
            save_dir: Directory where shop inventory is saved
        """
        if save_dir is None:
            # Default to user's save game directory
            from tools.common import get_save_game_path
            save_dir = os.path.join(get_save_game_path(), 'shop')

        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

        self.inventory_file = os.path.join(save_dir, 'boltac_inventory.pkl')

        # Shop inventory
        self.player_sold_items: List[Equipment] = []  # Items sold by players
        self.magic_items_available: List[str] = []    # Magic item indices available
        self.shop_gold: int = 10000  # Shop's gold for buying from players
        self.shop_level: int = 1     # Shop level (unlocks better items)

        # Load existing inventory if it exists
        self.load()

    def load(self) -> bool:
        """
        Load shop inventory from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.inventory_file):
            # Initialize with some default magic items for new shop
            self._initialize_default_inventory()
            return False

        try:
            with open(self.inventory_file, 'rb') as f:
                data = pickle.load(f)
                self.player_sold_items = data.get('player_sold_items', [])
                self.magic_items_available = data.get('magic_items_available', [])
                self.shop_gold = data.get('shop_gold', 10000)
                self.shop_level = data.get('shop_level', 1)
            return True
        except Exception as e:
            print(f"Error loading shop inventory: {e}")
            self._initialize_default_inventory()
            return False

    def save(self) -> bool:
        """
        Save shop inventory to file.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            data = {
                'player_sold_items': self.player_sold_items,
                'magic_items_available': self.magic_items_available,
                'shop_gold': self.shop_gold,
                'shop_level': self.shop_level,
            }
            with open(self.inventory_file, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving shop inventory: {e}")
            return False

    def _initialize_default_inventory(self):
        """Initialize shop with default magic items based on shop level"""
        # Start with some basic potions and common items
        # Stock: 5 for common potions, 1 for magic items
        self.magic_items_available = {
            'potion-of-healing': 5,  # Common potions have more stock
            'antitoxin': 3,
            'rope-of-climbing': 1,  # Magic items have stock of 1
        }

        if self.shop_level >= 2:
            self.magic_items_available.update({
                'potion-of-greater-healing': 3,
                'cloak-of-protection': 1,
            })

        if self.shop_level >= 3:
            self.magic_items_available.update({
                'ring-of-protection': 1,
                'wand-of-magic-missiles': 1,
            })

    def add_sold_item(self, item: Equipment):
        """
        Add an item sold by a player to the shop inventory.

        Args:
            item: Equipment item sold by player
        """
        self.player_sold_items.append(item)
        self.save()

    def remove_sold_item(self, item: Equipment) -> bool:
        """
        Remove a sold item from shop (when bought back).

        Args:
            item: Equipment item to remove

        Returns:
            True if removed successfully
        """
        if item in self.player_sold_items:
            self.player_sold_items.remove(item)
            self.save()
            return True
        return False

    def add_magic_item(self, item_index: str):
        """
        Add a magic item to shop inventory.

        Args:
            item_index: Index of magic item to add
        """
        self.magic_items_available.append(item_index)
        self.save()

    def remove_magic_item(self, item_index: str) -> bool:
        """
        Remove a magic item from shop (when bought).

        Args:
            item_index: Index of magic item to remove

        Returns:
            True if removed successfully
        """
        if item_index in self.magic_items_available:
            self.magic_items_available.remove(item_index)
            self.save()
            return True
        return False

    def get_all_available_items(self) -> List[Tuple[Equipment, int]]:
        """
        Get all items available for purchase (sold items + magic items).

        Returns:
            List of tuples (equipment, stock_count) where stock_count is -1 for unlimited
        """
        all_items = []

        # Add player-sold items (always have stock of 1)
        for item in self.player_sold_items:
            all_items.append((item, 1))

        # Add magic items with stock
        for item_index, stock in self.magic_items_available.items():
            if stock > 0:
                item = get_magic_item(item_index)
                if not item:
                    item = get_special_weapon(item_index)
                if not item:
                    item = get_special_armor(item_index)
                if item:
                    all_items.append((item, stock))

        return all_items

    def buy_from_player(self, item: Equipment, sell_price: int) -> bool:
        """
        Buy an item from a player.

        Args:
            item: Item to buy
            sell_price: Price to pay (in copper pieces)

        Returns:
            True if shop has enough gold and purchase successful
        """
        if self.shop_gold >= sell_price:
            self.shop_gold -= sell_price
            self.add_sold_item(item)
            return True
        return False

    def sell_to_player(self, item: Equipment, buy_price: int) -> bool:
        """
        Sell an item to a player.

        Args:
            item: Item to sell
            buy_price: Price player pays (in copper pieces)

        Returns:
            True if sale successful
        """
        self.shop_gold += buy_price

        # Remove from inventory
        if item in self.player_sold_items:
            self.remove_sold_item(item)
        elif hasattr(item, 'index'):
            self.remove_magic_item(item.index)

        return True

    def restock_magic_items(self, num_items: int = 3, shop_tier: int = 1):
        """
        Restock shop with new magic items.

        Args:
            num_items: Number of items to add
            shop_tier: Shop tier (1-4) determines item quality
        """
        import random

        # Determine available items by tier
        # Include magic armors and weapons
        tier_items = {
            1: ['potion-of-healing', 'antitoxin', 'rope-of-climbing', 'bag-of-holding'],
            2: ['potion-of-greater-healing', 'ring-of-protection', 'cloak-of-protection', 'wand-of-magic-missiles'],
            3: ['potion-of-superior-healing', 'ring-of-spell-storing', 'wand-of-fireballs', 'bracers-of-defense'],
            4: ['potion-of-supreme-healing', 'ring-of-regeneration', 'belt-of-giant-strength'],
        }

        # Add special armors to tier items
        if shop_tier >= 2:
            # Add some magic armors from SPECIAL_ARMORS
            for armor_index in list(SPECIAL_ARMORS.keys())[:3]:
                tier_items[2].append(armor_index)

        if shop_tier >= 3:
            # Add more magic armors
            for armor_index in list(SPECIAL_ARMORS.keys())[3:6]:
                tier_items[3].append(armor_index)

        available = tier_items.get(shop_tier, tier_items[1])

        for _ in range(num_items):
            item_idx = random.choice(available)
            # Add with stock of 1 for magic items, 3 for potions
            quantity = 3 if 'potion' in item_idx else 1
            self.add_magic_item(item_idx, quantity)

    def upgrade_shop(self):
        """Upgrade shop level (unlocks better items)"""
        if self.shop_level < 4:
            self.shop_level += 1
            self.restock_magic_items(num_items=5, shop_tier=self.shop_level)
            self.save()


# Global shop instance (singleton pattern)
_global_shop: Optional[BoltacInventory] = None


def get_boltac_shop(save_dir: str = None) -> BoltacInventory:
    """
    Get the global Boltac shop instance (singleton).

    Args:
        save_dir: Directory for shop saves (optional)

    Returns:
        BoltacInventory instance
    """
    global _global_shop
    if _global_shop is None:
        _global_shop = BoltacInventory(save_dir)
    return _global_shop


def reset_boltac_shop():
    """Reset the global shop instance (for testing)"""
    global _global_shop
    _global_shop = None


__all__ = [
    'BoltacInventory',
    'get_boltac_shop',
    'reset_boltac_shop',
]
