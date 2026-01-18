# Changelog - DnD 5E NCurses Edition

All notable changes to the NCurses implementation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Build System** - Complete multi-OS build system with PyInstaller
  - `main.spec` - PyInstaller config for console version
  - `dungeon_menu_pygame.spec` - PyInstaller config for pygame version
  - `build_all.sh` - Automated build script for macOS/Linux
  - `build_all.bat` - Automated build script for Windows
  - Optimized executables (33% smaller than integrated approach)
  - See `docs/GUIDE_DEPLOIEMENT.md` for instructions
- **Documentation** - Complete deployment and architecture guides
  - `docs/ANALYSE_DEPLOIEMENT.md` - Detailed analysis (13 pages)
  - `docs/GUIDE_DEPLOIEMENT.md` - Step-by-step deployment guide
  - `docs/ARCHITECTURE_JEUX.md` - Games architecture documentation
  - `docs/DECISION_DEPLOIEMENT.md` - Deployment decision summary
- **Requirements** - New requirements files for different use cases
  - `requirements-dist.txt` - For production (with dnd-5e-core from PyPI)
  - `requirements-dev-new.txt` - For local development

### Changed
- **populate_functions.py** - Updated to use dnd-5e-core collections module
  - Now uses `dnd_5e_core.data.populate()` when available
  - Automatic fallback to local collections if dnd-5e-core not found
  - 100% backward compatible, no code changes required
  - See `test_populate_migration.py` for validation
- **README.md** - Updated with new build instructions and download links

### Planned
- Trading post implementation (buy/sell equipment)
- Character status detailed view
- Party reorder with interactive UI
- Character rename with validation
- Enhanced inventory system
- Sound effects (terminal beep)
- Custom color themes

## [0.2.0] - 2025-12-16

### Added - Full Gameplay Implementation

#### Complete Game Functions
All main.py functions have been fully implemented in NCurses:

**Castle Services:**
- ✅ **Gilgamesh's Tavern** - Complete party management
  - Add/Remove members
  - Divvy gold (equal distribution)
  - Disband party
  - Character status (structure)
  - Reorder (structure)
- ✅ **Adventurer's Inn** - Full rest system
  - 5 room types (Free to 500GP)
  - HP recovery based on room quality
  - Age progression (weeks)
  - Spell slot restoration
  - Gold deduction
- ✅ **Temple of Cant** - Complete resurrection services
  - PARALYZED/STONED/DEAD/ASHES healing
  - Success chance based on Constitution
  - Gold cost by level
  - Party member contribution
- 🚧 **Boltac's Trading Post** - Placeholder

**Edge of Town:**
- ✅ **Training Grounds** - Character creation
  - Create new character (interactive)
  - Create random character
  - Delete character with confirmation
  - Character status (structure)
  - Rename (structure)
- ✅ **Dungeon Exploration** - Full combat system
  - Text mode integration
  - Complete explore_dungeon() call
  - Monster encounters
  - Death handling
  - Auto-save after exploration

#### Technical Improvements
- Text/NCurses mode switching
  - Proper curses.endwin() / reinit
  - Seamless transitions
  - Error handling
- Enhanced error handling
  - Protected saves
  - Fallback stubs
  - Try/catch everywhere
- Auto-save system
  - Save after every important action
  - Character file management
  - Party state persistence

#### New UI Components
- 11 new draw functions
- 11 new input handlers
- 15 total game modes
- Context-aware menus
- Real-time feedback

### Changed
- Mode system expanded (4 → 15 modes)
- Handler architecture refactored
- Import system with fallbacks
- Load game data with collections

### Fixed
- Duplicate function definitions
- Return type consistency
- Import error handling
- Curses reinitialization

## [0.1.0] - 2024-12-16

### Added - Initial Release

#### Core Files
- `main_ncurses.py` - Main NCurses interface implementation
- `run_ncurses.py` - Launcher script
- `test_ncurses.py` - Test suite for NCurses compatibility
- `config_ncurses.py` - Configuration file

#### Documentation
- `NCURSES_README.md` - Complete documentation
- `NCURSES_COMPARISON.md` - Comparison with original main.py
- `QUICKSTART.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation overview
- `CHANGELOG.md` - This file

#### Features
- Main menu navigation
- Castle menu with 6 options
- Edge of Town menu
- Party & Roster management interface
- Dual message system
- Terminal size verification (80x24 minimum)
- Color support detection
- Keyboard navigation

---

## Version History

### Version Numbering

We use Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Notes

#### v0.1.0 - "Foundation" (2024-12-16)
**Focus**: Basic infrastructure and navigation

This initial release provides the foundation for a complete NCurses-based D&D 5E game interface. While core gameplay features are not yet implemented, the architecture is solid and ready for expansion.

**What works:**
- Complete menu navigation system
- Party/roster display
- Message system
- Terminal handling

**What's next:**
- Character creation (v0.2.0)
- Combat system (v0.3.0)
- Dungeon exploration (v0.4.0)

---

## Roadmap

### v0.2.0 - "Character Creation" (Planned)
**Target**: Q1 2025

#### Features
- [ ] Full character creation wizard
  - [ ] Race selection with subraces
  - [ ] Class selection
  - [ ] Ability score rolling/assignment
  - [ ] Equipment selection
  - [ ] Name and appearance
- [ ] Character sheet display
- [ ] Edit existing characters
- [ ] Delete characters from roster

### v0.3.0 - "Combat System" (Planned)
**Target**: Q2 2025

#### Features
- [ ] Turn-based combat implementation
- [ ] Combat animations
- [ ] Dice roll visualization
- [ ] Damage calculation display
- [ ] Status effects
- [ ] Combat log
- [ ] Flee mechanics
- [ ] Victory/defeat handling

### v0.4.0 - "Dungeon Exploration" (Planned)
**Target**: Q2 2025

#### Features
- [ ] Maze rendering
- [ ] Player movement on map
- [ ] Enemy placement
- [ ] Random encounters
- [ ] Treasure chests
- [ ] Trap detection
- [ ] Mini-map
- [ ] Fog of war

### v0.5.0 - "Services & Trading" (Planned)
**Target**: Q3 2025

#### Features
- [ ] Tavern recruitment system
- [ ] Inn rest and recovery
- [ ] Temple resurrection and healing
- [ ] Trading post buy/sell
- [ ] Equipment comparison
- [ ] Price negotiation
- [ ] Inventory management

### v0.6.0 - "Polish & Features" (Planned)
**Target**: Q4 2025

#### Features
- [ ] Save/load system
- [ ] Multiple save slots
- [ ] Character import/export
- [ ] Custom color themes
- [ ] Sound effects
- [ ] Achievements
- [ ] Statistics tracking
- [ ] High scores

### v1.0.0 - "Complete Edition" (Planned)
**Target**: 2026

#### Features
- All core features implemented
- Comprehensive documentation
- Full test coverage
- Performance optimizations
- Multi-language support
- Tutorial mode
- Modding support

---

## Contributing

### How to Contribute

1. **Report Bugs**
   - Use the issue tracker
   - Include terminal type and size
   - Provide reproduction steps

2. **Suggest Features**
   - Check the roadmap first
   - Open a feature request
   - Explain use case and benefits

3. **Submit Code**
   - Fork the repository
   - Create a feature branch
   - Follow coding standards
   - Add tests if applicable
   - Update documentation
   - Submit pull request

### Coding Standards

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to all functions
- Keep functions small and focused
- Comment complex logic
- Handle curses.error exceptions
- Test on multiple terminals

### Testing Checklist

Before submitting:
- [ ] Code runs without errors
- [ ] `test_ncurses.py` passes
- [ ] Tested on at least 2 different terminals
- [ ] Terminal resize doesn't crash
- [ ] ESC key works in all menus
- [ ] Documentation updated
- [ ] Config file updated if needed

---

## Credits

### Based On
- **DnD-5e-ncurses** - Architecture and design patterns
- **DnD 5th Edition API** - Original game logic

### Technologies
- Python 3.10+
- NCurses library
- D&D 5th Edition ruleset

### Contributors
- Initial implementation: 2024-12-16

---

## License

Same license as the main DnD-5th-Edition-API project.

---

## Links

- [Main Repository](https://github.com/yourusername/DnD-5th-Edition-API)
- [Documentation](./NCURSES_README.md)
- [Quick Start](./QUICKSTART.md)
- [Issue Tracker](https://github.com/yourusername/DnD-5th-Edition-API/issues)

---

**Legend:**
- ✅ Implemented
- 🚧 In Progress
- 📋 Planned
- ❌ Deprecated

