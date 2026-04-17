#!/bin/bash
echo "Building Windows executable..."

if [ ! -f "$HOME/.wine_elo/drive_c/Program Files/Python311/python.exe" ]; then
    echo "Installing Python in Wine..."
    cd /tmp
    curl -sL https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -o python-installer.exe
    WINEPREFIX="$HOME/.wine_elo" wine python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 2>&1 | tail -3
    rm python-installer.exe
fi

WINEPREFIX="$HOME/.wine_elo" wine python -m pip install pyinstaller pyside6 -q 2>&1 | tail -3

cd /home/blap/projects/rivals2-lb
WINEPREFIX="$HOME/.wine_elo" wine python -m PyInstaller --onefile --name elo_calc_gui elo_calc_gui.py 2>&1 | tail -5

mkdir -p /home/blap/projects/rivals2-lb/dist/win
mv /home/blap/projects/rivals2-lb/dist/elo_calc_gui.exe /home/blap/projects/rivals2-lb/dist/win/
echo "Windows build: dist/win/elo_calc_gui.exe"