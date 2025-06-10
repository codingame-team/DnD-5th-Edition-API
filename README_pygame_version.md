# D&D 5th Edition Game

A Python-based implementation of a Dungeons & Dragons style game using Pygame.

[User guide](manual/manual_pygame_version.md)

## Description

This project is a graphical interface for a D&D-inspired game that features character management,
inventory systems, and various gameplay mechanics. The game includes a trading post (Boltac's),
character roster management, and dungeon exploration features.

## Features

- Character Management System
    - Save/Load functionality
    - Character roster handling
    - Character state persistence

- Trading & Inventory System
    - Equipment management
    - Buy/Sell interface
    - Item categorization

- Dungeon Gameplay
    - Monster encounters
    - Kill tracking system
    - Line of sight calculations (Bresenham's algorithm)
    - Pathfinding (A* and BFS algorithms)

- Item Systems
    - Weapons
    - Armor
    - Various potion types (Healing, Speed, Strength)
    - Treasure system

- Combat & Actions
    - Turn-based combat system
    - Special abilities
    - Spell casting system
    - Action types management

## Technical Specifications

- Built with Python and Pygame
- Screen Resolution: 1280x720 pixels (configurable)
- Tile-based movement system (32x32 pixels per tile)
- 60 FPS target frame rate
- Advanced pathfinding algorithms
- Dungeon generation systems