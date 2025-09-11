# D&D 5th Edition Simulation Engine

A comprehensive simulation engine implementing D&D 5th Edition rules with multiple interface options.

## Available Versions

### 1. Console Version
Full D&D 5th Edition rules implementation with character creation and combat simulation.

**Run using:**
- Recommended: `python ./main.py` (requires Terminal and Python ≥ 3.10.0)
- Debug mode: `python ./main_pexpect.py` (for IDE debugging, may have minor display issues)

[Console Version Manual](manual/manual_console_version.md)

### 2. PyQt5 Version
Graphical interface using Qt Designer framework with full D&D features except training grounds.

**Run using:**
- `python pyQTApp/wizardry.py`

[PyQt5 Version Manual](manual/manual_pyQT_version.md)

### 3. Tkinter Version (Tkinter Dungeon Explorer)
Basic arena with simplified D&D rules, featuring fights and enemy movement.

- Single-character dungeon exploration with:
- Multiple dungeon levels 
- Treasure collection 
- Basic D&D ruleset implementation

**Run using:**
- `python ./dungeon_tk.py`

[Tkinter Version Manual](manual/manual_tk_version.md)

### 4. Pygame Version (Pygame Dungeon Explorer)
Advanced implementation featuring:
- Spell casting
- Inventory management
- Melee & ranged combat (D&D 5th Edition rules)

[Pygame Version Documentation](README_pygame_version.md)

### 5. RPG Pygame Demo
Basic gameplay with collision detection (Simplon gamejam inspired)

**Run using:**
- `python ./rpg_pygame.py`

[RPG Demo Manual](manual/manual_rpg_pygame_demo_version.md)

### 6. 3D Dungeon Explorer (Refactored)
Modern 3D first-person dungeon crawler with object-oriented architecture:
- **Raycasting 3D rendering** with textured walls
- **Procedural dungeon generation** using rooms and corridors
- **Real-time combat system** with projectiles and animations
- **Health potions** and inventory management
- **Mini-map** for navigation
- **Clean OOP design** with Game and Dungeon classes

**Features:**
- First-person 3D perspective with mouse aiming
- Dynamic enemy AI with shooting and movement
- Visual effects for shooting and damage
- Sound effects for immersive gameplay
- Optimized rendering for smooth performance

**Run using:**
- `python tools/dungeon_perl/dungeon_3d.py`

**Controls:**
- Z/S - Move forward/backward
- Q/D - Turn left/right
- Arrow keys - Strafe left/right
- Mouse click - Shoot
- P - Use health potion

### 7. Ncurses Version
Text-based arena with basic combat and enemy movement

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


