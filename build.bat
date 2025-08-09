@echo off
echo Building Unlock Music GUI...

echo Step 1: Compiling Go backend...
go build -o um.exe cmd\um\main.go
if errorlevel 1 (
    echo Failed to compile Go backend
    pause
    exit /b 1
)
echo Go backend compiled successfully: um.exe

echo Step 2: Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 3: Packaging Python GUI with backend...
pyinstaller --onefile --windowed --add-binary "um.exe;." --name "UnlockMusicGUI" --hidden-import=tkinter --hidden-import=tkinter.scrolledtext gui_app.py
if errorlevel 1 (
    echo Failed to package GUI
    pause
    exit /b 1
)

echo Build completed successfully!
echo Output: dist\UnlockMusicGUI.exe
pause
