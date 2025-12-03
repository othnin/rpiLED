#!/usr/bin/env python3
"""
PySide6 GUI for controlling the WOPR LED service via IPC.
Top section for testing patterns and hooks.
Bottom section for persistent startup configuration.
"""
import sys
import socket
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QGroupBox, QMessageBox,
    QSplitter, QStatusBar, QListWidgetItem, QComboBox
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont


class WOPRControlGUI(QMainWindow):
    def __init__(self, socket_path="/tmp/wopr.sock"):
        super().__init__()
        self.socket_path = socket_path
        self.setWindowTitle("WOPR LED Control")
        self.setMinimumSize(900, 700)
        
        # Track current configuration state
        self.current_pattern = None  # Currently selected pattern in dropdown
        self.hook_links = {}  # {hook_name: pattern_name}
        self.startup_patterns = []  # [pattern_names]
        
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
        
        # ===== TEST SECTION (Top) =====
        test_group = QGroupBox("Test Patterns & Hooks")
        test_layout = QVBoxLayout()
        
        # Splitter for patterns and hooks
        test_splitter = QSplitter(Qt.Horizontal)
        
        # Test Patterns
        patterns_group = QGroupBox("Available Patterns")
        patterns_layout = QVBoxLayout()
        self.test_patterns_list = QListWidget()
        self.test_patterns_list.itemDoubleClicked.connect(self.start_selected_pattern)
        patterns_layout.addWidget(self.test_patterns_list)
        
        patterns_btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_selected_pattern)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_pattern)
        patterns_btn_layout.addWidget(self.start_btn)
        patterns_btn_layout.addWidget(self.stop_btn)
        patterns_layout.addLayout(patterns_btn_layout)
        
        patterns_group.setLayout(patterns_layout)
        test_splitter.addWidget(patterns_group)
        
        # Test Hooks
        hooks_group = QGroupBox("Available Hooks (Test)")
        hooks_layout = QVBoxLayout()
        self.test_hooks_list = QListWidget()
        hooks_layout.addWidget(self.test_hooks_list)
        
        hook_btn_layout = QHBoxLayout()
        self.trigger_hook_btn = QPushButton("Trigger Selected Hook")
        self.trigger_hook_btn.clicked.connect(self.trigger_selected_hook)
        hook_btn_layout.addWidget(self.trigger_hook_btn)
        hooks_layout.addLayout(hook_btn_layout)
        
        hooks_group.setLayout(hooks_layout)
        test_splitter.addWidget(hooks_group)
        
        test_layout.addWidget(test_splitter)
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # ===== STARTUP CONFIGURATION SECTION (Bottom) =====
        startup_group = QGroupBox("Startup Configuration")
        startup_layout = QVBoxLayout()
        
        # Instructions
        startup_layout.addWidget(QLabel("Select how to start this pattern:"))
        startup_layout.addSpacing(5)
        
        # Startup mode selector (dropdown)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Pattern:"))
        
        self.startup_mode_dropdown = QComboBox()
        self.startup_mode_dropdown.addItem("(Select a pattern)")
        self.startup_mode_dropdown.currentIndexChanged.connect(self.on_startup_mode_changed)
        mode_layout.addWidget(self.startup_mode_dropdown)
        mode_layout.addSpacing(20)
        
        startup_layout.addLayout(mode_layout)
        startup_layout.addSpacing(10)
        
        # Configuration info box
        self.config_info_box = QGroupBox("Configuration Options")
        config_box_layout = QVBoxLayout()
        
        # Hook link option
        hook_option_layout = QHBoxLayout()
        self.hook_radio_label = QLabel("🔗 Hook Link:")
        self.hook_radio_label.setStyleSheet("font-weight: bold;")
        hook_option_layout.addWidget(self.hook_radio_label)
        
        self.hook_dropdown = QComboBox()
        self.hook_dropdown.addItem("(Select a hook)")
        hook_option_layout.addWidget(self.hook_dropdown)
        
        self.hook_start_btn = QPushButton("Start & Auto-start on Boot")
        self.hook_start_btn.setEnabled(False)
        self.hook_start_btn.clicked.connect(self.add_startup_link_with_start)
        self.hook_start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        hook_option_layout.addWidget(self.hook_start_btn)
        
        self.hook_remove_btn = QPushButton("Remove & Stop")
        self.hook_remove_btn.setEnabled(False)
        self.hook_remove_btn.clicked.connect(self.remove_startup_link_with_stop)
        self.hook_remove_btn.setStyleSheet("background-color: #f44336; color: white;")
        hook_option_layout.addWidget(self.hook_remove_btn)
        
        config_box_layout.addLayout(hook_option_layout)
        config_box_layout.addSpacing(10)
        
        # Standalone option
        standalone_option_layout = QHBoxLayout()
        self.standalone_radio_label = QLabel("⭐ Standalone:")
        self.standalone_radio_label.setStyleSheet("font-weight: bold;")
        standalone_option_layout.addWidget(self.standalone_radio_label)
        
        self.standalone_start_btn = QPushButton("Start & Auto-start on Boot")
        self.standalone_start_btn.setEnabled(False)
        self.standalone_start_btn.clicked.connect(self.add_pattern_to_startup_with_start)
        self.standalone_start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        standalone_option_layout.addWidget(self.standalone_start_btn)
        
        self.standalone_remove_btn = QPushButton("Remove & Stop")
        self.standalone_remove_btn.setEnabled(False)
        self.standalone_remove_btn.clicked.connect(self.remove_pattern_from_startup_with_stop)
        self.standalone_remove_btn.setStyleSheet("background-color: #f44336; color: white;")
        standalone_option_layout.addWidget(self.standalone_remove_btn)
        
        standalone_option_layout.addStretch()
        config_box_layout.addLayout(standalone_option_layout)
        
        self.config_info_box.setLayout(config_box_layout)
        startup_layout.addWidget(self.config_info_box)
        
        # Status info
        self.startup_status_label = QLabel("")
        self.startup_status_label.setStyleSheet("color: green; font-style: italic;")
        startup_layout.addWidget(self.startup_status_label)
        
        startup_layout.addStretch()
        
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
        self.refresh_startup_links()
    
    def refresh_patterns(self):
        """Refresh the list of available patterns."""
        response = self.send_ipc_command("list_patterns")
        if response.get("ok"):
            self.test_patterns_list.clear()
            patterns = response.get("result", [])
            self.test_patterns_list.addItems(sorted(patterns))
            self.status_bar.showMessage(f"Loaded {len(patterns)} patterns", 3000)
    
    def refresh_hooks(self):
        """Refresh the list of available hooks."""
        response = self.send_ipc_command("list_hooks")
        if response.get("ok"):
            self.test_hooks_list.clear()
            hooks = response.get("result", [])
            self.test_hooks_list.addItems(sorted(hooks))
    
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
    
    def refresh_startup_links(self):
        """Refresh the persistent startup links and patterns."""
        # Refresh hook-pattern links
        response = self.send_ipc_command("list_persistent_links")
        if response.get("ok"):
            self.hook_links = response.get("result", {})
        
        # Refresh standalone patterns
        response = self.send_ipc_command("list_startup_patterns")
        if response.get("ok"):
            self.startup_patterns = response.get("result", [])
        
        # Update pattern dropdown with all available patterns
        self.startup_mode_dropdown.blockSignals(True)
        current_text = self.startup_mode_dropdown.currentText()
        self.startup_mode_dropdown.clear()
        self.startup_mode_dropdown.addItem("(Select a pattern)")
        
        # Get all patterns
        response = self.send_ipc_command("list_patterns")
        if response.get("ok"):
            patterns = sorted(response.get("result", []))
            for pattern in patterns:
                self.startup_mode_dropdown.addItem(pattern)
        
        # Restore selection if it exists
        index = self.startup_mode_dropdown.findText(current_text)
        if index >= 0:
            self.startup_mode_dropdown.setCurrentIndex(index)
        
        self.startup_mode_dropdown.blockSignals(False)
        
        # Update hook dropdown
        response = self.send_ipc_command("list_hooks")
        if response.get("ok"):
            self.hook_dropdown.blockSignals(True)
            current_hook = self.hook_dropdown.currentText()
            self.hook_dropdown.clear()
            self.hook_dropdown.addItem("(Select a hook)")
            
            hooks = sorted(response.get("result", []))
            for hook in hooks:
                self.hook_dropdown.addItem(hook)
            
            # Restore selection if it exists
            index = self.hook_dropdown.findText(current_hook)
            if index >= 0:
                self.hook_dropdown.setCurrentIndex(index)
            
            self.hook_dropdown.blockSignals(False)
    
    def start_selected_pattern(self):
        """Start the selected pattern."""
        current = self.test_patterns_list.currentItem()
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
    
    def trigger_selected_hook(self):
        """Trigger the selected hook for testing."""
        current = self.test_hooks_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a hook to trigger.")
            return
        
        hook_name = current.text()
        
        # Special case for test hook
        if hook_name == "test_trigger":
            response = self.send_ipc_command("trigger_test_hook")
            if response.get("ok"):
                self.status_bar.showMessage(f"Triggered hook: {hook_name}", 3000)
            else:
                QMessageBox.critical(self, "Error", f"Failed to trigger hook: {response.get('error')}")
        else:
            QMessageBox.information(
                self, "Info", 
                f"The '{hook_name}' hook triggers automatically based on system conditions.\n"
                f"Use 'test_trigger' hook to manually test patterns."
            )
    
    def add_startup_link(self):
        """Add a persistent link from selected hook and pattern."""
        hook_item = self.test_hooks_list.currentItem()
        pattern_item = self.test_patterns_list.currentItem()
        
        if not hook_item:
            QMessageBox.warning(self, "No Hook Selected", "Please select a hook from the Available Hooks list.")
            return
        
        if not pattern_item:
            QMessageBox.warning(self, "No Pattern Selected", "Please select a pattern from the Available Patterns list.")
            return
        
        hook_event_name = hook_item.text()
        pattern_name = pattern_item.text()
        
        # Check if pattern is already in standalone
        response = self.send_ipc_command("list_startup_patterns")
        if response.get("ok"):
            standalone = response.get("result", [])
            if pattern_name in standalone:
                QMessageBox.warning(
                    self, "Conflict", 
                    f"Pattern '{pattern_name}' is already configured as Standalone.\n"
                    f"Remove it from Standalone first before adding as a Hook Link."
                )
                return
        
        response = self.send_ipc_command("add_persistent_link", {
            "hook_event_name": hook_event_name,
            "pattern_name": pattern_name
        })
        
        if response.get("ok"):
            self.status_bar.showMessage(f"Added hook link: {hook_event_name} → {pattern_name}", 3000)
            self.refresh_startup_links()
        else:
            QMessageBox.critical(self, "Error", f"Failed to add link: {response.get('error')}")
    
    def remove_startup_link(self):
        """Remove the selected persistent link."""
        current = self.startup_links_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a link to remove.")
            return
        
        text = current.text()
        if text == "(No hook links configured)":
            return
        
        # Extract hook event name (everything before the arrow)
        if " → " in text:
            hook_event_name = text.split(" → ")[0]
        else:
            return
        
        reply = QMessageBox.question(
            self, "Confirm", f"Remove link: {text}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            response = self.send_ipc_command("remove_persistent_link", {
                "hook_event_name": hook_event_name
            })
            
            if response.get("ok"):
                self.status_bar.showMessage(f"Removed link: {hook_event_name}", 3000)
                self.refresh_startup_links()
            else:
                QMessageBox.critical(self, "Error", f"Failed to remove link: {response.get('error')}")

    def add_pattern_to_startup(self):
        """Add a standalone pattern to startup (no hook required)."""
        pattern_item = self.test_patterns_list.currentItem()
        
        if not pattern_item:
            QMessageBox.warning(self, "No Pattern Selected", "Please select a pattern from the Available Patterns list.")
            return
        
        pattern_name = pattern_item.text()
        
        # Check if pattern is already in hook links
        response = self.send_ipc_command("list_persistent_links")
        if response.get("ok"):
            links = response.get("result", {})
            for hook_event, linked_pattern in links.items():
                if linked_pattern == pattern_name:
                    QMessageBox.warning(
                        self, "Conflict",
                        f"Pattern '{pattern_name}' is already linked to hook '{hook_event}'.\n"
                        f"Remove the hook link first before adding as Standalone."
                    )
                    return
        
        response = self.send_ipc_command("add_pattern_to_startup", {
            "pattern_name": pattern_name
        })
        
        if response.get("ok"):
            self.status_bar.showMessage(f"Added pattern to startup: {pattern_name}", 3000)
            self.refresh_startup_links()
        else:
            QMessageBox.critical(self, "Error", f"Failed to add pattern: {response.get('error')}")

    def remove_pattern_from_startup(self):
        """Remove a standalone pattern from startup."""
        current = self.startup_patterns_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a pattern to remove.")
            return
        
        pattern_name = current.text()
        if pattern_name == "(No standalone patterns configured)":
            return
        
        reply = QMessageBox.question(
            self, "Confirm", f"Remove pattern from startup: {pattern_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            response = self.send_ipc_command("remove_pattern_from_startup", {
                "pattern_name": pattern_name
            })
            
            if response.get("ok"):
                self.status_bar.showMessage(f"Removed pattern from startup: {pattern_name}", 3000)
                self.refresh_startup_links()
            else:
                QMessageBox.critical(self, "Error", f"Failed to remove pattern: {response.get('error')}")

    def on_startup_mode_changed(self):
        """Handle pattern selection from dropdown - update configuration options."""
        pattern_name = self.startup_mode_dropdown.currentText()
        
        if pattern_name == "(Select a pattern)":
            self.hook_start_btn.setEnabled(False)
            self.hook_remove_btn.setEnabled(False)
            self.standalone_start_btn.setEnabled(False)
            self.standalone_remove_btn.setEnabled(False)
            self.startup_status_label.setText("")
            return
        
        self.current_pattern = pattern_name
        
        # Check if pattern is in hook links
        is_in_hook_links = any(p == pattern_name for p in self.hook_links.values())
        
        # Check if pattern is in standalone
        is_in_standalone = pattern_name in self.startup_patterns
        
        # Update status label
        if is_in_hook_links:
            hook_name = [h for h, p in self.hook_links.items() if p == pattern_name][0]
            self.startup_status_label.setText(
                f"✓ Currently linked to {hook_name} and auto-starts on boot"
            )
            self.hook_remove_btn.setEnabled(True)
            self.hook_start_btn.setEnabled(False)
            self.hook_start_btn.setText("Start & Auto-start on Boot")
            self.standalone_start_btn.setEnabled(False)
            self.standalone_remove_btn.setEnabled(False)
            self.standalone_start_btn.setText("Start & Auto-start on Boot")
        elif is_in_standalone:
            self.startup_status_label.setText(
                f"✓ Currently standalone and auto-starts on boot"
            )
            self.standalone_remove_btn.setEnabled(True)
            self.standalone_start_btn.setEnabled(False)
            self.standalone_start_btn.setText("Start & Auto-start on Boot")
            self.hook_start_btn.setEnabled(False)
            self.hook_remove_btn.setEnabled(False)
            self.hook_start_btn.setText("Start & Auto-start on Boot")
        else:
            self.startup_status_label.setText(f"Not configured yet")
            self.hook_start_btn.setEnabled(True)
            self.hook_start_btn.setText("Start & Auto-start on Boot")
            self.standalone_start_btn.setEnabled(True)
            self.standalone_start_btn.setText("Start & Auto-start on Boot")
            self.hook_remove_btn.setEnabled(False)
            self.standalone_remove_btn.setEnabled(False)

    def add_startup_link_with_start(self):
        """Add hook link and immediately start the pattern."""
        if not self.current_pattern:
            QMessageBox.warning(self, "No Pattern", "Please select a pattern first.")
            return
        
        hook_name = self.hook_dropdown.currentText()
        if hook_name == "(Select a hook)":
            QMessageBox.warning(self, "No Hook", "Please select a hook.")
            return
        
        pattern_name = self.current_pattern
        
        # Check if pattern is already in standalone
        if pattern_name in self.startup_patterns:
            QMessageBox.warning(
                self, "Conflict",
                f"Pattern '{pattern_name}' is already configured as Standalone.\n"
                f"Remove it first to add as Hook Link."
            )
            return
        
        # Add persistent link
        response = self.send_ipc_command("add_persistent_link", {
            "hook_event_name": hook_name,
            "pattern_name": pattern_name
        })
        
        if not response.get("ok"):
            QMessageBox.critical(self, "Error", f"Failed to add link: {response.get('error')}")
            return
        
        # Start the pattern immediately
        response = self.send_ipc_command("start_pattern", {"name": pattern_name})
        
        if response.get("ok"):
            self.status_bar.showMessage(
                f"✓ Started {pattern_name} (linked to {hook_name}, auto-starts on boot)", 5000
            )
            self.hook_start_btn.setText("✓ Running")
            self.hook_start_btn.setEnabled(False)
            self.hook_remove_btn.setEnabled(True)
            self.refresh_startup_links()
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to start pattern: {response.get('error')}")

    def remove_startup_link_with_stop(self):
        """Remove hook link and stop the pattern."""
        if not self.current_pattern:
            return
        
        pattern_name = self.current_pattern
        hook_name = [h for h, p in self.hook_links.items() if p == pattern_name]
        
        if not hook_name:
            QMessageBox.warning(self, "Not Found", f"Pattern not linked to any hook.")
            return
        
        hook_name = hook_name[0]
        
        reply = QMessageBox.question(
            self, "Confirm",
            f"Remove '{pattern_name}' from hook link and stop it?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Remove link
        response = self.send_ipc_command("remove_persistent_link", {
            "hook_event_name": hook_name
        })
        
        if not response.get("ok"):
            QMessageBox.critical(self, "Error", f"Failed to remove link: {response.get('error')}")
            return
        
        # Stop pattern
        response = self.send_ipc_command("stop_pattern")
        
        if response.get("ok"):
            self.status_bar.showMessage(f"Removed hook link and stopped pattern", 3000)
            self.hook_start_btn.setText("Start & Auto-start on Boot")
            self.hook_remove_btn.setEnabled(False)
            self.hook_start_btn.setEnabled(True)
            self.refresh_startup_links()
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to stop pattern: {response.get('error')}")

    def add_pattern_to_startup_with_start(self):
        """Add standalone pattern and immediately start it."""
        if not self.current_pattern:
            QMessageBox.warning(self, "No Pattern", "Please select a pattern first.")
            return
        
        pattern_name = self.current_pattern
        
        # Check if pattern is already in hook links
        if any(p == pattern_name for p in self.hook_links.values()):
            QMessageBox.warning(
                self, "Conflict",
                f"Pattern '{pattern_name}' is already linked to a hook.\n"
                f"Remove the hook link first to add as Standalone."
            )
            return
        
        # Add to startup
        response = self.send_ipc_command("add_pattern_to_startup", {
            "pattern_name": pattern_name
        })
        
        if not response.get("ok"):
            QMessageBox.critical(self, "Error", f"Failed to add pattern: {response.get('error')}")
            return
        
        # Start the pattern immediately
        response = self.send_ipc_command("start_pattern", {"name": pattern_name})
        
        if response.get("ok"):
            self.status_bar.showMessage(
                f"✓ Started {pattern_name} (standalone, auto-starts on boot)", 5000
            )
            self.standalone_start_btn.setText("✓ Running")
            self.standalone_start_btn.setEnabled(False)
            self.standalone_remove_btn.setEnabled(True)
            self.refresh_startup_links()
        else:
            QMessageBox.critical(self, "Error", f"Failed to start pattern: {response.get('error')}")

    def remove_pattern_from_startup_with_stop(self):
        """Remove standalone pattern and stop it."""
        if not self.current_pattern:
            return
        
        pattern_name = self.current_pattern
        
        if pattern_name not in self.startup_patterns:
            QMessageBox.warning(self, "Not Found", f"Pattern not in standalone configuration.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm",
            f"Remove '{pattern_name}' from startup and stop it?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Remove from startup
        response = self.send_ipc_command("remove_pattern_from_startup", {
            "pattern_name": pattern_name
        })
        
        if not response.get("ok"):
            QMessageBox.critical(self, "Error", f"Failed to remove pattern: {response.get('error')}")
            return
        
        # Stop pattern
        response = self.send_ipc_command("stop_pattern")
        
        if response.get("ok"):
            self.status_bar.showMessage(f"Removed pattern from startup and stopped it", 3000)
            self.standalone_start_btn.setText("Start & Auto-start on Boot")
            self.standalone_remove_btn.setEnabled(False)
            self.standalone_start_btn.setEnabled(True)
            self.refresh_startup_links()
        else:
            QMessageBox.critical(self, "Error", f"Failed to stop pattern: {response.get('error')}")



def main():
    app = QApplication(sys.argv)
    window = WOPRControlGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()