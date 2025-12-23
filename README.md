# D&D 5th Edition Simulation Engine

A comprehensive simulation engine implementing D&D 5th Edition rules with multiple interface options.

## 🏗️ Architecture

This project uses **dnd-5e-core** package for all D&D 5e game logic. Most games import from dnd-5e-core for entities, combat, spells, equipment, etc.

**See [docs/ARCHITECTURE_JEUX.md](docs/ARCHITECTURE_JEUX.md) for detailed architecture documentation.**

## Available Versions

### 1. Console Version ✅ Uses dnd-5e-core
Full D&D 5th Edition rules implementation with character creation and combat simulation.

**Run using:**
- Recommended: `python ./main.py` (requires Terminal and Python ≥ 3.10.0)
- Debug mode: `python ./main_pexpect.py` (for IDE debugging, may have minor display issues)

[Console Version Manual](manual/manual_console_version.md)

### 2. Ncurses Version ✅ Uses dnd-5e-core
Text-based interface (ncurses) - ncurses adaptation of main.py with full D&D 5e features.

**Run using:**
- `python ./main_ncurses.py`

**Features:**
- Castle services (Tavern, Inn, Temple, Trading Post, Training Grounds)
- Dungeon exploration with combat
- Character creation and party management
- Inventory management

[Ncurses Version Manual](manual/manual_ncurses_version.md)

### 3. Pygame Suite ✅ Uses dnd-5e-core
Complete graphical game with multiple modules:

**Main Menu:** `python ./dungeon_menu_pygame.py`

**Modules:**
- **dungeon_pygame.py** - Dungeon exploration and combat
- **boltac_tp_pygame.py** - Boltac's Trading Post (buy/sell equipment)
- **monster_kills_pygame.py** - Monster kill statistics

**Features:**
- Spell casting
- Inventory management
- Melee & ranged combat (D&D 5th Edition rules)
- Graphical interface with mouse support

[Pygame Version Documentation](README_pygame_version.md)

### 4. Tkinter Version ❌ Standalone (simplified D&D rules)
Basic arena with **simplified custom D&D rules** (does not use dnd-5e-core).

- Single-character dungeon exploration
- Multiple dungeon levels 
- Treasure collection 
- Simplified D&D ruleset implementation

**Run using:**
- `python ./dungeon_tk.py`

[Tkinter Version Manual](manual/manual_tk_version.md)

### 5. PyQt5 Version ✅ Uses dnd-5e-core
Graphical interface using Qt Designer framework with full D&D features except training grounds.

**Run using:**
- `python pyQTApp/wizardry.py`

[PyQt5 Version Manual](manual/manual_pyQT_version.md)

### 5. RPG Pygame Demo ❌ Standalone (simplified D&D rules)
Basic gameplay with collision detection (Simplon gamejam inspired)

**Run using:**
- `python ./lab_games/rpg_pygame.py`

[RPG Demo Manual](manual/manual_rpg_pygame_demo_version.md)

### 6. Ncurses Version ❌ Standalone (simplified D&D rules)
Text-based arena with basic combat and enemy movement

**Run using:**
- `python ./lab_games/rpg_ncurses.py`

[Ncurses Version Manual](manual/manual_ncurses_version.md)

## Installation

### Binary Installation
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run platform-specific installer:
- macOS/Linux: `./install.sh`
- Windows: `install.bat`

### Development Installation
    Required: Python 3.11+

#### Option 1: IDE Installation (Recommended)
    Use IntelliJ PyCharm 2022.3 Community Edition's package manager

#### Option 2: Manual Installation
1. Update pip:
```bash
pip install --upgrade pip
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```


