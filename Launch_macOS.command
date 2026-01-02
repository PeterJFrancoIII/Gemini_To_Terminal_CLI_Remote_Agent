#!/bin/bash
cd "$(dirname "$0")"

# Create venv if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
echo "Installing/Updating requirements..."
pip install -r requirements.txt

# Run
echo "Starting Gemini Terminal Bridge..."
python3 gui_bridge.py
