#!/bin/bash
cd /opt/WOPR/frontend
source venv/bin/activate
python3 src/wopr_gui.py
deactivate
