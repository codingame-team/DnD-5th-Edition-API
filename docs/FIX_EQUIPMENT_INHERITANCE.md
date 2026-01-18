# ✅ CORRECTION HÉRITAGE - Armor et Weapon héritent d'Equipment

**Date :** 26 décembre 2025  
**Problème :** Les classes Armor et Weapon ne héritaient plus d'Equipment

---

## ❌ Problème Identifié

Lors de la migration précédente, les classes `ArmorData` et `WeaponData` avaient été transformées en dataclasses indépendantes au lieu d'hériter d'`Equipment`.

### Avant (Incorrect)

**armor.py :**
```python
@dataclass
class ArmorData:
    # ❌ N'héritait pas d'Equipment
    index: str
    name: str
    armor_class: Dict
    # ... attributs Equipment dupliqués
    category: Optional['EquipmentCategory'] = None
    cost: Optional['Cost'] = None
    weight: float = 0.0
    desc: Optional[str] = None
    equipped: bool = False
```

**weapon.py :**
```python
@dataclass
class WeaponData:
    # ❌ N'héritait pas d'Equipment
    index: str
    name: str
    properties: List[WeaponProperty]
    # ... attributs Equipment dupliqués
    category: Optional['Equipment'] = None
    cost: Optional['Equipment'] = None
    weight: float = 0.0
    desc: Optional[str] = None
    equipped: bool = False
```

**Problèmes :**
- ❌ Duplication des attributs Equipment (category, cost, weight, desc, equipped)
- ❌ Pas de relation hiérarchique
- ❌ `isinstance(armor, Equipment)` retournait False
- ❌ Violation du principe DRY

---

## ✅ Correction Appliquée

### 1. ArmorData hérite d'Equipment

**Fichier :** `dnd-5e-core/dnd_5e_core/equipment/armor.py`

```python
from .equipment import Equipment, Cost, EquipmentCategory

@dataclass
class ArmorData(Equipment):
    """
    Armor data structure for D&D 5e armor.
    
    Inherits from Equipment for inventory management.
    For pygame positioning, use GameEntity wrapper.
    """
    # Armor-specific attributes only
    armor_class: Dict = field(default_factory=dict)
    str_minimum: int = 0
    stealth_disadvantage: bool = False
    
    # ✅ index, name, cost, weight, desc, category, equipped
    #    sont hérités d'Equipment !
```

### 2. WeaponData hérite d'Equipment

**Fichier :** `dnd-5e-core/dnd_5e_core/equipment/weapon.py`

```python
from .equipment import Equipment

@dataclass
class WeaponData(Equipment):
    """
    Weapon data structure for D&D 5e weapons.
    
    Inherits from Equipment for inventory management.
    For pygame positioning, use GameEntity wrapper.
    """
    # Weapon-specific attributes only
    properties: List[WeaponProperty] = field(default_factory=list)
    damage_type: Optional[DamageType] = None
    range_type: Optional[RangeType] = None
    category_type: Optional[CategoryType] = None
    damage_dice: Optional['DamageDice'] = None
    damage_dice_two_handed: Optional['DamageDice'] = None
    weapon_range: Optional[WeaponRange] = None
    throw_range: Optional[WeaponThrowRange] = None
    is_magic: bool = False
    
    # Computed fields
    range: Optional[WeaponRange] = field(default=None, init=False)
    category_range: str = field(default='', init=False)
    
    # ✅ index, name, cost, weight, desc, category, equipped
    #    sont hérités d'Equipment !
```

---

## 📊 Hiérarchie Corrigée

```
Equipment (base class)
  ├─ index: str
  ├─ name: str
  ├─ cost: Cost
  ├─ weight: int
  ├─ desc: Optional[List[str]]
  ├─ category: EquipmentCategory
  └─ equipped: bool
  
    ↓ hérite
    
ArmorData(Equipment)
  ├─ [hérite tous les attributs Equipment]
  ├─ armor_class: Dict
  ├─ str_minimum: int
  └─ stealth_disadvantage: bool
  
    ↓ hérite
    
WeaponData(Equipment)
  ├─ [hérite tous les attributs Equipment]
  ├─ properties: List[WeaponProperty]
  ├─ damage_type: DamageType
  ├─ range_type: RangeType
  ├─ category_type: CategoryType
  ├─ damage_dice: DamageDice
  └─ ... (autres attributs weapon-specific)
```

---

## ✅ Avantages de la Correction

### 1. Hiérarchie Correcte
- ✅ `isinstance(armor, Equipment)` → True
- ✅ `isinstance(weapon, Equipment)` → True
- ✅ Polymorphisme fonctionnel

### 2. Pas de Duplication
- ✅ Attributs Equipment définis une seule fois
- ✅ Respect du principe DRY
- ✅ Maintenance simplifiée

### 3. Cohérence
- ✅ Tous les équipements héritent d'Equipment
- ✅ Architecture logique et intuitive
- ✅ Conforme aux principes OOP

### 4. Extensibilité
- ✅ Facile d'ajouter d'autres types d'équipement
- ✅ Méthodes Equipment disponibles pour Armor et Weapon
- ✅ `price`, `sell_price` automatiquement disponibles

---

## 🧪 Tests de Validation

### Test 1 : Héritage
```python
from dnd_5e_core.equipment import Equipment, Armor, Weapon

armor = request_armor('chain-mail')
weapon = request_weapon('longsword')

✅ isinstance(armor, Equipment) → True
✅ isinstance(weapon, Equipment) → True
✅ isinstance(armor, Armor) → True
✅ isinstance(weapon, Weapon) → True
```

### Test 2 : Attributs Hérités
```python
armor = request_armor('chain-mail')
✅ armor.index → 'chain-mail'
✅ armor.name → 'Chain Mail'
✅ armor.cost → Cost(...)
✅ armor.weight → 55
✅ armor.category → EquipmentCategory(...)
✅ armor.equipped → False
```

### Test 3 : Attributs Spécifiques
```python
armor = request_armor('chain-mail')
✅ armor.armor_class → {'base': 16, ...}
✅ armor.base_ac → 16
✅ armor.str_minimum → 13
✅ armor.stealth_disadvantage → True

weapon = request_weapon('longsword')
✅ weapon.damage_dice → DamageDice('1d8')
✅ weapon.category_type → CategoryType.MARTIAL
✅ weapon.range_type → RangeType.MELEE
✅ weapon.category_range → 'Martial Melee'
```

### Test 4 : Méthodes Héritées
```python
armor = request_armor('chain-mail')
✅ armor.price → 15000 (en copper)
✅ armor.sell_price → 7500 (half price)
✅ armor.__hash__() → hash(armor.index)
```

---

## 📝 Fichiers Modifiés

### dnd-5e-core
1. ✅ `equipment/armor.py`
   - ArmorData hérite d'Equipment
   - Retrait attributs dupliqués
   - Import Equipment ajouté

2. ✅ `equipment/weapon.py`
   - WeaponData hérite d'Equipment
   - Retrait attributs dupliqués
   - Import Equipment ajouté
   - Ajout default values pour Optional fields

---

## 🎯 Architecture Finale

### Equipment (Base)
```python
@dataclass
class Equipment:
    """Base class for all equipment"""
    index: str
    name: str
    cost: Cost
    weight: int
    desc: Optional[List[str]]
    category: EquipmentCategory
    equipped: bool
```

### Armor (Spécialisé)
```python
@dataclass
class ArmorData(Equipment):
    """Armor with AC calculation"""
    # Hérite: index, name, cost, weight, desc, category, equipped
    armor_class: Dict
    str_minimum: int
    stealth_disadvantage: bool
```

### Weapon (Spécialisé)
```python
@dataclass
class WeaponData(Equipment):
    """Weapon with damage and properties"""
    # Hérite: index, name, cost, weight, desc, category, equipped
    properties: List[WeaponProperty]
    damage_type: DamageType
    range_type: RangeType
    category_type: CategoryType
    damage_dice: DamageDice
    # ... autres attributs weapon
```

---

## ✅ CORRECTION COMPLÈTE

**Résultat :**
- ✅ Armor et Weapon héritent correctement d'Equipment
- ✅ Pas de duplication d'attributs
- ✅ Hiérarchie OOP correcte
- ✅ Tests passés
- ✅ main.py fonctionne
- ✅ Architecture cohérente

**Principe respecté : Single Responsibility + DRY**

---

**Date :** 26 décembre 2025  
**Status :** ✅ CORRIGÉ  
**Impact :** Architecture OOP correcte et maintenable

