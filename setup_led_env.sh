#!/bin/bash
# setup_led_env.sh
# Creates a virtual environment called "venv" and installs required packages.

set -e  # Exit on error

echo "=== Creating Python virtual environment: venv ==="
python3 -m venv venv

echo "=== Activating virtual environment ==="
source  venv/bin/activate

echo "=== Upgrading pip inside the venv ==="
pip install --upgrade pip

echo "=== Installing requirements ==="
pip install -r src/requirements.txt




echo ""
echo "✅ Installation complete!"
echo "To activate this environment later, run:"
echo "    source venv/bin/activate"
echo ""
echo "When activated, run your scripts with:"
echo "    python your_script.py"
echo ""
echo "Deactivate the venv anytime with:"
echo "    deactivate"