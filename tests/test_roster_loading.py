#!/usr/bin/env python3
"""Test script to debug roster loading"""

import os
import sys

# Change to project directory
os.chdir('/')

# Test without ncurses first
print("=== Testing roster loading ===\n")

# Check if characters exist
chars_dir = "../gameState/characters"
print(f"Characters directory: {chars_dir}")
print(f"Directory exists: {os.path.exists(chars_dir)}")

if os.path.exists(chars_dir):
    files = [f for f in os.listdir(chars_dir) if f.endswith('.dmp')]
    print(f"Found {len(files)} .dmp files:")
    for f in files[:10]:
        print(f"  - {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

print("\n=== Testing get_roster stub ===\n")

# Import the stub
from main_ncurses import get_roster, IMPORTS_AVAILABLE

print(f"IMPORTS_AVAILABLE: {IMPORTS_AVAILABLE}")
print(f"Calling get_roster('{chars_dir}')...")

roster = get_roster(chars_dir)
print(f"Result: {len(roster)} characters loaded")

if roster:
    print(f"\nFirst character:")
    char = roster[0]
    print(f"  Name: {char.name if hasattr(char, 'name') else 'N/A'}")
    print(f"  Level: {char.level if hasattr(char, 'level') else 'N/A'}")
    print(f"  Class: {char.class_type.name if hasattr(char, 'class_type') else 'N/A'}")
else:
    print("\n❌ No characters loaded!")
    print("\nDebug: Trying to load manually...")

    import pickle
    files = [f for f in os.listdir(chars_dir) if f.endswith('.dmp')]
    if files:
        test_file = os.path.join(chars_dir, files[0])
        print(f"Trying to load: {test_file}")
        try:
            with open(test_file, 'rb') as f:
                char = pickle.load(f)
                print(f"✓ Successfully loaded {char.name if hasattr(char, 'name') else 'unknown'}")
        except Exception as e:
            print(f"❌ Error: {e}")

