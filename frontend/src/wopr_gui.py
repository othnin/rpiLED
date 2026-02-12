#!/usr/bin/env python3
"""
PySide6 GUI for controlling the WOPR LED service via IPC.
Simplified layout with Test Patterns and Select Patterns sections.
"""
import sys
import socket
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QMessageBox, QStatusBar, QComboBox, QCheckBox, QSlider
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont


class WOPRControlGUI(QMainWindow):
    def __init__(self, socket_path="/tmp/wopr.sock"):
        super().__init__()
        self.socket_path = socket_path
        self.setWindowTitle("WOPR LED Control")
        self.setMinimumSize(700, 600)
        
        # Track state
        self.patterns = []  # List of available patterns
        self.hooks = []  # List of available hooks
        self.test_pattern_buttons = {}  # {pattern_name: (start_btn, stop_btn)}
        self.running_test_pattern = None  # Currently running test pattern
        
        # Create central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Left side: main content
        layout = QVBoxLayout()
        main_layout.addLayout(layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # ===== TOP SECTION: Status =====
        status_layout = QHBoxLayout()
        
        # Connection status label
        self.conn_status = QLabel("● Disconnected")
        self.conn_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.conn_status)
        
        status_layout.addStretch()
        
        # Current pattern display
        self.current_pattern_label = QLabel("Current Pattern: None")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.current_pattern_label.setFont(font)
        status_layout.addWidget(self.current_pattern_label)
        
        layout.addLayout(status_layout)
        
        # Running hooks display (aligned to the right, under Current Pattern)
        running_hooks_layout = QHBoxLayout()
        running_hooks_layout.addStretch()
        self.running_hooks_label = QLabel("Running Hooks: None")
        running_hooks_font = QFont()
        running_hooks_font.setPointSize(12)
        running_hooks_font.setBold(True)
        self.running_hooks_label.setFont(running_hooks_font)
        running_hooks_layout.addWidget(self.running_hooks_label)
        layout.addLayout(running_hooks_layout)
        
        layout.addSpacing(10)
        
        # ===== TEST PATTERNS SECTION =====
        test_group = QGroupBox()
        test_layout = QVBoxLayout()
        
        # Bold header
        test_header = QLabel("Test Patterns")
        test_header_font = QFont()
        test_header_font.setBold(True)
        test_header_font.setPointSize(11)
        test_header.setFont(test_header_font)
        test_layout.addWidget(test_header)
        
        # Container for pattern buttons (will be populated dynamically)
        self.test_patterns_container = QVBoxLayout()
        test_layout.addLayout(self.test_patterns_container)
        
        # Test Hook checkbox
        self.test_hook_checkbox = QCheckBox("Test Hook")
        self.test_hook_checkbox.stateChanged.connect(self.on_test_hook_changed)
        test_layout.addWidget(self.test_hook_checkbox)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addSpacing(20)
        
        # ===== SELECT PATTERNS SECTION =====
        select_group = QGroupBox()
        select_layout = QVBoxLayout()
        
        # Bold header
        select_header = QLabel("Select Patterns")
        select_header_font = QFont()
        select_header_font.setBold(True)
        select_header_font.setPointSize(11)
        select_header.setFont(select_header_font)
        select_layout.addWidget(select_header)
        
        select_layout.addSpacing(10)
        
        # Pattern dropdown
        pattern_select_layout = QHBoxLayout()
        pattern_select_layout.addWidget(QLabel("Pattern:"))
        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("(Select a pattern)")
        pattern_select_layout.addWidget(self.pattern_dropdown)
        pattern_select_layout.addStretch()
        select_layout.addLayout(pattern_select_layout)
        
        select_layout.addSpacing(10)
        
        # Configure Options subsection
        config_box = QGroupBox("Configure Options")
        config_layout = QVBoxLayout()
        
        # Hook type dropdown
        hook_select_layout = QHBoxLayout()
        hook_select_layout.addWidget(QLabel("Hook Type:"))
        self.hook_dropdown = QComboBox()
        self.hook_dropdown.addItem("(Select a hook)")
        hook_select_layout.addWidget(self.hook_dropdown)
        hook_select_layout.addStretch()
        config_layout.addLayout(hook_select_layout)
        
        config_layout.addSpacing(10)
        
        # OK button
        ok_btn_layout = QHBoxLayout()
        ok_btn_layout.addStretch()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 30px;")
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        ok_btn_layout.addWidget(self.ok_btn)
        ok_btn_layout.addStretch()
        config_layout.addLayout(ok_btn_layout)
        
        config_box.setLayout(config_layout)
        select_layout.addWidget(config_box)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        layout.addStretch()
        
        # ===== RIGHT SIDE: BRIGHTNESS CONTROL =====
        brightness_panel = QVBoxLayout()
        brightness_panel.addStretch()
        
        # Brightness label
        self.brightness_label = QLabel("Brightness: 100%")
        brightness_label_font = QFont()
        brightness_label_font.setBold(True)
        brightness_label_font.setPointSize(10)
        self.brightness_label.setFont(brightness_label_font)
        self.brightness_label.setAlignment(Qt.AlignCenter)
        brightness_panel.addWidget(self.brightness_label)
        
        brightness_panel.addSpacing(10)
        
        # Vertical brightness slider
        self.brightness_slider = QSlider(Qt.Vertical)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickPosition(QSlider.TicksRight)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.setMinimumHeight(300)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_panel.addWidget(self.brightness_slider)
        
        brightness_panel.addStretch()
        
        main_layout.addLayout(brightness_panel)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
        # Initial refresh
        self.refresh_all()
    
    def closeEvent(self, event):
        """Handle application close - stop any running test pattern and save brightness."""
        if self.running_test_pattern:
            self.send_ipc_command("stop_pattern")
        
        # Save current brightness
        current_brightness = self.brightness_slider.value()
        self.send_ipc_command("set_brightness", {"value": current_brightness})
        
        event.accept()
    
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
    
    def refresh_patterns(self):
        """Refresh the list of available patterns."""
        response = self.send_ipc_command("list_patterns")
        if response.get("ok"):
            self.patterns = sorted(response.get("result", []))
            self.populate_test_patterns()
            self.populate_pattern_dropdown()
            self.status_bar.showMessage(f"Loaded {len(self.patterns)} patterns", 3000)
    
    def refresh_hooks(self):
        """Refresh the list of available hooks."""
        response = self.send_ipc_command("list_hooks")
        if response.get("ok"):
            self.hooks = sorted(response.get("result", []))
            self.populate_hook_dropdown()
    
    def refresh_status(self):
        """Refresh the current pattern status and brightness."""
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
            
            # Update brightness slider from backend
            brightness = result.get("brightness", 100)
            self.brightness_slider.blockSignals(True)
            self.brightness_slider.setValue(brightness)
            self.brightness_label.setText(f"Brightness: {brightness}%")
            self.brightness_slider.blockSignals(False)
        
        # Refresh running hooks - show only hooks that have patterns linked
        response = self.send_ipc_command("list_persistent_links")
        if response.get("ok"):
            links = response.get("result", {})
            # Filter to only show hooks that have patterns (not null)
            active_hooks = [hook for hook, pattern in links.items() if pattern is not None]
            if active_hooks:
                self.running_hooks_label.setText(f"Running Hooks: {', '.join(active_hooks)}")
                self.running_hooks_label.setStyleSheet("color: green;")
            else:
                self.running_hooks_label.setText("Running Hooks: None")
                self.running_hooks_label.setStyleSheet("color: gray;")
    
    def populate_test_patterns(self):
        """Populate the test patterns section with individual Start/Stop buttons."""
        # Clear existing buttons
        while self.test_patterns_container.count():
            item = self.test_patterns_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
        self.test_pattern_buttons.clear()
        
        # Create a row for each pattern
        for pattern in self.patterns:
            row_layout = QHBoxLayout()
            
            # Pattern name label
            pattern_label = QLabel(pattern)
            pattern_label.setMinimumWidth(200)
            row_layout.addWidget(pattern_label)
            
            row_layout.addStretch()
            
            # Start button
            start_btn = QPushButton("Start")
            start_btn.setFixedWidth(80)
            start_btn.clicked.connect(lambda checked, p=pattern: self.start_test_pattern(p))
            row_layout.addWidget(start_btn)
            
            # Stop button
            stop_btn = QPushButton("Stop")
            stop_btn.setFixedWidth(80)
            stop_btn.setEnabled(False)
            stop_btn.clicked.connect(lambda checked, p=pattern: self.stop_test_pattern(p))
            row_layout.addWidget(stop_btn)
            
            self.test_patterns_container.addLayout(row_layout)
            self.test_pattern_buttons[pattern] = (start_btn, stop_btn)
    
    def clear_layout(self, layout):
        """Recursively clear a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
    
    def populate_pattern_dropdown(self):
        """Populate the pattern dropdown in Select Patterns section."""
        self.pattern_dropdown.blockSignals(True)
        current_text = self.pattern_dropdown.currentText()
        self.pattern_dropdown.clear()
        self.pattern_dropdown.addItem("(Select a pattern)")
        
        for pattern in self.patterns:
            self.pattern_dropdown.addItem(pattern)
        
        # Restore selection if it exists
        index = self.pattern_dropdown.findText(current_text)
        if index >= 0:
            self.pattern_dropdown.setCurrentIndex(index)
        
        self.pattern_dropdown.blockSignals(False)
    
    def populate_hook_dropdown(self):
        """Populate the hook dropdown in Configure Options."""
        self.hook_dropdown.blockSignals(True)
        current_text = self.hook_dropdown.currentText()
        self.hook_dropdown.clear()
        self.hook_dropdown.addItem("(Select a hook)")
        
        # Filter out test_trigger from the dropdown
        for hook in self.hooks:
            if hook != "test_trigger":
                self.hook_dropdown.addItem(hook)
        
        # Restore selection if it exists
        index = self.hook_dropdown.findText(current_text)
        if index >= 0:
            self.hook_dropdown.setCurrentIndex(index)
        
        self.hook_dropdown.blockSignals(False)
    
    def start_test_pattern(self, pattern_name):
        """Start a test pattern."""
        response = self.send_ipc_command("start_pattern", {"name": pattern_name})
        
        if response.get("ok"):
            self.running_test_pattern = pattern_name
            self.status_bar.showMessage(f"Started test pattern: {pattern_name}", 3000)
            
            # Update button states
            if pattern_name in self.test_pattern_buttons:
                start_btn, stop_btn = self.test_pattern_buttons[pattern_name]
                start_btn.setEnabled(False)
                stop_btn.setEnabled(True)
            
            # Disable all other start buttons
            for p, (start_btn, stop_btn) in self.test_pattern_buttons.items():
                if p != pattern_name:
                    start_btn.setEnabled(False)
            
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to start pattern: {response.get('error')}")
    
    def stop_test_pattern(self, pattern_name):
        """Stop a test pattern."""
        response = self.send_ipc_command("stop_pattern")
        
        if response.get("ok"):
            self.running_test_pattern = None
            self.status_bar.showMessage(f"Stopped test pattern: {pattern_name}", 3000)
            
            # Update button states - enable all start buttons, disable all stop buttons
            for p, (start_btn, stop_btn) in self.test_pattern_buttons.items():
                start_btn.setEnabled(True)
                stop_btn.setEnabled(False)
            
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to stop pattern: {response.get('error')}")
    
    def on_test_hook_changed(self, state):
        """Handle Test Hook checkbox state change."""
        if state == Qt.Checked:
            # Trigger test hook
            response = self.send_ipc_command("trigger_test_hook")
            if response.get("ok"):
                self.status_bar.showMessage("Test hook triggered", 3000)
            else:
                QMessageBox.critical(self, "Error", f"Failed to trigger test hook: {response.get('error')}")
                self.test_hook_checkbox.setChecked(False)
        # Note: Unchecking doesn't do anything special
    
    def on_brightness_changed(self, value):
        """Handle brightness slider change - update in real-time."""
        self.brightness_label.setText(f"Brightness: {value}%")
        
        # Send brightness update to backend immediately
        response = self.send_ipc_command("set_brightness", {"value": value})
        if not response.get("ok"):
            self.status_bar.showMessage(f"Failed to set brightness: {response.get('error')}", 3000)
    
    def on_ok_clicked(self):
        """Handle OK button click - save configuration and close app."""
        pattern_name = self.pattern_dropdown.currentText()
        hook_name = self.hook_dropdown.currentText()
        
        # Check if nothing is selected
        if pattern_name == "(Select a pattern)":
            # Nothing selected, just close the app
            self.close()
            return
        
        # Pattern is selected - determine if hook is also selected
        hook_selected = hook_name != "(Select a hook)"
        
        # Validate: if hook is selected, pattern must be selected (already validated above)
        # But we also need to check the reverse: if hook selected but no pattern
        if hook_selected and pattern_name == "(Select a pattern)":
            QMessageBox.warning(self, "Validation Error", "Please select a pattern to go with the hook.")
            return
        
        # CLEAR ALL EXISTING CONFIGURATIONS FIRST
        # This ensures only ONE configuration exists at a time
        
        # 1. Remove ALL hook links
        response = self.send_ipc_command("list_persistent_links")
        if response.get("ok"):
            existing_links = response.get("result", {})
            for existing_hook in list(existing_links.keys()):
                remove_response = self.send_ipc_command("remove_persistent_link", {
                    "hook_event_name": existing_hook
                })
                if not remove_response.get("ok"):
                    QMessageBox.critical(self, "Error", 
                        f"Failed to clear existing configuration: {remove_response.get('error')}")
                    return
        
        # 2. Remove ALL standalone patterns
        response = self.send_ipc_command("list_startup_patterns")
        if response.get("ok"):
            existing_standalone = response.get("result", [])
            for existing_pattern in existing_standalone:
                remove_response = self.send_ipc_command("remove_pattern_from_startup", {
                    "pattern_name": existing_pattern
                })
                if not remove_response.get("ok"):
                    QMessageBox.critical(self, "Error", 
                        f"Failed to clear existing configuration: {remove_response.get('error')}")
                    return
        
        # NOW SAVE THE NEW SINGLE CONFIGURATION
        if hook_selected:
            # Save as hook-linked pattern
            response = self.send_ipc_command("add_persistent_link", {
                "hook_event_name": hook_name,
                "pattern_name": pattern_name
            })
            
            if not response.get("ok"):
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {response.get('error')}")
                return
            
            # Save brightness before starting pattern
            current_brightness = self.brightness_slider.value()
            self.send_ipc_command("set_brightness", {"value": current_brightness})
            
            # Start the pattern immediately
            start_response = self.send_ipc_command("start_pattern", {"name": pattern_name})
            
            if start_response.get("ok"):
                QMessageBox.information(
                    self, "Success",
                    f"Configuration saved!\n\n"
                    f"Pattern: {pattern_name}\n"
                    f"Hook: {hook_name}\n"
                    f"Brightness: {current_brightness}%\n\n"
                    f"Pattern started and will run on reboot when the hook triggers."
                )
            else:
                QMessageBox.warning(
                    self, "Partial Success",
                    f"Configuration saved but failed to start pattern: {start_response.get('error')}"
                )
        else:
            # Save as standalone pattern
            response = self.send_ipc_command("add_pattern_to_startup", {
                "pattern_name": pattern_name
            })
            
            if not response.get("ok"):
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {response.get('error')}")
                return
            
            # Save brightness before starting pattern
            current_brightness = self.brightness_slider.value()
            self.send_ipc_command("set_brightness", {"value": current_brightness})
            
            # Start the pattern immediately
            start_response = self.send_ipc_command("start_pattern", {"name": pattern_name})
            
            if start_response.get("ok"):
                QMessageBox.information(
                    self, "Success",
                    f"Configuration saved!\n\n"
                    f"Pattern: {pattern_name}\n"
                    f"Brightness: {current_brightness}%\n\n"
                    f"Pattern started and will run on reboot."
                )
            else:
                QMessageBox.warning(
                    self, "Partial Success",
                    f"Configuration saved but failed to start pattern: {start_response.get('error')}"
                )
        
        # Close the application
        self.close()


def main():
    app = QApplication(sys.argv)
    window = WOPRControlGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
