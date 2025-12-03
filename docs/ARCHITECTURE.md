# WOPR LED Control System - Architecture Guide

## System Overview

WOPR is a distributed LED control system with three main layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (GUI)                           │
│                   wopr_gui.py                               │
│  (PySide6 - User selects patterns and configurations)       │
└────────────────────┬────────────────────────────────────────┘
                     │ IPC Commands (JSON over Unix socket)
                     │ /tmp/wopr.sock
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 IPC SERVER LAYER                             │
│            (ipc_server.py)                                  │
│  - Listens on /tmp/wopr.sock                               │
│  - Routes GUI commands to backend                          │
│  - Returns results to GUI                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ Function Calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND CONTROL LAYER                        │
│            (backend.py, run_service.py)                    │
│  - PatternManager orchestrates all operations              │
│  - Handles pattern lifecycle                               │
│  - Manages hook system                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   ┌─────────────┐          ┌──────────────┐
   │   PATTERNS  │          │ HOOKS+ALERTS │
   │             │          │              │
   │ • knight_   │          │ • cpu_       │
   │   rider     │          │   monitor    │
   │ • loading_  │          │ • disk_      │
   │   bar       │          │   monitor    │
   │ • my_cool_  │          │ • cpu_temp   │
   │   pattern   │          │ • mem_       │
   │             │          │   monitor    │
   │             │          │ • voltage_   │
   │             │          │   monitor    │
   └─────────────┘          └──────────────┘
        │                          │
        │ (animate LEDs)           │ (monitor system)
        │                          │
        └────────────┬─────────────┘
                     ▼
            ┌─────────────────┐
            │   LED Strip     │
            │  (NeoPixels)    │
            └─────────────────┘
```

## Component Details

### 1. Frontend: GUI (`wopr_gui.py`)

**Purpose**: User interface for controlling patterns and configuring auto-start

**Key Components**:
- Pattern list and test controls
- Hook list for testing
- Startup configuration with dropdown selector
- Status displays

**User Interactions**:
- Select patterns to test
- Trigger hooks manually
- Configure hook→pattern links
- Configure standalone auto-start patterns
- View current pattern and connection status

**IPC Actions Called**:
- `list_patterns` - Get available patterns
- `list_hooks` - Get available hooks
- `start_pattern` - Start a pattern immediately
- `stop_pattern` - Stop current pattern
- `stop_all` - Stop all patterns
- `trigger_test_hook` - Manually trigger test hook
- `status` - Get current pattern status
- `add_persistent_link` - Link hook to pattern for auto-start
- `remove_persistent_link` - Remove hook link
- `add_pattern_to_startup` - Configure pattern for standalone auto-start
- `remove_pattern_from_startup` - Remove from auto-start
- `list_persistent_links` - Get configured hook links
- `list_startup_patterns` - Get configured standalone patterns

### 2. IPC Server Layer (`ipc_server.py`)

**Purpose**: JSON-RPC interface over Unix domain socket

**Socket**: `/tmp/wopr.sock`

**Protocol**: JSON request/response

**Request Format**:
```json
{
  "action": "action_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response Format**:
```json
{
  "ok": true/false,
  "result": {...},
  "error": "error message if ok=false"
}
```

**Supported Actions** (22 total):

#### Pattern Control
- `start_pattern` - Start a pattern by name
- `stop_pattern` - Stop current pattern
- `stop_all` - Stop all patterns
- `status` - Get current pattern status
- `list_patterns` - List all available patterns

#### Hook Management
- `list_hooks` - List all available hooks
- `trigger_test_hook` - Manually trigger test hook for testing
- `list_hook_states` - Get current state of all hooks

#### Persistent Configuration
- `add_persistent_link` - Link hook to pattern (hook_event_name, pattern_name)
- `remove_persistent_link` - Remove hook link (hook_event_name)
- `list_persistent_links` - List all hook→pattern links
- `add_pattern_to_startup` - Add pattern to boot auto-start (pattern_name)
- `remove_pattern_from_startup` - Remove from boot auto-start (pattern_name)
- `list_startup_patterns` - List patterns configured for auto-start

#### System Management
- `debug_status` - Get detailed debug info
- `reload_config` - Reload configuration from disk

### 3. Backend Control Layer

#### `backend.py` - Core Pattern Management

**PatternManager Class**:
```python
class PatternManager:
    def __init__(self, base_dir)
    
    # Pattern control
    def start_pattern(name)      # Start pattern by name
    def stop_pattern()            # Stop current pattern
    def get_status()              # Get current pattern info
    def get_pattern(name)         # Get pattern object
    
    # Hook management
    def get_hook(name)            # Get hook object
    def check_hooks()             # Check all hooks for alerts
    
    # Persistent storage
    def save_hook_links()         # Save links to disk
    def load_hook_links()         # Load links from disk
    def get_hook_links()          # Get current links
```

**Alert System** (`hook_alerts.py`):
- `AlertLevel` enum: NORMAL, WARNING, CRITICAL
- `HookMessage` class: Carries hook→pattern alerts
- Color mapping: NORMAL=green, WARNING=orange, CRITICAL=red

**Pattern Base Class**:
```python
class PatternBase:
    def run(self, led_manager, alert_queue=None)
    # alert_queue: Optional queue for receiving HookMessage objects
    # Pattern reads from queue to change colors based on system alerts
```

**Hook Base Class**:
```python
class SystemEventHook:
    def get_message(self)         # Generate HookMessage if alert triggered
    # Returns HookMessage with alert level and color
```

#### `run_service.py` - Service Loop

**Responsibilities**:
1. Load configuration from persistent storage
2. Start configured patterns at boot
3. Manage pattern lifecycle during service runtime
4. Check hooks periodically for alerts
5. Route hook alerts to running patterns

**Main Loop**:
```
while True:
    1. Check if current pattern should stop
    2. Let current pattern animate one frame
    3. Check hooks for alert changes (every 500ms)
    4. Send alerts to pattern's queue if running
    5. Sleep briefly
```

**Alert Routing**:
```
Hook detects change → generates HookMessage
                   ↓
PatternManager.check_hooks() finds message
                   ↓
Routes to pattern's alert_queue
                   ↓
Pattern reads queue and changes color
                   ↓
LEDs update with new color
```

## Data Flow Examples

### Example 1: User Starts a Pattern from GUI

```
User clicks "Start" button in test section
        ↓
GUI sends IPC command: start_pattern(name="knight_rider")
        ↓
IPC Server receives and calls:
  PatternManager.start_pattern("knight_rider")
        ↓
Backend:
  1. Loads pattern module
  2. Creates pattern instance
  3. Starts animation thread
        ↓
IPC Server returns: {"ok": true, "result": {"pattern": "knight_rider"}}
        ↓
GUI updates status label: "Current Pattern: knight_rider"
        ↓
LEDs animate with pattern
```

### Example 2: User Configures Hook Link

```
User selects pattern "loading_bar" from dropdown
User selects hook "cpu_monitor" from dropdown
User clicks "🔗 Start & Auto-start on Boot"
        ↓
GUI sends IPC: add_persistent_link(
  hook_event_name="cpu_monitor",
  pattern_name="loading_bar"
)
        ↓
IPC Server calls:
  PatternManager.add_hook_link("cpu_monitor", "loading_bar")
        ↓
Backend:
  1. Saves link to persistent storage (hook_links.json)
  2. Links are loaded on next boot
        ↓
GUI sends IPC: start_pattern(name="loading_bar")
        ↓
Backend starts pattern immediately
        ↓
GUI updates: "✓ Currently linked to cpu_monitor and auto-starts on boot"
```

### Example 3: Hook Alert Triggered at Runtime

```
Background: Pattern "loading_bar" running with cpu_monitor linked
        ↓
run_service loop calls: PatternManager.check_hooks()
        ↓
cpu_monitor detects CPU > 75% threshold (CRITICAL)
        ↓
hook.get_message() returns:
  HookMessage(
    level=AlertLevel.CRITICAL,
    color=(255, 0, 0),  # Red
    hook_name="cpu_monitor"
  )
        ↓
Alert added to pattern's alert_queue
        ↓
Pattern's run() method checks queue and reads message
        ↓
Pattern changes animation color from default to RED
        ↓
LEDs show red animation indicating high CPU
```

### Example 4: System Boot with Auto-Start

```
System boots → run_service.py starts
        ↓
1. Load persistent configuration
   - hook_links = {cpu_monitor: loading_bar}
   - startup_patterns = [knight_rider]
        ↓
2. Start configured patterns
   - Start "loading_bar" (will respond to cpu_monitor)
   - Start "knight_rider" (standalone)
        ↓
3. Enter main loop
   - Animate current patterns
   - Check hooks for alerts
   - Route alerts to patterns
```

## File Organization

```
/opt/WOPR/
├── backend/
│   ├── src/
│   │   ├── backend.py           # PatternManager (core control)
│   │   ├── run_service.py       # Service loop
│   │   ├── ipc_server.py        # IPC server
│   │   ├── hook_alerts.py       # Alert system
│   │   ├── config.py            # Configuration
│   │   ├── hooks/
│   │   │   ├── cpu_monitor.py   # CPU alert hook
│   │   │   ├── disk_monitor.py  # Disk alert hook
│   │   │   ├── cpu_temp.py      # CPU temp hook
│   │   │   ├── mem_monitor.py   # Memory hook
│   │   │   └── voltage_monitor.py # Voltage hook
│   │   └── patterns/
│   │       ├── knight_rider.py  # Knight Rider animation
│   │       ├── loading_bar.py   # Loading bar animation
│   │       └── my_cool_pattern.py # Custom animation
│   └── systemd/
│       └── wopr.service         # Systemd service
│
├── frontend/
│   └── src/
│       └── wopr_gui.py          # PySide6 GUI
│
└── data/
    └── hook_links.json          # Persistent hook configuration
    └── startup_patterns.json    # Persistent pattern configuration
```

## Communication Protocols

### Socket Communication (GUI ↔ IPC Server)

**Protocol**: JSON-RPC over Unix domain socket

**Socket Path**: `/tmp/wopr.sock`

**How it works**:
1. GUI connects to socket
2. Sends JSON request
3. Waits for JSON response
4. Closes socket

**Example**:
```python
# GUI sends
{"action": "start_pattern", "params": {"name": "knight_rider"}}

# IPC Server responds
{"ok": true, "result": {"pattern": "knight_rider", "started": true}}
```

### Alert Queue (Hook → Pattern)

**Type**: Thread-safe queue

**Message Format**: `HookMessage` object
- `level`: AlertLevel enum (NORMAL, WARNING, CRITICAL)
- `color`: RGB tuple (r, g, b)
- `hook_name`: Which hook triggered alert
- `value`: Current system value (e.g., CPU percentage)

**How it works**:
1. Pattern is started with alert_queue parameter
2. Pattern.run() receives queue reference
3. During animation, pattern checks queue
4. Reads HookMessage if available
5. Updates animation color accordingly

### Persistent Storage

**Files**: JSON format

**hook_links.json**:
```json
{
  "cpu_monitor": "loading_bar",
  "disk_monitor": "knight_rider",
  "mem_monitor": "my_cool_pattern"
}
```

**startup_patterns.json**:
```json
[
  "knight_rider",
  "my_cool_pattern"
]
```

**Loading**: 
- On service start, run_service.py loads both files
- Starts configured patterns
- Loads hook links for alert routing

## Thread Management

**Main Thread**: `run_service.py` loop
- Animates current pattern
- Checks hooks
- Manages LED updates

**Pattern Thread**: Each running pattern gets its own thread
- Runs pattern animation loop
- Updates LEDs
- Responsive to stop/pause requests

**IPC Server Thread**: Always listening for commands
- Handles GUI requests
- Returns responses immediately
- Non-blocking

## Error Handling

**IPC Level**: 
- Returns `{"ok": false, "error": "error message"}`
- GUI displays error dialog

**Backend Level**:
- Pattern fails to load: Falls back to safe state
- Hook fails to check: Skips that hook, logs error
- IPC connection lost: Gracefully reconnects on next request

## Security Considerations

**Local Only**: Unix domain socket (no network exposure)

**File Permissions**: 
- Socket created with mode 0o666 (anyone can connect)
- On single-user RPi this is acceptable
- For multi-user: Restrict with proper permissions

**Input Validation**:
- IPC server validates action names
- Parameters validated before use
- Pattern names validated before loading

## Performance Characteristics

**Latency**:
- GUI command → Response: <100ms
- Hook check → Alert delivery: <1 frame (typically 16-33ms)
- Pattern start: <50ms

**Resource Usage**:
- Each pattern: ~5-10MB memory
- Service idle: <10MB
- IPC socket: Negligible overhead

**Scalability**:
- Supports 3-5 simultaneous patterns (RPi limitation)
- 5+ hooks checking continuously
- 1000+ alert messages/sec possible

## Extension Points

**Adding a New Pattern**:
1. Create file in `backend/src/patterns/`
2. Inherit from `PatternBase`
3. Implement `run(led_manager, alert_queue=None)`
4. Pattern auto-discovered at runtime

**Adding a New Hook**:
1. Create file in `backend/src/hooks/`
2. Inherit from `SystemEventHook`
3. Implement `get_message()`
4. Hook auto-discovered at runtime

**Adding IPC Action**:
1. Add handler in `ipc_server.py`
2. Follow `handle_action_name()` pattern
3. Return `{"ok": bool, "result": data}`

## Troubleshooting

**GUI can't connect**:
- Check if service running: `pgrep -f run_service`
- Check socket exists: `ls -la /tmp/wopr.sock`
- Check permissions: `ls -la /tmp/wopr.sock`

**Patterns not responding to alerts**:
- Check hook is linked: `curl /tmp/wopr.sock with list_persistent_links`
- Check hook is checking: Monitor `debug_status` output
- Check pattern receives queue: Add debug prints

**Service crashes on boot**:
- Check logs: `journalctl --user -u wopr -n 50`
- Check Python syntax: `python -m py_compile *.py`
- Check imports: Run `python -c "import backend"`

**LED colors wrong**:
- Check alert levels in hook_alerts.py
- Verify pattern uses alert colors
- Check LED strip configuration

## Next Steps

- See `BEGINNER_GUIDE.md` for user-friendly overview
- See `IPC_ACTIONS_REFERENCE.md` for all API details
- See `GUI_DOCUMENTATION.md` for GUI feature guide
