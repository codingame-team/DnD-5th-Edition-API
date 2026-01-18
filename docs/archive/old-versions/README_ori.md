<!-- TOC -->
  * [Simulation engine system of D&D 5th Edition universe](#simulation-engine-system-of-dd-5th-edition-universe)
      * [New Features (Staging)](#new-features-staging)
<!-- TOC -->

## Simulation engine system of D&D 5th Edition universe

Usage to run:
  - [console version](manual/manual_console_version.md): (full DnD 5th rules with character's creation and combat simulation)
    - python ./main.py (using a compatible Terminal and python version >= 3.10.0) -> best method for playing
    - python ./main_pexpect.py (inside Python IDE - emulate a pseudo Terminal using pexpect) -> preferred method for debugging (still includes some minor display bugs)
  - [pyQT5 version](manual/manual_pyQT_version.md): (graphical version using famous `QT Designer` framework, providing same features than console version, except `training grounds`, but with full control of party's action during combat phase using `QT Designer` widgets)
    - python pyQTApp/wizardry.py
  - [Tkinter version](manual/manual_tk_version.md): (simple graphical arena with basic fights and moving enemies, and limited DnD rules)
    - python ./dungeon_tk.py
  - [Pygame version](README_pygame_version.md): (more complex version using spell's casting, inventory management, melee & ranged attacks following advanced DnD 5th rules)
  - [RPG Pygame demo version](manual/manual_rpg_pygame_demo_version.md) (basic gameplay using collision inspired from `Simplon` gamejam's classroom)
    - python ./rpg_pygame.py
  - [Ncurses version](manual/manual_ncurses_version.md): (simple textual arena using *ncurses* with basic fights and moving enemies, and limited DnD rules)

#### New Features (Staging)
    Graphic combat exploration using Tk with a single character (and limited gameplay) and DnD minimal rulesets:

    - explore levels of dungeons
    - collect treasures

    How to run:
    - `python dungeon_tk.py` (playable version)
    
    Similar projet but with pyGame:

    How to run:
    - `python dungeon_pygame.py` (draft version)

Prerequisites:
- Run in binary mode:
  - Installer pyinstaller: `pip install pyinstaller`
    - install.sh (to compile project on macOS/Linux versions)
    - install.bat (to compile project on windows versions)
- Run in interpreted mode (useful for debugging)
  - List of required modules for python v3.11:
      ./requirements.txt
  - Procedure to install modules (inside your local or virtual Python environnement):
    - `Noob` method: Let your favorite IDE handle missing modules (preferred IDE: IntelliJ PyCharm 2022.3 Community Edition)
    - `Geek` method:
      - Using command line:
        - Get the latest version of pip module:
          - pip install --upgrade pip
          - If pip3.11 is you latest version:
            - pip3.11 install -r requirements.txt


