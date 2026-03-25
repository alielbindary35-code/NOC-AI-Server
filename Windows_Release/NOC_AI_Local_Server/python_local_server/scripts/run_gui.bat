@echo off
setlocal enabledelayedexpansion
title NOC AI - Local Test GUI (Windows)

color 0B
echo =================================================
echo    NOC AI  -  Local Test GUI  (Windows)
echo =================================================
echo.

:: 1. Check Python
echo [INFO] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from python.org and check "Add to PATH".
    pause
    exit /b 1
)
echo [OK]   Python found.

:: 2. Create and Activate venv
set VENV_DIR=venv
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv %VENV_DIR%
)
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
echo [OK]   Activated.

:: 3. Install Dependencies
echo [INFO] Ensuring required dependencies are installed...
python -m pip install --upgrade pip >nul 2>&1
pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing 'requests' for Local AI Agent...
    pip install requests
)
echo [OK]   Dependencies ready.
echo.
echo ─────────────────────────────────────────────────

:: 4. Check and Setup Ollama (AI Agent)
set OLLAMA_MODEL=llama3.2:1b
echo [INFO] Checking AI Agent Engine (Ollama)...

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo [Notice] Ollama is NOT installed on this PC.
    echo Ollama is required to give your Local Server the EXACT same AI intelligence as the Production n8n server.
    echo Without it, the server will fallback to basic word-matching (Regex).
    echo.
    set /p INSTALL_CHOICE="Do you want to download and install Ollama automatically now? [y/N]: "
    
    if /i "!INSTALL_CHOICE!"=="y" (
        color 0B
        echo [INFO] Downloading Ollama setup... (this might take a minute)
        curl -L https://ollama.com/download/OllamaSetup.exe -o OllamaSetup.exe
        if exist OllamaSetup.exe (
            echo [INFO] Installing Ollama... Please wait.
            start /wait OllamaSetup.exe /S
            echo [OK]   Ollama installed successfully.
            del OllamaSetup.exe
            
            :: Wait a moment for Ollama to finish initializing
            timeout /t 5 >nul
        ) else (
            color 0C
            echo [ERROR] Download failed. Skipping AI setup.
            color 0B
        )
    ) else (
        echo [WARN] Skipping Ollama installation. Local Server will use Regex Fallback.
    )
    color 0B
)

:: If Ollama is installed (either previously or just now)
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    :: Ensure it's running (start silently if possible)
    start "" /b ollama serve >nul 2>&1
    
    :: Check for model
    ollama list | findstr /i "%OLLAMA_MODEL%" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [INFO] Pulling the lightweight AI model '%OLLAMA_MODEL%' for fast local reasoning...
        ollama pull %OLLAMA_MODEL%
        echo [OK]   Model ready!
    ) else (
        echo [OK]   AI Model '%OLLAMA_MODEL%' is ready.
    )
)

echo.
echo ─────────────────────────────────────────────────
echo [INFO] Launching NOC AI GUI...
echo ─────────────────────────────────────────────────
echo.

:: 5. Launch the GUI
python local_ai_gui.py

:: In case GUI crashes or exits, keep console open to read errors
pause
