# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# PyInstaller spec for main.py (Console version)
from PyInstaller.utils.hooks import collect_submodules

hidden_imports = [
    'dnd_5e_core',
    'dnd_5e_core.entities',
    'dnd_5e_core.combat',
    'dnd_5e_core.data',
    'dnd_5e_core.data.collections',
    'dnd_5e_core.equipment',
    'dnd_5e_core.spells',
    'dnd_5e_core.races',
    'dnd_5e_core.classes',
    'dnd_5e_core.abilities',
    'dnd_5e_core.mechanics',
    'dnd_5e_core.ui',
    'json',
    'csv',
    'sqlite3',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gameState', 'gameState'),
        ('Tables', 'Tables'),
        ('data', 'data'),  # Include D&D 5e data files
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pygame', 'tkinter', 'matplotlib'],
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
    name='dnd-console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
