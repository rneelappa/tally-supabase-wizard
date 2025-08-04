#!/usr/bin/env bash
set -e

LOGFILE="install_log.txt"
echo "==== Tally Supabase Wizard Install Log ====" > "$LOGFILE"

# Check for Python 3.11+
PYTHON_CMD=""
for cmd in python3.11 python3 python; do
    if command -v $cmd >/dev/null 2>&1; then
        VERSION=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ "$VERSION" == "3.11" || "$VERSION" > "3.11" ]]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo "Python 3.11+ not found. Attempting to install..." | tee -a "$LOGFILE"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            brew install python@3.11 | tee -a "$LOGFILE"
        else
            echo "Homebrew not found. Please install Homebrew or Python 3.11+ manually." | tee -a "$LOGFILE"
            exit 1
        fi
    elif command -v apt >/dev/null 2>&1; then
        sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-distutils | tee -a "$LOGFILE"
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y python3.11 | tee -a "$LOGFILE"
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y python3.11 | tee -a "$LOGFILE"
    else
        echo "No supported package manager found. Please install Python 3.11+ manually." | tee -a "$LOGFILE"
        exit 1
    fi
    PYTHON_CMD="python3.11"
fi

# Ensure pip is installed
$PYTHON_CMD -m ensurepip --upgrade || true

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip | tee -a "$LOGFILE"

# Install Python dependencies
$PYTHON_CMD -m pip install -r requirements.txt | tee -a "$LOGFILE"

# Launch the wizard
echo "Launching Tally Supabase Wizard..." | tee -a "$LOGFILE"
$PYTHON_CMD tally_supabase_wizard.py