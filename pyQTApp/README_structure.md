# D&D 5th Edition Character Manager

## Castle Location Modules

### 1. The Tavern - Character Management Hub
- Character roster management
- Party formation center
- Character inspection system
- Party size limit: 6 members
- Dynamic roster updates

### 2. Boltac's Trading Post - Equipment & Commerce
- Equipment buying/selling
- Inventory management
- Party gold distribution
- Item database access
- Character wealth tracking

### 3. The Temple of Cant - Character Revival Center
- Character resurrection
- Status effect management
- Constitution-based revival
- Age progression system
- Permanent death handling

### 4. The Inn - Recovery & Healing Center
Room Tiers:
- Basic:     0 GP/week  - No healing
- Common:    10 GP/week - 1 week stay
- Quality:   100 GP/week - 3 weeks stay
- Luxury:    200 GP/week - 7 weeks stay
- Royal:     500 GP/week - 10 weeks stay

## Adventure Modules

### 5. Edge of Town - Adventure Gateway
- Adventure initiation
- Monster encounters
- World navigation
- Return mechanism
- Safe zone interface

### 6. Combat System - Battle Manager
- Turn-based combat
- Action management
- Monster encounters
- Party tactics
- Combat resolution

## Core System Modules

### 7. Character System
- Character creation
- Stat management
- Level progression
- Class abilities
- Race features

### 8. Inventory System
- Item management
- Equipment tracking
- Currency handling
- Weight calculation
- Storage limits

### 9. Combat Engine
- Initiative tracking
- Action resolution
- Damage calculation
- Status effects
- Victory conditions

### 10. Save System
- Character persistence
- Game state saving
- Progress tracking
- Data management
- Backup handling

## Technical Modules

### 11. Database Manager
- Monster database
- Item database
- Character storage
- Game state persistence
- Data validation

### 12. UI Framework
- PyQt5 interface
- Window management
- Event handling
- User input
- Visual feedback

### 13. Resource Manager
- Asset loading
- Image handling
- Sound management
- Resource allocation
- Memory optimization

### 14. Debug System
- Error logging
- State tracking
- Performance monitoring
- Debug output
- Testing tools

## Project Structure
```python
DnD-5th-Edition-API/
├── pyQTApp/
│   ├── Castle/
│   │   ├── Tavern_module.py     # Character & Party Management
│   │   ├── Boltac_module.py     # Trading & Equipment
│   │   ├── Cant_module.py       # Revival & Restoration
│   │   ├── Inn_module.py        # Healing & Recovery
│   │   └── EdgeOfTown.py        # Adventure Gateway
│   ├── Combat/
│   │   ├── combat_ui.py         # Combat Interface
│   │   ├── actions.py           # Combat Actions
│   │   └── monsters.py          # Monster System
│   ├── Core/
│   │   ├── character.py         # Character System
│   │   ├── inventory.py         # Item Management
│   │   └── save_system.py       # Game State Management
│   ├── Database/
│   │   ├── monster_db.py        # Monster Database
│   │   └── item_db.py          # Item Database
│   ├── UI/
│   │   └── windows/            # Interface Components
│   ├── Resources/
│   │   ├── images/             # Visual Assets
│   │   └── data/               # Game Data
│   └── wizardry.py             # Main Application
├── characters/                  # Character Storage
└── requirements.txt            # Dependencies
