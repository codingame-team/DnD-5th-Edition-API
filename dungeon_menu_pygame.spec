# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for dungeon_menu_pygame.py
D&D 5e Pygame Game Suite using dnd-5e-core package
"""

block_cipher = None

# Collect all dnd-5e-core modules and data
from PyInstaller.utils.hooks import collect_submodules, collect_all
import os

dnd_5e_core_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'dnd-5e-core')
if not os.path.exists(dnd_5e_core_path):
    dnd_5e_core_path = os.path.join(os.path.dirname(os.getcwd()), 'dnd-5e-core')

hidden_imports = collect_submodules('dnd_5e_core')
hidden_imports += [
    # Pygame modules
    'pygame',
    'pygame.mixer',
    'pygame.font',
    'pygame.image',
    # Standard library
    'sqlite3',
    'csv',
    'json',
]

# Collect dnd-5e-core data files
dnd_core_datas, dnd_core_binaries, dnd_core_hiddenimports = collect_all('dnd_5e_core')
hidden_imports += dnd_core_hiddenimports

# Add dnd-5e-core collections explicitly (they are outside the package)
if os.path.exists(dnd_5e_core_path):
    collections_path = os.path.join(dnd_5e_core_path, 'collections')
    if os.path.exists(collections_path):
        # Add all JSON files from collections directory
        import glob
        for json_file in glob.glob(os.path.join(collections_path, '*.json')):
            dnd_core_datas.append((json_file, 'collections'))
        print(f"Added {len(glob.glob(os.path.join(collections_path, '*.json')))} collection files from {collections_path}")

a = Analysis(
    ['dungeon_menu_pygame.py'],
    pathex=[dnd_5e_core_path] if os.path.exists(dnd_5e_core_path) else [],
    binaries=dnd_core_binaries,
    datas=[
        # Game-specific assets
        ('sprites', 'sprites'),
        ('sounds', 'sounds'),
        ('images', 'images'),
        ('maze', 'maze'),
        ('gameState', 'gameState'),
        ('Tables', 'Tables'),
        ('data', 'data'),  # Include D&D 5e data files
    ] + dnd_core_datas,
    hiddenimports=hidden_imports,
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dnd-pygame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for pygame
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='images/icon.ico',  # Uncomment if you have an icon
)

