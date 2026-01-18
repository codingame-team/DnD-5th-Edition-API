#!/bin/bash

# Build script for DnD 5e Games - macOS/Linux
# Creates standalone executables for the main console and pygame versions

set -e  # Exit on error

# Colors for output
NC='\033[0m' # No Color
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'

echo ""
echo "🎮 ================================================"
echo "🎮  Building D&D 5e Games"
echo "🎮 ================================================"
echo ""

# Ensure we're in repository root (main.py must exist)
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from DnD-5th-Edition-API directory."
    exit 1
fi

# Check if dnd-5e-core is available locally
echo -e "${BLUE}📦 Checking dnd-5e-core...${NC}"
if [ -d "../dnd-5e-core" ]; then
    echo -e "${GREEN}✅ Found dnd-5e-core in ../dnd-5e-core${NC}"
    echo -e "${BLUE}📦 Installing dnd-5e-core in development mode...${NC}"
    pip install -e ../dnd-5e-core
else
    echo -e "${YELLOW}⚠️  dnd-5e-core not found locally. Trying to install from PyPI...${NC}"
    if ! pip install dnd-5e-core; then
        echo "❌ Error: Could not install dnd-5e-core from PyPI. Please ensure the package is available or clone ../dnd-5e-core locally."
        exit 1
    fi
fi

# Install PyInstaller if not present
echo -e "${BLUE}📦 Checking PyInstaller...${NC}"
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}⚠️  PyInstaller not found. Installing...${NC}"
    pip install pyinstaller
else
    echo -e "${GREEN}✅ PyInstaller found${NC}"
fi

echo ""
echo -e "${GREEN}✅ All dependencies ready${NC}"
echo ""

# Clean previous builds
echo -e "${BLUE}🧹 Cleaning previous builds...${NC}"
rm -rf build/ dist/
echo -e "${GREEN}✅ Cleanup done${NC}"
echo ""

# Build Console version (main.spec)
if [ -f "main.spec" ]; then
    echo -e "${BLUE}🎮 Building Console version (main.py) using main.spec...${NC}"
    if pyinstaller main.spec --clean --noconfirm; then
        echo -e "${GREEN}✅ Console version built successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Console build had warnings or errors${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  main.spec not found, skipping Console build${NC}"
fi

echo ""

# Build Pygame version (dungeon_menu_pygame.spec)
if [ -f "dungeon_menu_pygame.spec" ]; then
    echo -e "${BLUE}🎮 Building Pygame version (dungeon_menu_pygame.py) using dungeon_menu_pygame.spec...${NC}"
    if pyinstaller dungeon_menu_pygame.spec --clean --noconfirm; then
        echo -e "${GREEN}✅ Pygame version built successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Pygame build had warnings or errors${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  dungeon_menu_pygame.spec not found, skipping Pygame build${NC}"
fi

echo ""

# Show results
if [ -d "dist" ]; then
    TOTAL_SIZE=$(du -sh dist/ | cut -f1)
    echo -e "${GREEN}📁 Executables available in: ${BLUE}dist/${NC}"
    echo ""
    ls -lh dist/
    echo ""
    echo -e "${GREEN}📊 Total size: ${TOTAL_SIZE}${NC}"
else
    echo -e "${YELLOW}⚠️  No 'dist' directory found. Builds may have been skipped or failed.${NC}"
fi

echo ""
echo "🎉 ================================================"
echo "🎉  Build Complete!"
echo "🎉 ================================================"
echo ""
echo "📦 To distribute:"
echo ""
echo "   ./dist/dnd-pygame          # Pygame version"
echo "   ./dist/dnd-console         # Console version"
echo ""
echo "🚀 To test the executables:"
echo "   ./dist/dnd-pygame          # Run Pygame version"
echo "   ./dist/dnd-console         # Run Console version"
echo ""
