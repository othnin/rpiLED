#!/usr/bin/env python3
"""
PySide6 GUI for controlling the WOPR LED service via IPC.
"""
import sys
import socket
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QGroupBox, QMessageBox,
    QSplitter, QStatusBar
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont


class WOPRControlGUI(QMainWindow):
    def __init__(self, socket_path="/tmp/wopr.sock"):
        super().__init__()
        self.socket_path = socket_path
        self.setWindowTitle("WOPR LED Control")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connection status label
        self.conn_status = QLabel("● Disconnected")
        self.conn_status.setStyleSheet("color: red; font-weight: bold;")
        
        # Current pattern display
        self.current_pattern_label = QLabel("Current Pattern: None")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.current_pattern_label.setFont(font)
        
        # Top section with status
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.conn_status)
        status_layout.addStretch()
        status_layout.addWidget(self.current_pattern_label)
        layout.addLayout(status_layout)
        
        # Create splitter for patterns and hooks
        splitter = QSplitter(Qt.Horizontal)
        
        # Patterns section
        patterns_group = QGroupBox("Available Patterns")
        patterns_layout = QVBoxLayout()
        self.patterns_list = QListWidget()
        self.patterns_list.itemDoubleClicked.connect(self.start_selected_pattern)
        patterns_layout.addWidget(self.patterns_list)
        
        patterns_btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Selected")
        self.start_btn.clicked.connect(self.start_selected_pattern)
        self.stop_btn = QPushButton("Stop Pattern")
        self.stop_btn.clicked.connect(self.stop_pattern)
        patterns_btn_layout.addWidget(self.start_btn)
        patterns_btn_layout.addWidget(self.stop_btn)
        patterns_layout.addLayout(patterns_btn_layout)
        
        patterns_group.setLayout(patterns_layout)
        splitter.addWidget(patterns_group)
        
        # Hooks section
        hooks_group = QGroupBox("Available Hooks")
        hooks_layout = QVBoxLayout()
        self.hooks_list = QListWidget()
        hooks_layout.addWidget(self.hooks_list)
        hooks_group.setLayout(hooks_layout)
        splitter.addWidget(hooks_group)
        
        layout.addWidget(splitter)
        
        # Startup patterns section
        startup_group = QGroupBox("Startup Configuration")
        startup_layout = QVBoxLayout()
        
        self.startup_list = QListWidget()
        startup_layout.addWidget(QLabel("Startup Patterns & Links:"))
        startup_layout.addWidget(self.startup_list)
        
        startup_btn_layout = QHBoxLayout()
        self.add_startup_btn = QPushButton("Add Selected to Startup")
        self.add_startup_btn.clicked.connect(self.add_to_startup)
        self.remove_startup_btn = QPushButton("Remove from Startup")
        self.remove_startup_btn.clicked.connect(self.remove_from_startup)
        startup_btn_layout.addWidget(self.add_startup_btn)
        startup_btn_layout.addWidget(self.remove_startup_btn)
        startup_layout.addLayout(startup_btn_layout)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh All")
        self.refresh_btn.clicked.connect(self.refresh_all)
        self.stop_all_btn = QPushButton("Stop All Patterns")
        self.stop_all_btn.clicked.connect(self.stop_all_patterns)
        control_layout.addWidget(self.refresh_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.stop_all_btn)
        layout.addLayout(control_layout)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
        # Initial refresh
        self.refresh_all()
    
    def send_ipc_command(self, action, params=None):
        """Send a command to the IPC server and return the response."""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            
            request = {"action": action}
            if params:
                request["params"] = params
            
            sock.sendall(json.dumps(request).encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            
            # Read response
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            
            sock.close()
            
            response = json.loads(data.decode("utf-8"))
            self.update_connection_status(True)
            return response
            
        except Exception as e:
            self.update_connection_status(False)
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)
            return {"ok": False, "error": str(e)}
    
    def update_connection_status(self, connected):
        """Update the connection status indicator."""
        if connected:
            self.conn_status.setText("● Connected")
            self.conn_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.conn_status.setText("● Disconnected")
            self.conn_status.setStyleSheet("color: red; font-weight: bold;")
    
    def refresh_all(self):
        """Refresh all data from the service."""
        self.refresh_patterns()
        self.refresh_hooks()
        self.refresh_status()
        self.refresh_startup()
    
    def refresh_patterns(self):
        """Refresh the list of available patterns."""
        response = self.send_ipc_command("list_patterns")
        if response.get("ok"):
            self.patterns_list.clear()
            patterns = response.get("result", [])
            self.patterns_list.addItems(sorted(patterns))
            self.status_bar.showMessage(f"Loaded {len(patterns)} patterns", 3000)
    
    def refresh_hooks(self):
        """Refresh the list of available hooks."""
        response = self.send_ipc_command("list_hooks")
        if response.get("ok"):
            self.hooks_list.clear()
            hooks = response.get("result", [])
            self.hooks_list.addItems(sorted(hooks))
    
    def refresh_status(self):
        """Refresh the current pattern status."""
        response = self.send_ipc_command("status")
        if response.get("ok"):
            result = response.get("result", {})
            current = result.get("current_pattern")
            if current:
                self.current_pattern_label.setText(f"Current Pattern: {current}")
                self.current_pattern_label.setStyleSheet("color: green;")
            else:
                self.current_pattern_label.setText("Current Pattern: None")
                self.current_pattern_label.setStyleSheet("color: gray;")
    
    def refresh_startup(self):
        """Refresh the startup patterns and links."""
        response = self.send_ipc_command("list_startup")
        if response.get("ok"):
            self.startup_list.clear()
            result = response.get("result", {})
            patterns = result.get("startup_patterns", [])
            links = result.get("startup_links", {})
            
            for pattern in patterns:
                self.startup_list.addItem(f"Pattern: {pattern}")
            
            for hook, pattern in links.items():
                self.startup_list.addItem(f"Hook Link: {hook} → {pattern}")
    
    def start_selected_pattern(self):
        """Start the selected pattern."""
        current = self.patterns_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a pattern to start.")
            return
        
        pattern_name = current.text()
        response = self.send_ipc_command("start_pattern", {"name": pattern_name})
        
        if response.get("ok"):
            self.status_bar.showMessage(f"Started pattern: {pattern_name}", 3000)
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to start pattern: {response.get('error')}")
    
    def stop_pattern(self):
        """Stop the current pattern."""
        response = self.send_ipc_command("stop_pattern")
        
        if response.get("ok"):
            self.status_bar.showMessage("Stopped current pattern", 3000)
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to stop pattern: {response.get('error')}")
    
    def stop_all_patterns(self):
        """Stop all patterns."""
        reply = QMessageBox.question(
            self, "Confirm", "Stop all running patterns?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            response = self.send_ipc_command("stop_all")
            if response.get("ok"):
                self.status_bar.showMessage("Stopped all patterns", 3000)
                self.refresh_status()
            else:
                QMessageBox.critical(self, "Error", f"Failed to stop patterns: {response.get('error')}")
    
    def add_to_startup(self):
        """Add selected pattern to startup."""
        current = self.patterns_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a pattern to add to startup.")
            return
        
        pattern_name = current.text()
        #response = self.send_ipc_command("register_startup", {"name": pattern_name})
        response = self.send_ipc_command("save_pattern", {"name": pattern_name})
        
        if response.get("ok"):
            self.status_bar.showMessage(f"Added {pattern_name} to startup", 3000)
            self.refresh_startup()
        else:
            QMessageBox.critical(self, "Error", f"Failed to register: {response.get('error')}")
    
    def remove_from_startup(self):
        """Remove selected item from startup."""
        current = self.startup_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a startup item to remove.")
            return
        
        text = current.text()
        # Extract pattern name from the display text
        if text.startswith("Pattern: "):
            pattern_name = text.replace("Pattern: ", "")
        elif text.startswith("Hook Link: "):
            # For hook links, extract the pattern name after the arrow
            pattern_name = text.split(" → ")[1] if " → " in text else None
        else:
            return
        
        if pattern_name:
            response = self.send_ipc_command("unregister_startup", {"name": pattern_name})
            if response.get("ok"):
                self.status_bar.showMessage(f"Removed {pattern_name} from startup", 3000)
                self.refresh_startup()
            else:
                QMessageBox.critical(self, "Error", f"Failed to unregister: {response.get('error')}")


def main():
    app = QApplication(sys.argv)
    window = WOPRControlGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()