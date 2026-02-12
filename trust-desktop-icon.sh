#!/bin/bash
# Trust the WOPR desktop icon
# Run this as the normal user (not sudo) if the desktop icon shows a prompt

echo "Trusting WOPR desktop icon..."

# Method 1: Using gio
gio set ~/Desktop/wopr-control.desktop metadata::trusted true 2>/dev/null && \
    echo "✓ Desktop icon trusted (method 1)" || \
    echo "✗ Method 1 failed"

# Method 2: Right-click method simulation
chmod 755 ~/Desktop/wopr-control.desktop 2>/dev/null && \
    echo "✓ Desktop icon permissions set (method 2)" || \
    echo "✗ Method 2 failed"

# Method 3: Using dbus-launch
dbus-launch gio set ~/Desktop/wopr-control.desktop metadata::trusted true 2>/dev/null && \
    echo "✓ Desktop icon trusted (method 3)" || \
    echo "✗ Method 3 failed"

echo ""
echo "Done! Try clicking the desktop icon now."
echo "If still prompted, right-click the icon and select 'Allow Launching' or 'Trust This File'"
