#!/usr/bin/env bash
# AnnaSutra: One-Click Localhost Runner (macOS / Linux)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "========================================================"
echo "       AnnaSutra - One-Click Localhost Runner"
echo "========================================================"
echo ""

# Detect Python 3.12+
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3.12+ was not found on your PATH."
    echo "Please install Python 3.12 or higher from https://python.org"
    exit 1
fi

# Virtual environment setup
if [ ! -f ".venv/bin/python" ]; then
    if [ -f "backend/venv/bin/python" ]; then
        VENV_PY="backend/venv/bin/python"
    else
        echo "[1/4] Creating virtual environment (.venv)..."
        "$PY_CMD" -m venv .venv
        VENV_PY=".venv/bin/python"
        echo "[2/4] Installing dependencies from requirements.txt..."
        "$VENV_PY" -m pip install --upgrade pip
        "$VENV_PY" -m pip install -r requirements.txt
    fi
else
    VENV_PY=".venv/bin/python"
fi

echo "[3/4] Applying database migrations..."
"$VENV_PY" manage.py migrate --noinput

echo "[4/4] Verifying administrative configuration..."
"$VENV_PY" manage.py seed_demo_data

echo ""
echo "========================================================"
echo "  AnnaSutra is starting on http://localhost:8000/"
echo "  - Web Console:       http://localhost:8000/"
echo "  - Admin Panel:       http://localhost:8000/admin/ (admin / admin123)"
echo "  - Admin Gmail:       devnetraconsultancy@gmail.com"
echo "========================================================"
echo ""

# Attempt to open browser across platforms
if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:8000/" &>/dev/null &
elif command -v open &>/dev/null; then
    open "http://localhost:8000/" &>/dev/null &
fi

# Start Django server
"$VENV_PY" manage.py runserver 127.0.0.1:8000
