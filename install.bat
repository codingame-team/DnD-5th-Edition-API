@echo off

rem Check if PyInstaller is installed
where /q pyinstaller
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Please install it first.
    pause
    exit /b
)

rem Create the executable
pyinstaller --onefile ^
    --add-data "collections;collections" ^
    --add-data "data;data" ^
    --add-data "sprites;sprites" ^
    --add-data "sounds:sounds" ^
    --add-data "images;images" ^
    --add-data "combat;combat" ^
    --add-data "Tables;Tables" ^
    --add-data "gameState;gameState" ^
    dungeon_menu_pygame.py