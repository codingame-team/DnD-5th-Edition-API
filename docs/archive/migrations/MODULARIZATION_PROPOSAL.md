# Proposition de Modularisation du Projet D&D

## Analyse de la Situation Actuelle

### Projets Existants
1. **DnD-5th-Edition-API** - Projet principal avec multiples versions (console, PyQt5, Tkinter, Pygame, ncurses, 3D)
2. **DnD-5e-ncurses** - Projet séparé avec une version simplifiée ncurses

### Problématiques Identifiées

1. **Duplication de Code**: Les classes de base (Player, Monster, Weapon, Armor, Potion) sont définies plusieurs fois :
   - `/DnD-5th-Edition-API/dao_classes.py` (version complète avec D&D 5e complet)
   - `/DnD-5e-ncurses/entities.py` (version simplifiée)
   - Plusieurs autres fichiers spécifiques (rpg_ncurses.py, rpg_pygame.py, dungeon_tk.py, etc.)

2. **Couplage Fort**: Les classes D&D sont mélangées avec le code de présentation (pygame, curses, tkinter)

3. **Difficultés de Maintenance**: Toute modification des règles D&D doit être répétée dans plusieurs fichiers

4. **Complexité**: Le projet principal contient trop de versions différentes dans un seul repository

## Solution Proposée: Architecture Modulaire

### Structure Recommandée

```
dnd-core/                          # Package Python réutilisable
├── setup.py
├── README.md
├── LICENSE (MIT)
├── dnd_core/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── base.py              # Classes de base (Entity)
│   │   ├── player.py            # Classe Player
│   │   ├── monster.py           # Classe Monster
│   │   └── npc.py               # Classes NPC
│   ├── equipment/
│   │   ├── __init__.py
│   │   ├── weapons.py           # Armes
│   │   ├── armor.py             # Armures
│   │   ├── potions.py           # Potions
│   │   └── items.py             # Items génériques
│   ├── mechanics/
│   │   ├── __init__.py
│   │   ├── combat.py            # Système de combat
│   │   ├── dice.py              # Système de dés
│   │   ├── abilities.py         # Caractéristiques D&D
│   │   └── spells.py            # Système de sorts
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py            # Chargement depuis API
│   │   └── serialization.py    # Save/Load
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # Fonctions utilitaires

dnd-console/                       # Version Console
├── setup.py
├── README.md
├── requirements.txt              # dnd-core + dépendances console
├── main.py
└── ...

dnd-ncurses/                       # Version NCurses
├── setup.py
├── README.md
├── requirements.txt              # dnd-core + curses
├── main.py
├── ui_curses.py
└── ...

dnd-pyqt/                          # Version PyQt5
├── setup.py
├── README.md
├── requirements.txt              # dnd-core + PyQt5
├── wizardry.py
└── pyQTApp/
    └── ...

dnd-pygame/                        # Version Pygame
├── setup.py
├── README.md
├── requirements.txt              # dnd-core + pygame
├── dungeon_pygame.py
└── ...

dnd-tkinter/                       # Version Tkinter
├── setup.py
├── README.md
├── requirements.txt              # dnd-core + tkinter
├── dungeon_tk.py
└── ...
```

### Avantages de Cette Architecture

#### 1. **Réutilisabilité**
- Les classes D&D sont dans un package Python indépendant
- Toutes les versions de jeux utilisent le même package `dnd-core`
- Installation simple: `pip install dnd-core`

#### 2. **Maintenance Simplifiée**
- Une seule source de vérité pour les règles D&D
- Mise à jour centralisée
- Tests unitaires centralisés

#### 3. **Séparation des Préoccupations**
- **dnd-core**: Logique métier pure (règles D&D)
- **dnd-xxx**: Couche présentation (UI/UX)

#### 4. **Évolutivité**
- Facile d'ajouter de nouvelles versions (Web, Mobile, etc.)
- Possibilité de versioning sémantique pour `dnd-core`

#### 5. **Collaboration**
- Différentes équipes peuvent travailler sur différentes versions
- Le core peut être maintenu séparément

### Plan de Migration

#### Phase 1: Créer le Package Core

```bash
# Créer le nouveau repository
mkdir dnd-core
cd dnd-core

# Structure de base
mkdir -p dnd_core/{entities,equipment,mechanics,data,utils}
touch dnd_core/__init__.py
touch dnd_core/entities/{__init__.py,base.py,player.py,monster.py}
touch dnd_core/equipment/{__init__.py,weapons.py,armor.py,potions.py}
touch dnd_core/mechanics/{__init__.py,combat.py,dice.py,abilities.py}
```

**Exemple: dnd_core/entities/base.py**
```python
from dataclasses import dataclass
from abc import ABC, abstractmethod
from random import randint


@dataclass
class Entity(ABC):
    """Classe de base pour toutes les entités D&D"""
    name: str
    hp: int
    max_hp: int

    def attack_roll(self) -> int:
        """Lance 1d20 pour une attaque"""
        return randint(1, 20)

    def is_alive(self) -> bool:
        """Vérifie si l'entité est vivante"""
        return self.hp > 0

    @property
    @abstractmethod
    def armor_class(self) -> int:
        """Classe d'armure de l'entité"""
        pass

    @property
    @abstractmethod
    def damage(self) -> int:
        """Dégâts de base de l'entité"""
        pass

    def attack(self, target: 'Entity') -> int:
        """
        Attaque une autre entité
        Returns: dégâts infligés (0 si raté)
        """
        if self.attack_roll() >= target.armor_class:
            damage = self.damage
            target.hp = max(0, target.hp - damage)
            return damage
        return 0
```

**Exemple: dnd_core/entities/player.py**
```python
from dataclasses import dataclass, field
from typing import List, Optional
from .base import Entity
from ..equipment import Weapon, Armor, Potion


@dataclass
class Player(Entity):
    """Joueur D&D avec inventaire et équipement"""
    gold: int = 0
    inventory: List[Potion] = field(default_factory=list)
    weapons: List[Weapon] = field(default_factory=list)
    armors: List[Armor] = field(default_factory=list)
    equipped_weapon: Optional[Weapon] = None
    equipped_armor: Optional[Armor] = None

    @property
    def armor_class(self) -> int:
        return self.equipped_armor.value if self.equipped_armor else 10

    @property
    def damage(self) -> int:
        base_damage = 2
        weapon_bonus = self.equipped_weapon.damage if self.equipped_weapon else 0
        return base_damage + weapon_bonus

    def equip_weapon(self, weapon: Weapon) -> bool:
        """Équipe une arme"""
        if weapon in self.weapons:
            self.equipped_weapon = weapon
            return True
        return False

    def heal(self, amount: int) -> int:
        """
        Soigne le joueur
        Returns: points de vie réellement gagnés
        """
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before
```

**setup.py pour dnd-core**
```python
from setuptools import setup, find_packages

setup(
    name="dnd-core",
    version="0.1.0",
    description="D&D 5th Edition Core Rules Engine",
    author="Your Name",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black", "mypy"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
```

#### Phase 2: Adapter les Projets Existants

**Pour dnd-ncurses (simplifié):**

```python
# Avant (dans entities.py)
@dataclass
class Player(Entity):
    # ... tout le code dupliqué

# Après (dans main.py)
from dnd_core.entities import Player, Monster
from dnd_core.equipment import Weapon, Armor, Potion

# Le reste du code reste identique, juste changer les imports
```

**requirements.txt pour dnd-ncurses:**
```
dnd-core>=0.1.0
# ou en mode développement local:
# -e ../dnd-core
```

**Pour dnd-console (version complète):**

Le projet principal peut progressivement migrer vers le core package en:
1. Gardant la compatibilité avec l'existant
2. Migrant progressivement les classes vers dnd-core
3. Important depuis dnd-core au lieu de dao_classes.py

#### Phase 3: Publication et Distribution

```bash
# Pour dnd-core
cd dnd-core
python setup.py sdist bdist_wheel

# Installation locale pour développement
pip install -e .

# Ou publication sur PyPI
twine upload dist/*
```

Ensuite chaque projet peut installer:
```bash
pip install dnd-core
```

### Gestion des Versions

#### Pour dnd-core

Utiliser le versioning sémantique (SemVer):
- **0.1.0** - Version initiale avec classes de base
- **0.2.0** - Ajout du système de combat complet
- **0.3.0** - Ajout du système de sorts
- **1.0.0** - API stable

#### Pour les jeux individuels

Chaque jeu peut avoir son propre versioning et spécifier la version de dnd-core requise:

```python
# setup.py pour dnd-ncurses
install_requires=[
    "dnd-core>=0.1.0,<0.2.0",  # Compatible avec 0.1.x
]
```

### Structure de Développement Recommandée

```
workspace/
├── dnd-core/          # Git repo principal
├── dnd-console/       # Git repo séparé
├── dnd-ncurses/       # Git repo séparé  
├── dnd-pygame/        # Git repo séparé
├── dnd-pyqt/          # Git repo séparé
└── dnd-tkinter/       # Git repo séparé
```

Ou utiliser un monorepo avec Git submodules:

```
dnd-games/
├── core/              # Submodule
├── console/           # Submodule
├── ncurses/           # Submodule
└── ...
```

### Exemple d'Utilisation

**Dans n'importe quel projet:**

```python
# Créer un joueur
from dnd_core.entities import Player
from dnd_core.equipment import Weapon, Armor

player = Player(name="Gandalf", hp=50, max_hp=50, gold=100)

# Ajouter équipement
sword = Weapon(name="Long Sword", damage=5, cost=150)
player.weapons.append(sword)
player.equip_weapon(sword)

# Combat
from dnd_core.entities import Monster

orc = Monster(name="Orc", hp=15, max_hp=15, _damage=3, armor=13)
damage_dealt = player.attack(orc)

if damage_dealt > 0:
    print(f"{player.name} dealt {damage_dealt} damage to {orc.name}!")
```

## Recommandations Spécifiques

### 1. Migration Graduelle

Ne pas tout migrer d'un coup. Commencer par:
1. Créer `dnd-core` avec les classes de base
2. Migrer `dnd-ncurses` (le plus simple)
3. Puis les autres versions progressivement

### 2. Tests

Ajouter des tests unitaires pour `dnd-core`:

```python
# tests/test_player.py
import pytest
from dnd_core.entities import Player
from dnd_core.equipment import Weapon

def test_player_equip_weapon():
    player = Player(name="Test", hp=20, max_hp=20)
    sword = Weapon(name="Sword", damage=5, cost=100)
    
    player.weapons.append(sword)
    assert player.equip_weapon(sword) == True
    assert player.damage == 7  # 2 base + 5 weapon
```

### 3. Documentation

Créer une documentation pour `dnd-core`:
- README avec exemples d'utilisation
- API documentation avec Sphinx
- Guide de contribution

### 4. CI/CD

Configurer GitHub Actions pour:
- Tests automatiques sur `dnd-core`
- Publication automatique sur PyPI
- Tests d'intégration avec les projets clients

## Conclusion

**OUI, il est non seulement possible mais fortement recommandé de:**
1. ✅ Convertir les classes D&D en modules réutilisables
2. ✅ Séparer les jeux en projets distincts
3. ✅ Créer un package core Python (`dnd-core`)

**Avantages immédiats:**
- Code DRY (Don't Repeat Yourself)
- Maintenance centralisée
- Tests unitaires partagés
- Facilite l'ajout de nouvelles versions
- Architecture professionnelle et scalable

**Effort requis:**
- Court terme: Moyen (refactoring initial)
- Long terme: Faible (maintenance simplifiée)

**Retour sur investissement:**
- 🟢 Très élevé pour un projet multi-versions comme celui-ci

Je recommande de commencer dès maintenant avec une migration progressive, en commençant par extraire les classes de base dans `dnd-core`.

