# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Simple test spec for dnd-5e-core imports
from PyInstaller.utils.hooks import collect_all
import os

dnd_5e_core_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'dnd-5e-core')
if not os.path.exists(dnd_5e_core_path):
    dnd_5e_core_path = os.path.join(os.path.dirname(os.getcwd()), 'dnd-5e-core')

# Collect dnd-5e-core data files
dnd_core_datas, dnd_core_binaries, dnd_core_hiddenimports = collect_all('dnd_5e_core')

a = Analysis(
    ['test_imports.py'],
    pathex=[dnd_5e_core_path] if os.path.exists(dnd_5e_core_path) else [],
    binaries=dnd_core_binaries,
    datas=dnd_core_datas,
    hiddenimports=dnd_core_hiddenimports,
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='test-imports',
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

