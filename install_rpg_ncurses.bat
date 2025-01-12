@echo off

rem Check if PyInstaller is installed
where /q pyinstaller
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Please install it first.
    pause
    exit /b
)

rem Create the executable
pyinstaller --onefile rpg_ncurses.py