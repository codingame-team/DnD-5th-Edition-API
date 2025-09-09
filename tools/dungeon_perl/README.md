# Dungeon Explorer Games

Two dungeon exploration games with different gameplay styles and graphics engines.

## Games Overview

### 🎮 dungeon.py - 2D Top-Down Dungeon Explorer
Classic 2D dungeon crawler with ASCII-style graphics and strategic gameplay.

**Features:**
- Procedurally generated dungeons with rooms and corridors
- Turn-based movement system
- Difficulty levels (1-5) with larger dungeons
- Time limits and restart functionality
- QZSD movement controls (AZERTY keyboard support)
- Simple terminal-based graphics

**Controls:**
- `Q` - Move up
- `Z` - Move down  
- `S` - Move left
- `D` - Move right
- `R` - Restart game
- `ESC` - Quit

**Requirements:**
- Python 3.7+
- No external dependencies

### 🎯 dungeon_3d.py - 3D First-Person Dungeon Shooter
Immersive 3D dungeon experience with real-time combat and advanced graphics.

**Features:**
- 3D raycasting engine with textured walls
- Real-time first-person shooter gameplay
- Enemy AI with movement and shooting
- Health system with potion collection
- Mouse-controlled shooting with crosshair
- Bullet physics and collision detection
- Line-of-sight mechanics
- Audio feedback for actions
- Animated enemy sprites
- HUD with health and inventory display

**Controls:**
- `Q` - Move forward
- `Z` - Move backward
- `S` - Turn left
- `D` - Turn right
- `Mouse` - Aim and shoot
- `P` - Use health potion
- `ESC` - Quit

**Requirements:**
- Python 3.7+
- Pygame library: `pip install pygame`

## Installation & Setup

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd tools/dungeon_perl

# For 2D version (no dependencies)
python dungeon.py

# For 3D version (install pygame first)
pip install pygame
python dungeon_3d.py
```

### Asset Support
The 3D version supports custom enemy sprites:
- Place PNG files in `assets/enemies/` directory
- Supported: `orc.png`, `skeleton.png`, `goblin.png`, `troll.png`
- Fallback sprites generated automatically if assets missing

## Gameplay

### 2D Dungeon (dungeon.py)
Navigate through procedurally generated dungeons. Choose difficulty level for larger, more complex mazes. Race against time to explore the entire dungeon.

### 3D Dungeon (dungeon_3d.py)
Survive in a 3D dungeon filled with enemies. Collect health potions, shoot enemies, and try to clear all rooms. Features realistic line-of-sight and bullet physics.

## Technical Details

### Dungeon Generation
Both games use the same procedural generation algorithm:
1. **Room Placement** - Random non-overlapping rectangular rooms
2. **Corridor Creation** - Connect rooms with L-shaped corridors
3. **Difficulty Scaling** - Larger dungeons with fewer corridors at higher difficulties

### 3D Rendering (dungeon_3d.py)
- **Raycasting Engine** - Classic Wolfenstein-style 3D rendering
- **Texture Mapping** - Wall textures with distance-based shading
- **Sprite Rendering** - 2D sprites in 3D space with scaling
- **Collision Detection** - Precise wall and entity collision

### Performance Optimization
- Efficient raycasting with early termination
- Sprite culling for off-screen entities
- Optimized texture rendering
- Frame-rate independent movement

## File Structure
```
tools/dungeon_perl/
├── dungeon.py              # 2D top-down version
├── dungeon_3d.py           # 3D first-person version
├── load_assets.py          # Asset loading utilities
├── assets/
│   └── enemies/            # Enemy sprite assets (optional)
└── README.md               # This file
```

## Development

### Adding New Features
- **2D Version**: Modify movement logic, add items, implement combat
- **3D Version**: Add new enemy types, weapons, or rendering effects

### Custom Assets
Create 64x64 PNG sprites for enemies and place in `assets/enemies/` directory. The game will automatically load and use them.

## Troubleshooting

### Common Issues
- **Pygame not found**: Install with `pip install pygame`
- **Performance issues**: Reduce window size or disable audio
- **Controls not working**: Ensure AZERTY keyboard layout support

### Debug Mode
Both games print debug information to console for troubleshooting.

## License
Part of the D&D 5th Edition API project. See main repository for license details.