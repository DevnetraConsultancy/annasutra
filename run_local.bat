@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo        AnnaSutra - One-Click Localhost Runner
echo ========================================================
echo.

cd /d "%~dp0"

:: Detect Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py -3"
    ) else (
        echo [ERROR] Python 3.12+ was not found on your PATH.
        echo Please install Python 3.12 or higher from https://python.org
        pause
        exit /b 1
    )
)

:: Virtual environment setup
if not exist ".venv\Scripts\python.exe" (
    if exist "backend\venv\Scripts\python.exe" (
        set "VENV_PY=backend\venv\Scripts\python.exe"
    ) else (
        echo [1/4] Creating virtual environment (.venv)...
        %PY_CMD% -m venv .venv
        if %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Failed to create virtual environment.
            pause
            exit /b 1
        )
        set "VENV_PY=.venv\Scripts\python.exe"
        echo [2/4] Installing dependencies from requirements.txt...
        !VENV_PY! -m pip install --upgrade pip
        !VENV_PY! -m pip install -r requirements.txt
    )
) else (
    set "VENV_PY=.venv\Scripts\python.exe"
)

echo [3/4] Applying database migrations...
!VENV_PY! manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Database migration failed.
    pause
    exit /b 1
)

echo [4/4] Verifying administrative configuration...
!VENV_PY! manage.py seed_demo_data

echo.
echo ========================================================
echo   AnnaSutra is starting on http://localhost:8000/
echo   - Web Console:       http://localhost:8000/
echo   - Admin Panel:       http://localhost:8000/admin/ (admin / admin123)
echo   - Admin Gmail:       devnetraconsultancy@gmail.com
echo ========================================================
echo.

:: Launch browser in background
start "" "http://localhost:8000/"

:: Start Django server
!VENV_PY! manage.py runserver 127.0.0.1:8000
