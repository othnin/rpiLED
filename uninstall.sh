#!/bin/bash
#
# WOPR LED Control System Uninstaller
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="/opt/WOPR"
SERVICE_USER="${SUDO_USER:-$USER}"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

echo -e "${YELLOW}"
cat << "EOF"
╦ ╦╔═╗╔═╗╦═╗  ╦ ╦╔╗╔╦╔╗╔╔═╗╔╦╗╔═╗╦  ╦  ╔═╗╦═╗
║║║║ ║╠═╝╠╦╝  ║ ║║║║║║║║╚═╗ ║ ╠═╣║  ║  ║╣ ╠╦╝
╚╩╝╚═╝╩  ╩╚═  ╚═╝╝╚╝╩╝╚╝╚═╝ ╩ ╩ ╩╩═╝╩═╝╚═╝╩╚═
EOF
echo -e "${NC}"

log_warning "This will remove the WOPR LED Control System"
log_warning "Installation directory: $INSTALL_DIR"
echo

read -p "Are you sure you want to uninstall? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Uninstall cancelled"
    exit 0
fi

# Stop and disable service
log_info "Stopping service..."
systemctl stop wopr.service 2>/dev/null || true
systemctl disable wopr.service 2>/dev/null || true
rm -f /etc/systemd/system/wopr.service
systemctl daemon-reload

# Remove installation directory
log_info "Removing installation files..."
rm -rf "$INSTALL_DIR"

# Remove desktop files
log_info "Removing desktop shortcuts..."
rm -f /home/$SERVICE_USER/.local/share/applications/wopr-control.desktop
rm -f /home/$SERVICE_USER/Desktop/wopr-control.desktop

# Remove socket file
rm -f /tmp/wopr.sock

log_info "Uninstall complete!"
log_warning "Note: SPI interface and system packages were not removed"
log_warning "To disable SPI, remove 'dtparam=spi=on' from /boot/config.txt"

exit 0