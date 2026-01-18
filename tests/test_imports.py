#!/usr/bin/env python3
"""Simple test script to check if dnd-5e-core is properly included in the executable"""
import sys
import os

print("Testing dnd_5e_core import...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Executable: {sys.executable}")
print()

try:
    import dnd_5e_core
    print("✅ dnd_5e_core imported successfully")
    print(f"   Location: {dnd_5e_core.__file__}")
    print()

    from dnd_5e_core.entities import Character
    print("✅ Character class imported")

    from dnd_5e_core.equipment import Weapon
    print("✅ Weapon class imported")

    from dnd_5e_core.ui import cprint, Color
    print("✅ UI utilities imported")

    print()
    print("🎉 All imports successful!")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

