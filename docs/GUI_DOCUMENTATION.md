# GUI Documentation - Complete User & Developer Guide

## GUI Overview

The WOPR GUI (`wopr_gui.py`) is a PySide6 application that provides a user-friendly interface for:
- Testing patterns
- Triggering hooks
- Configuring boot auto-start
- Monitoring system status

## User Interface Layout

```
╔════════════════════════════════════════════════════════════════════╗
║  WOPR LED Control                                                  ║
║  ● Connected              Current Pattern: knight_rider            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Test Patterns & Hooks                                            ║
║  ┌──────────────────────┐ ┌──────────────────────┐               ║
║  │ Available Patterns   │ │ Available Hooks      │               ║
║  │                      │ │                      │               ║
║  │ • knight_rider       │ │ • cpu_monitor        │               ║
║  │ • loading_bar        │ │ • disk_monitor       │               ║
║  │ • my_cool_pattern    │ │ • cpu_temp           │               ║
║  │ • (more...)          │ │ • mem_monitor        │               ║
║  │                      │ │ • test_trigger       │               ║
║  │ [Start] [Stop]       │ │ • voltage_monitor    │               ║
║  │                      │ │                      │               ║
║  │                      │ │ [Trigger Selected]   │               ║
║  └──────────────────────┘ └──────────────────────┘               ║
║                                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║  Startup Configuration                                             ║
║  Select how to start this pattern:                                ║
║                                                                    ║
║  Pattern: [Select a pattern ▼]                                   ║
║                                                                    ║
║  ╔─ Configuration Options ──────────────────────────────────────┐ ║
║  ║  🔗 Hook Link: [Select hook ▼]                             ║ ║
║  ║                [Start & Auto-start] [Remove & Stop]        ║ ║
║  ║                                                              ║ ║
║  ║  ⭐ Standalone:    [Start & Auto-start] [Remove & Stop]     ║ ║
║  ║                                                              ║ ║
║  ╚──────────────────────────────────────────────────────────────╝ ║
║                                                                    ║
║  (Status: Not configured yet)                                     ║
║                                                                    ║
║  [Refresh All]               [Stop All Patterns]                 ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

## Section Breakdown

### Top: Connection & Status Bar

**Connection Status** (top left):
- Green ● Connected - Service is running, socket available
- Red ● Disconnected - Can't reach service
- Updates every time GUI sends command

**Current Pattern** (top right):
- Shows which pattern is currently running
- Updates every 2 seconds
- Green text if running, gray if none

### Test Section: Patterns

**Purpose**: Quickly test patterns without configuration

**How to Use**:
1. Click pattern name in "Available Patterns" list
2. Click [Start] to run it
3. Double-click pattern also starts it
4. Click [Stop] to stop running pattern

**Features**:
- Double-click shortcut for quick start
- Multiple patterns listed
- Start/Stop buttons below list

### Test Section: Hooks

**Purpose**: Test hooks to verify alert system works

**How to Use**:
1. Click hook name in "Available Hooks" list
2. Click [Trigger Selected Hook] to manually trigger it
3. Watch pattern color change if a pattern is linked

**Note**: Most hooks trigger automatically based on system conditions. Only "test_trigger" is manual.

### Startup Configuration: Pattern Selector

**Purpose**: Choose which pattern to configure

**How it Works**:
1. Click dropdown to see all available patterns
2. Select one pattern
3. Configuration options below become active
4. Status shows current configuration for selected pattern

**Behavior**:
- Dropdown preserves selection when you refresh
- (Select a pattern) is placeholder
- All running patterns available

### Startup Configuration: Hook Link Option (🔗)

**Purpose**: Link pattern to system event for auto-response + boot auto-start

**What it Does**:
- When you click "Start & Auto-start on Boot":
  1. Links hook to pattern (saved to disk)
  2. Starts pattern immediately
  3. Pattern will auto-start on next boot
  4. Pattern will change color when hook triggers

**How to Use**:
1. Select pattern from top dropdown
2. Select a hook from "🔗 Hook Link" dropdown
3. Click "Start & Auto-start on Boot"
4. Pattern starts immediately and status shows link

**Button States**:
- "Start & Auto-start on Boot" (green) - Ready to configure
- "✓ Running" (green, disabled) - Pattern is linked and running
- "Remove & Stop" (red) - Click to remove link and stop pattern

**Example**:
- Select "loading_bar" pattern
- Select "cpu_monitor" hook
- Click "Start & Auto-start on Boot"
- Pattern starts immediately
- Status: "✓ Currently linked to cpu_monitor and auto-starts on boot"
- Next reboot: Pattern auto-starts
- When CPU rises: Pattern color changes to orange/red

### Startup Configuration: Standalone Option (⭐)

**Purpose**: Pattern auto-starts on boot without hook integration

**What it Does**:
- When you click "Start & Auto-start on Boot":
  1. Adds pattern to startup list (saved to disk)
  2. Starts pattern immediately
  3. Pattern will auto-start on next boot
  4. Pattern runs standalone (no hook integration)

**How to Use**:
1. Select pattern from top dropdown
2. Click "Start & Auto-start on Boot" (in Standalone section)
3. Pattern starts immediately and status shows it's configured

**Button States**:
- "Start & Auto-start on Boot" (green) - Ready to configure
- "✓ Running" (green, disabled) - Pattern is standalone and running
- "Remove & Stop" (red) - Click to remove from startup and stop pattern

**Example**:
- Select "knight_rider" pattern
- Click "Start & Auto-start on Boot" (Standalone)
- Pattern starts immediately
- Status: "✓ Currently standalone and auto-starts on boot"
- Next reboot: Pattern auto-starts

### Status Display

**Shows Current Configuration**:
- "Not configured yet" - Pattern not set up for auto-start
- "✓ Currently linked to [hook] and auto-starts on boot" - Hook link active
- "✓ Currently standalone and auto-starts on boot" - Standalone active

**Updates When**:
- You select different pattern
- You add/remove configuration
- You refresh

### Bottom Buttons

**Refresh All** (left):
- Reloads all data from service
- Useful if config changed externally
- Preserves current pattern selection

**Stop All Patterns** (right):
- Stops all running patterns
- Confirmation dialog appears
- Doesn't change persistent configuration

## Workflows

### Workflow 1: Test a Pattern Quickly

```
1. Find pattern in "Available Patterns" list
2. Click pattern name to select it
3. Click [Start] button
4. Pattern runs and LEDs animate
5. Watch the animation
6. Click [Stop] to stop
```

**Time**: ~5 seconds  
**Result**: Pattern runs, nothing saved  

---

### Workflow 2: Configure Pattern to Auto-Start on Boot (Standalone)

```
1. Click pattern dropdown at top
2. Select pattern you want
3. Click "⭐ Start & Auto-start on Boot" button
4. ✓ Pattern starts immediately
5. ✓ Configured to start on next boot
6. ✓ Status shows configuration
```

**Time**: ~2 seconds  
**Result**: Pattern starts now AND on every future boot  
**Persistent**: Yes - survives reboot

---

### Workflow 3: Link Pattern to System Event (CPU, Memory, etc.)

```
1. Click pattern dropdown at top
2. Select pattern (e.g., "loading_bar")
3. Select hook from "🔗 Hook Link" dropdown (e.g., "cpu_monitor")
4. Click "🔗 Start & Auto-start on Boot" button
5. ✓ Pattern starts immediately
6. ✓ Pattern linked to hook (saved to disk)
7. ✓ Will auto-start on boot
8. Now when CPU changes: Pattern color changes
```

**Time**: ~2 seconds  
**Result**: Pattern responds to system events + auto-starts on boot  
**Persistent**: Yes - link survives reboot  

---

### Workflow 4: Test Hook Alert System

```
1. Start a pattern (test workflow #1)
2. Find "test_trigger" in Available Hooks
3. Click it to select
4. Click [Trigger Selected Hook]
5. Watch pattern respond if linked
   (If linked to hook: color might change)
```

**Time**: ~3 seconds  
**Result**: Verify alert system working  

---

### Workflow 5: Remove Auto-Start Configuration

```
1. Click pattern dropdown
2. Select the configured pattern
3. Status shows current configuration
4. Click "Remove & Stop" button (red) in appropriate section
5. Confirmation dialog - click Yes
6. ✓ Pattern stops immediately
7. ✓ Configuration removed
8. ✓ Won't auto-start on next boot
```

**Time**: ~2 seconds  

---

### Workflow 6: Reboot and Verify Auto-Start

```
1. Configure pattern for auto-start (workflow #2 or #3)
2. Click [Refresh All] to confirm saved
3. Reboot system: sudo reboot
4. System boots...
5. LEDs show configured pattern(s) running automatically
6. ✓ Auto-start working!
```

## Color Indicators

### Connection Status (Top Left)
- **● Green**: Connected to service
- **● Red**: Disconnected (service not running)

### Pattern Label (Top Right)
- **Green Text**: Pattern currently running
- **Gray Text**: No pattern running

### Status Text (Startup Section)
- **Green Italic**: Configuration active

### Buttons
- **Green Buttons**: "Start & Auto-start" action buttons
- **Red Buttons**: "Remove & Stop" (destructive actions)
- **Gray Buttons**: Disabled (not applicable now)

## Tips & Tricks

### Quick Pattern Testing
- Double-click pattern name to start it immediately
- Faster than click + [Start] button

### Keyboard Navigation
- Tab through dropdown and buttons
- Space/Enter to activate buttons
- Arrow keys in dropdowns to select

### Verify Configuration
- Click pattern dropdown to see what's configured
- Status label shows current state
- Use [Refresh All] to sync with disk if changed externally

### Troubleshooting Connection

If shows "● Disconnected":
1. Check if service running: `systemctl --user status wopr`
2. Check if socket exists: `ls -la /tmp/wopr.sock`
3. Restart service: `systemctl --user restart wopr`

## Developer Information

### GUI Class: `WOPRControlGUI`

**Initialization**: 
- Creates all UI elements
- Connects signals to handlers
- Starts 2-second refresh timer

**Main Components**:
- Status bar, connection indicator
- Pattern test list with controls
- Hook test list with controls
- Startup configuration with dropdown
- Control buttons (Refresh, Stop All)

### Key Methods

**IPC Communication**:
```python
def send_ipc_command(action, params=None)
# Sends command to IPC server, handles errors
# Returns {"ok": bool, "result": data, "error": message}
```

**Refresh Methods**:
```python
def refresh_patterns()      # Populate pattern lists
def refresh_hooks()         # Populate hook list
def refresh_status()        # Update current pattern display
def refresh_startup_links() # Update startup config display
def refresh_all()          # Call all refresh methods
```

**Pattern Control**:
```python
def start_selected_pattern()  # Start test pattern
def stop_pattern()            # Stop current pattern
def stop_all_patterns()       # Stop all patterns
```

**Startup Configuration**:
```python
def on_startup_mode_changed()             # Pattern dropdown changed
def add_startup_link_with_start()         # Configure hook link
def remove_startup_link_with_stop()       # Remove hook link
def add_pattern_to_startup_with_start()   # Configure standalone
def remove_pattern_from_startup_with_stop() # Remove standalone
```

### State Tracking

```python
self.current_pattern           # Currently selected pattern
self.hook_links                # {hook_name: pattern_name}
self.startup_patterns          # [pattern_names]
```

### Button Enable/Disable Logic

**When no pattern selected**:
- All buttons disabled

**When pattern not configured**:
- Both "Start & Auto-start" buttons enabled
- Both "Remove & Stop" buttons disabled

**When pattern in hook link**:
- Hook "Start" button shows "✓ Running" (disabled)
- Hook "Remove" button enabled
- Standalone buttons all disabled

**When pattern standalone**:
- Standalone "Start" button shows "✓ Running" (disabled)
- Standalone "Remove" button enabled
- Hook buttons all disabled

### IPC Actions Called

**Startup**:
- `list_patterns`
- `list_hooks`
- `status`
- `list_persistent_links`
- `list_startup_patterns`

**Testing**:
- `start_pattern`
- `stop_pattern`
- `trigger_test_hook`
- `status`

**Configuration**:
- `add_persistent_link`
- `remove_persistent_link`
- `add_pattern_to_startup`
- `remove_pattern_from_startup`
- `list_persistent_links`
- `list_startup_patterns`

**Refresh**:
- `status` (every 2 seconds)

### Error Handling

**Connection Errors**:
- Caught in `send_ipc_command()`
- Updates connection status to red
- Shows error message in status bar
- Continues operation (retries on next command)

**Validation Errors**:
- Hook dropdown "must select" warning
- Pattern dropdown "must select" warning
- Conflict warnings (pattern in both modes)

**Operation Errors**:
- Critical dialogs for failed operations
- Preserves UI state
- Can retry

### Styling

**Colors**:
- Green buttons: `#4CAF50` (start actions)
- Red buttons: `#f44336` (stop actions)
- Connection green: `color: green`
- Connection red: `color: red`

**Fonts**:
- Current Pattern label: 12pt, bold
- Status text: Green, italic

**Layout**:
- Main window: 900x700 minimum
- Splitter for test section (resizable)
- Stretch factors for flexible layout

## Extension Points

### Add New Pattern
1. Create file in `backend/src/patterns/`
2. Inherit from `PatternBase`
3. Implement `run(led_manager, alert_queue=None)`
4. Pattern auto-appears in GUI list

### Add New Hook
1. Create file in `backend/src/hooks/`
2. Inherit from `SystemEventHook`
3. Implement `get_message()`
4. Hook auto-appears in GUI list

### Add GUI Feature
1. Add widget to appropriate section
2. Connect signal to handler method
3. Update refresh methods if needed
4. Follow existing patterns for consistency

## Common Issues

### Buttons Not Responding
- Check connection status (should be green)
- Check pattern selected (dropdown not "(Select...)")
- Try [Refresh All]
- Check service running: `pgrep -f run_service`

### Pattern Not Starting
- Check pattern name is valid
- Check service has permissions
- Check /dev/spidev0.0 exists (LED hardware)
- Check service logs: `journalctl --user -u wopr`

### Configuration Not Persisting
- Check /opt/WOPR/backend/data/ writable
- Check hooks_links.json and startup_patterns.json exist
- Try [Refresh All] after configuration
- Reboot to verify persistence

### Status Not Updating
- Refresh timer runs every 2 seconds
- Force refresh: Click [Refresh All]
- Check `status` action works: `printf '{"action":"status"}' | socat - UNIX-CONNECT:/tmp/wopr.sock`

## Next Steps

- See `ARCHITECTURE.md` for system design
- See `IPC_ACTIONS_REFERENCE.md` for all available actions
- See `BEGINNER_GUIDE.md` for user overview
