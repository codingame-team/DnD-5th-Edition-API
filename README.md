## Simulation engine system of D&D 5th Edition universe

Usage to run:
  - console mode: (full DnD 5th rules with character's creation and combat simulation)
    - python ./main.py (using a compatible Terminal and python version >= 3.10.0) -> best method for playing
    - python ./main_pexpect.py (inside Python IDE - emulate a pseudo Terminal using pexpect) -> preferred method for debugging (still includes some minor display bugs)
  - Tkinter version: (simple graphical arena with basic fights and moving enemies, and limited DnD rules)
    - python ./dungeon_tk.py
  - Pygame version: (more complex version using spell's casting, inventory management, melee & ranged attacks following *main.py* DnD 5th rules)
    - python ./dungeon_menu_pygame.py (to select a character)
    - python ./dungeon_
  - (under construction...) GUI mode:
    - python /pyQT5App/wizardry.py [under construction...]

#### New Features (Staging)
    Graphic maze exploration using Tk with a single character (and limited gameplay) and DnD minimal rulesets:

    - explore levels of dungeons
    - collect treasures

    How to run:
    - `python dungeon_tk.py` (playable version)
    
    Similar projet but with pyGame:

    How to run:
    - `python dungeon_pygame.py` (draft version)

Prerequisites:
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


