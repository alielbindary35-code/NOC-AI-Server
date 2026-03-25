@echo off
setlocal enabledelayedexpansion
title NOC AI - Local Test GUI (Windows)

color 0B
echo =================================================
echo    NOC AI  -  Local Test GUI  (Windows)
echo =================================================
echo.

:: 1. Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from python.org and check "Add to PATH".
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version') do set PY_VER=%%v
echo [OK]   Python found: %PY_VER%

:: 2. Create and Activate venv
set VENV_DIR=venv
echo [2/5] Setting up Virtual Environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment [first time]...
    python -m venv %VENV_DIR%
    if !errorlevel! neq 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK]   Virtual environment created.
)
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    color 0C
    echo [ERROR] Failed to activate environment.
    pause
    exit /b 1
)
echo [OK]   Activated.

:: 3. Install Dependencies
echo [3/5] Checking Dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required libraries ('requests')...
    pip install requests
    if !errorlevel! neq 0 (
        color 0C
        echo [ERROR] Failed to install dependencies. Check your internet connection.
        pause
        exit /b 1
    )
)
echo [OK]   Dependencies ready.
echo.
echo ─────────────────────────────────────────────────

:: 4. Check and Setup Ollama (AI Agent)
set OLLAMA_MODEL=llama3.2:1b
echo [4/5] Checking AI Agent Engine (Ollama)...

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo [Notice] Ollama is NOT detected in your system path.
    echo Ollama allows your Local Server to have high-level AI reasoning.
    echo.
    set /p INSTALL_CHOICE="Do you want to download and install Ollama automatically now? [y/N]: "
    
    if /i "!INSTALL_CHOICE!"=="y" (
        color 0B
        echo [INFO] Downloading Ollama setup... [please wait]
        curl -L https://ollama.com/download/OllamaSetup.exe -o OllamaSetup.exe
        if exist OllamaSetup.exe (
            echo [INFO] Starting Ollama Installer...
            echo        Please follow the installer prompts and FINISH the installation.
            start /wait OllamaSetup.exe
            echo [INFO] Cleaning up...
            del OllamaSetup.exe
            
            echo [INFO] Verifying installation...
            timeout /t 3 >nul
            REM Try to find it again, might need full path if PATH hasn't updated
            where ollama >nul 2>&1
            if !errorlevel! neq 0 (
                if exist "%LocalAppData%\Ollama\ollama.exe" (
                    set "PATH=%PATH%;%LocalAppData%\Ollama"
                    echo [OK]   Ollama found in LocalAppData.
                ) else (
                    color 0C
                    echo [WARN] Ollama was installed but is not yet in your PATH.
                    echo        You might need to restart this window after setup.
                )
            )
        ) else (
            color 0C
            echo [ERROR] Download failed. Check your internet connection.
            color 0B
        )
    ) else (
        echo [WARN] Skipping Ollama. Local Server will use Regex Fallback.
    )
    color 0B
) else (
    echo [OK]   Ollama is already installed.
)

:: If Ollama is available
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Starting Ollama server (background)...
    start "" /b ollama serve >nul 2>&1
    
    echo [INFO] Checking for AI Model '%OLLAMA_MODEL%'...
    ollama list | findstr /i "%OLLAMA_MODEL%" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [INFO] Pulling '%OLLAMA_MODEL%'... [this only happens once]
        ollama pull %OLLAMA_MODEL%
        echo [OK]   Model ready!
    ) else (
        echo [OK]   AI Model is ready.
    )
)

echo.
echo ─────────────────────────────────────────────────
echo [5/5] Launching NOC AI GUI...
echo ─────────────────────────────────────────────────
echo.

:: 5. Launch the GUI
python local_ai_gui.py
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] The GUI exited with an error (Code: %errorlevel%).
    echo If you see a 'ModuleNotFoundError', try deleting the 'venv' folder and running again.
)

echo.
echo Setup script finished.
pause
