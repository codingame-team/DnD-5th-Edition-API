@echo off
REM Build script for DnD 5e Games - Windows
REM Creates standalone executables for all game versions

echo ================================================
echo   Building D^&D 5e Games
echo ================================================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from DnD-5th-Edition-API directory.
    pause
    exit /b 1
)

REM Check if dnd-5e-core is available
echo Checking dnd-5e-core...
if exist "..\dnd-5e-core\" (
    echo Found dnd-5e-core in ..\dnd-5e-core
    echo Installing dnd-5e-core in development mode...
    pip install -e ..\dnd-5e-core
) else (
    echo Warning: dnd-5e-core not found locally. Trying to install from pip...
    pip install dnd-5e-core
    if %errorlevel% neq 0 (
        echo ERROR: Could not install dnd-5e-core. Please ensure it's available.
        pause
        exit /b 1
    )
)

REM Check if PyInstaller is installed
echo Checking PyInstaller...
where /q pyinstaller
if %errorlevel% neq 0 (
    echo Warning: PyInstaller not found. Installing...
    pip install pyinstaller
)

echo.
echo All dependencies ready
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
echo Cleanup done
echo.

REM Build Console version
if exist "main.spec" (
    echo Building Console version (main.py)...
    pyinstaller main.spec --clean --noconfirm
    if %errorlevel% equ 0 (
        echo Console version built successfully
    ) else (
        echo Warning: Console build had issues
    )
    echo.
) else (
    echo Warning: main.spec not found, skipping Console build
)

REM Build Pygame version
if exist "dungeon_menu_pygame.spec" (
    echo Building Pygame version (dungeon_menu_pygame.py)...
    pyinstaller dungeon_menu_pygame.spec --clean --noconfirm
    if %errorlevel% equ 0 (
        echo Pygame version built successfully
    ) else (
        echo Warning: Pygame build had issues
    )
    echo.
) else (
    echo Warning: dungeon_menu_pygame.spec not found, skipping Pygame build
)

REM Show results
echo.
echo ================================================
echo   Build Complete!
echo ================================================
echo.
echo Executables available in: dist\
echo.

if exist "dist\" (
    dir dist\
    echo.
)

echo.
echo To test the executables:
echo    dist\dnd-console.exe        # Console version
echo    dist\dnd-pygame.exe          # Pygame version
echo.
echo To distribute:
echo    1. Test executables on target OS
echo    2. Rename with version: dnd-console-1.0-windows.exe
echo    3. Upload to GitHub Releases
echo.
pause

