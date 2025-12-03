# Component Interaction Guide

## How Components Talk to Each Other

This document explains the exact flow of how GUI, IPC Server, Backend, Hooks, and Patterns interact.

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│                     GUI (wopr_gui.py)                  │
│         User clicks buttons and makes selections       │
└────────────────┬───────────────────────────────────────┘
                 │
                 │ JSON over Unix Socket (/tmp/wopr.sock)
                 │ {"action": "...", "params": {...}}
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│              IPC Server (ipc_server.py)                │
│    Receives JSON commands, routes to backend, replies  │
└────────────────┬───────────────────────────────────────┘
                 │
                 │ Direct Function Calls
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│            Backend (backend.py + run_service.py)       │
│         PatternManager orchestrates everything         │
└────────┬──────────────┬──────────────┬────────────────┘
         │              │              │
         │              │              │
    ┌────▼─────┐  ┌────▼──────┐  ┌───▼──────────┐
    │ Patterns │  │   Hooks   │  │ Persistent  │
    │          │  │  + Alerts │  │ Storage     │
    │ Load     │  │           │  │             │
    │ Animate  │  │ Monitor   │  │ • Links     │
    │ Update   │  │ Check     │  │ • Patterns  │
    │ LEDs     │  │ Generate  │  │             │
    │          │  │ Alerts    │  │ (JSON files)│
    └──────────┘  └───────────┘  └─────────────┘
         │
         │ SPI Bus
         │
         ▼
    ┌─────────────┐
    │ LED Strip   │
    └─────────────┘
```

## Detailed Interaction Flows

### Flow 1: User Starts a Pattern (Quick Test)

```
┌─────────────────────────────────────────────────────────────────┐
│ USER ACTION: Click pattern → Click [Start] button              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ GUI (wopr_gui.py)                                               │
│ - User clicks [Start]                                           │
│ - start_selected_pattern() called                               │
│ - Gets pattern name from test_patterns_list                     │
│ - Creates IPC request: {                                        │
│     "action": "start_pattern",                                  │
│     "params": {"name": "knight_rider"}                          │
│   }                                                              │
│ - Connects to /tmp/wopr.sock                                    │
│ - Sends JSON request                                            │
│ - Waits for response                                            │
└─────────────────────────────────────────────────────────────────┘
                            │
         JSON over Unix Socket /tmp/wopr.sock
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ IPC SERVER (ipc_server.py)                                      │
│ - Listening on /tmp/wopr.sock                                   │
│ - Receives JSON: {"action": "start_pattern", "params": {...}}   │
│ - Validates action exists                                       │
│ - Validates parameters                                          │
│ - Calls handler: handle_start_pattern("knight_rider")           │
│ - Handler calls backend                                         │
└─────────────────────────────────────────────────────────────────┘
                            │
                     Function Call
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (backend.py)                                            │
│ - PatternManager.start_pattern("knight_rider") called           │
│ - Loads pattern module:                                         │
│   from patterns.knight_rider import KnightRider                 │
│ - Creates instance: pattern = KnightRider()                     │
│ - Creates AlertQueue for this pattern                           │
│ - Starts pattern thread:                                        │
│   thread = Thread(target=pattern.run,                           │
│     args=(led_manager, alert_queue))                            │
│ - Returns {"ok": true, "pattern": "knight_rider"}               │
└─────────────────────────────────────────────────────────────────┘
                            │
                Response JSON
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ IPC SERVER (ipc_server.py)                                      │
│ - Receives result from backend                                  │
│ - Returns JSON response:                                        │
│   {                                                              │
│     "ok": true,                                                 │
│     "result": {                                                 │
│       "pattern": "knight_rider",                                │
│       "started": true                                           │
│     }                                                            │
│   }                                                              │
│ - Closes socket connection                                      │
└─────────────────────────────────────────────────────────────────┘
                            │
         JSON Response on /tmp/wopr.sock
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ GUI (wopr_gui.py)                                               │
│ - Receives response: {"ok": true, "result": {...}}              │
│ - Calls refresh_status() to show current pattern                │
│ - Updates status bar: "Pattern started: knight_rider"           │
│ - Updates "Current Pattern" label to "knight_rider"             │
│ - Connection status already shows "Connected"                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    USER SEES:
                LEDs animating with knight_rider
                Status shows "Current Pattern: knight_rider"
```

### Flow 2: User Configures Hook Link with Auto-Start

```
┌─────────────────────────────────────────────────────────────────┐
│ USER ACTION: Select pattern → Select hook → Click Start button │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ GUI (wopr_gui.py)                                               │
│ - User selects "loading_bar" from pattern dropdown              │
│   → on_startup_mode_changed() called                            │
│   → Displays status, enables buttons                            │
│                                                                  │
│ - User selects "cpu_monitor" from hook dropdown                 │
│   → hook_start_btn enabled                                      │
│                                                                  │
│ - User clicks "🔗 Start & Auto-start on Boot"                   │
│   → add_startup_link_with_start() called                        │
│   → Validates hook selected (not "(Select a hook)")             │
│   → Validates pattern selected (self.current_pattern)           │
│   → Validates pattern not in startup_patterns already           │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
        Step 1: SEND ADD_PERSISTENT_LINK COMMAND
┌─────────────────────────────────────────────────────────────────┐
│ GUI (wopr_gui.py) - send_ipc_command()                          │
│ - Creates request:                                              │
│   {                                                              │
│     "action": "add_persistent_link",                            │
│     "params": {                                                 │
│       "hook_event_name": "cpu_monitor",                         │
│       "pattern_name": "loading_bar"                             │
│     }                                                            │
│   }                                                              │
│ - Connects to /tmp/wopr.sock                                    │
│ - Sends JSON request                                            │
└─────────────────────────────────────────────────────────────────┘
                            │
                     JSON over Socket
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ IPC SERVER (ipc_server.py) - handle_add_persistent_link()       │
│ - Receives action and parameters                                │
│ - Calls: PatternManager.add_hook_link(                          │
│       "cpu_monitor", "loading_bar"                              │
│   )                                                              │
│ - Returns {"ok": true, "result": {...}}                         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (backend.py) - PatternManager.add_hook_link()           │
│ - Validates hook name exists                                    │
│ - Validates pattern name exists                                 │
│ - Adds to hook_links dict:                                      │
│   hook_links["cpu_monitor"] = "loading_bar"                     │
│ - Saves to persistent storage:                                  │
│   save_hook_links() writes hook_links.json                      │
│ - File content:                                                 │
│   {                                                              │
│     "cpu_monitor": "loading_bar"                                │
│   }                                                              │
│ - Returns success                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                     Disk Write (json file)
                            │
                            ▼
        Step 2: SEND START_PATTERN COMMAND
┌─────────────────────────────────────────────────────────────────┐
│ GUI (wopr_gui.py) - add_startup_link_with_start()               │
│ - After link created, sends second command:                     │
│   {                                                              │
│     "action": "start_pattern",                                  │
│     "params": {"name": "loading_bar"}                           │
│   }                                                              │
│ - Connects to /tmp/wopr.sock                                    │
│ - Sends JSON request                                            │
└─────────────────────────────────────────────────────────────────┘
                            │
                     JSON over Socket
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ IPC SERVER (ipc_server.py) - handle_start_pattern()             │
│ - Receives "start_pattern" action                               │
│ - Calls: PatternManager.start_pattern("loading_bar")            │
│ - Returns {"ok": true, "result": {...}}                         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (backend.py) - PatternManager.start_pattern()           │
│ - Loads pattern: from patterns.loading_bar import LoadingBar    │
│ - Creates instance: pattern = LoadingBar()                      │
│ - Creates AlertQueue for this pattern                           │
│ - Starts pattern thread:                                        │
│   Thread(target=pattern.run,                                    │
│     args=(led_manager, alert_queue))                            │
│                                                                  │
│ - IMPORTANT: Pattern thread loops forever calling:              │
│   while True:                                                   │
│       - Check alert_queue for HookMessage                       │
│       - If message: update color from message                   │
│       - Animate one frame                                       │
│       - Update LEDs                                             │
│       - Sleep briefly                                           │
└─────────────────────────────────────────────────────────────────┘
                            │
                Response JSON
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ GUI (wopr_gui.py) - add_startup_link_with_start()               │
│ - Response: {"ok": true, "result": {...}}                       │
│ - Updates UI:                                                   │
│   - hook_start_btn.setText("✓ Running")                         │
│   - hook_start_btn.setEnabled(False)                            │
│   - hook_remove_btn.setEnabled(True)                            │
│   - startup_status_label shows linked status                    │
│   - Status bar: "✓ Started loading_bar (linked to cpu_monitor..)"│
│ - Calls refresh_status() → updates "Current Pattern" label      │
│ - Calls refresh_startup_links() → syncs state                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    USER SEES:
        • LEDs animating with loading_bar pattern
        • "Current Pattern: loading_bar"
        • Button shows "✓ Running"
        • Status: "✓ Currently linked to cpu_monitor..."
        • Auto-start configured (survives reboot)
```

### Flow 3: Runtime Alert from Hook to Pattern

```
Precondition: Pattern "loading_bar" running with cpu_monitor linked

┌─────────────────────────────────────────────────────────────────┐
│ RUN_SERVICE.PY - Main Service Loop                              │
│ while True:                                                     │
│   1. Animate current pattern (loading_bar.run())                │
│   2. Every 500ms:                                               │
│      manager.check_hooks()                                      │
│   3. Sleep briefly                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                Every 500ms: manager.check_hooks() called
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (backend.py) - PatternManager.check_hooks()             │
│ - For each hook:                                                │
│   1. Call hook.get_message()                                    │
│   2. If message returned: route to pattern's queue              │
│                                                                  │
│ - For cpu_monitor hook:                                         │
│   cpu = os.getloadavg()[0] / os.cpu_count()                     │
│   = 75.2%                                                       │
│                                                                  │
│   if cpu > 75:                                                  │
│       level = AlertLevel.CRITICAL                               │
│       color = (255, 0, 0)  # Red                                │
│   elif cpu > 50:                                                │
│       level = AlertLevel.WARNING                                │
│       color = (255, 165, 0)  # Orange                           │
│   else:                                                         │
│       level = AlertLevel.NORMAL                                 │
│       color = (0, 255, 0)  # Green                              │
│                                                                  │
│   message = HookMessage(                                        │
│       level=AlertLevel.CRITICAL,                                │
│       color=(255, 0, 0),                                        │
│       hook_name="cpu_monitor",                                  │
│       value=75.2                                                │
│   )                                                              │
│                                                                  │
│   return message  # ← Hook returns message                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                   Message returned
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (backend.py) - check_hooks() continued                  │
│ - Looks up which pattern linked to cpu_monitor:                 │
│   hook_links = {"cpu_monitor": "loading_bar"}                   │
│ - Finds linked pattern: "loading_bar"                           │
│ - Gets pattern's alert_queue                                    │
│ - Puts message in queue:                                        │
│   alert_queue.put(message)                                      │
│                                                                  │
│ - Returns, function ends                                        │
└─────────────────────────────────────────────────────────────────┘
                            │
           Message in Pattern's Alert Queue
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ PATTERN THREAD (patterns/loading_bar.py)                        │
│ - Running in separate thread                                    │
│ - Main loop in run() method:                                    │
│                                                                  │
│   while not stop_requested:                                     │
│       # Check for alerts from hooks                             │
│       if alert_queue:                                           │
│           try:                                                  │
│               message = alert_queue.get_nowait()                │
│               # Message contains color from hook                │
│               self.current_color = message.color                │
│           except:                                               │
│               pass  # No message available                      │
│                                                                  │
│       # Animate one frame using current_color                   │
│       self.animate_frame(led_manager)                           │
│                                                                  │
│       # Update physical LEDs                                    │
│       led_manager.update()                                      │
│                                                                  │
│       sleep(0.033)  # ~30fps                                    │
│                                                                  │
│ - Color changed to RED from message                             │
│ - Next frames animate with red color                            │
│ - LEDs immediately show red animation                           │
└─────────────────────────────────────────────────────────────────┘
                            │
                      SPI Bus Signal
                            │
                            ▼
                    ┌─────────────────┐
                    │  LED Strip      │
                    │  Shows RED!     │
                    └─────────────────┘
                            │
                            ▼
                    USER SEES:
            Animation color changed from previous
            to RED, showing CPU usage is high
            (happens automatically, very fast)
```

### Flow 4: System Boot with Auto-Start

```
┌─────────────────────────────────────────────────────────────────┐
│ SYSTEM BOOT                                                     │
│ - Systemd starts wopr.service                                   │
│ - Executes: python3 /opt/WOPR/backend/src/run_service.py        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ RUN_SERVICE.PY - Initialization                                 │
│                                                                  │
│ 1. Load persistent configuration:                               │
│    persistent_data = load_persistent_data()                     │
│    # Reads from /opt/WOPR/backend/data/hook_links.json          │
│    # Reads from /opt/WOPR/backend/data/startup_patterns.json    │
│                                                                  │
│    hook_links = {                                               │
│      "cpu_monitor": "loading_bar"                               │
│    }                                                             │
│    startup_patterns = ["knight_rider"]                          │
│                                                                  │
│ 2. Start patterns from hook_links:                              │
│    for pattern_name in hook_links.values():                     │
│        manager.start_pattern(pattern_name)                      │
│    # Starts "loading_bar"                                       │
│                                                                  │
│ 3. Start standalone patterns:                                   │
│    for pattern_name in startup_patterns:                        │
│        manager.start_pattern(pattern_name)                      │
│    # Starts "knight_rider"                                      │
│                                                                  │
│ 4. Enter main loop:                                             │
│    while True:                                                  │
│        # Animate patterns                                       │
│        manager.animate()                                        │
│        # Check hooks                                            │
│        manager.check_hooks()                                    │
│        # Route alerts to patterns                               │
│        sleep(0.033)                                             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    RESULT ON BOOT:
        • loading_bar starts (linked to cpu_monitor)
        • knight_rider starts (standalone)
        • LEDs show animated patterns
        • Hooks monitoring system
        • Alerts routed to patterns automatically
```

## Component Responsibilities

### GUI (wopr_gui.py)

**Responsibilities**:
1. Display UI for user interaction
2. Send IPC commands to backend
3. Receive and display results
4. Show connection status
5. Refresh displays periodically

**Does NOT**:
- Do any LED control
- Check system metrics
- Store configuration (that's done by backend)

**Calls IPC Actions**:
- `list_patterns`, `list_hooks`
- `start_pattern`, `stop_pattern`, `stop_all`
- `status`, `trigger_test_hook`
- `add_persistent_link`, `remove_persistent_link`
- `add_pattern_to_startup`, `remove_pattern_from_startup`
- `list_persistent_links`, `list_startup_patterns`

---

### IPC Server (ipc_server.py)

**Responsibilities**:
1. Listen on `/tmp/wopr.sock` for requests
2. Parse JSON requests
3. Validate action and parameters
4. Route to backend handlers
5. Return JSON responses
6. Handle socket cleanup

**Does NOT**:
- Do business logic (that's backend)
- Store data (that's backend)
- Control LEDs (that's backend)

**Methods for each action**:
- `handle_start_pattern()`
- `handle_stop_pattern()`
- `handle_add_persistent_link()`
- ... (one per action)

**Each handler**:
1. Validates parameters
2. Calls backend function
3. Returns JSON result

---

### Backend (backend.py + run_service.py)

**Responsibilities**:
1. Load and manage patterns
2. Monitor hooks
3. Route alerts to patterns
4. Save/load configuration
5. Manage pattern lifecycle
6. Update LEDs

**Does NOT**:
- Handle networking (that's IPC server)
- Show UI (that's GUI)

**Key Class: PatternManager**
```python
class PatternManager:
    def start_pattern(name)           # Start pattern, create thread
    def stop_pattern()                # Stop current pattern
    def check_hooks()                 # Check all hooks, route alerts
    def add_hook_link(hook, pattern)  # Save link to disk
    def remove_hook_link(hook)        # Remove link from disk
    def add_pattern_to_startup()      # Save pattern to disk
    def remove_pattern_from_startup() # Remove pattern from disk
    def get_hook_links()              # Get from memory
    def get_startup_patterns()        # Get from memory
    def save_hook_links()             # Write to hook_links.json
    def load_hook_links()             # Read from hook_links.json
```

---

### Patterns (in patterns/)

**Responsibilities**:
1. Implement animation loop
2. Check alert queue
3. Update color based on alerts
4. Draw frames to LEDs

**Interface: PatternBase**
```python
class PatternBase:
    def run(self, led_manager, alert_queue=None):
        while not stop_requested:
            # Check for alerts
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    self.current_color = message.color
                except:
                    pass
            
            # Animate and update
            self.animate_frame(led_manager)
            led_manager.update()
            sleep(frame_delay)
```

---

### Hooks (in hooks/)

**Responsibilities**:
1. Check system conditions
2. Generate HookMessage if alert triggered
3. Return None if no change

**Interface: SystemEventHook**
```python
class SystemEventHook:
    def get_message(self):
        # Check condition
        # Determine alert level
        # Create and return HookMessage
        # Or return None
        pass
```

---

### Alert System (hook_alerts.py)

**Responsibilities**:
1. Define alert levels (NORMAL, WARNING, CRITICAL)
2. Define color mapping
3. Provide HookMessage class for communication

**Key Classes**:
```python
class AlertLevel(Enum):
    NORMAL = 1
    WARNING = 2
    CRITICAL = 3

class HookMessage:
    level: AlertLevel
    color: Tuple[int, int, int]
    hook_name: str
    value: float
```

---

### Persistent Storage

**Files**:
- `/opt/WOPR/backend/data/hook_links.json`
- `/opt/WOPR/backend/data/startup_patterns.json`

**Format**: JSON

**Who Reads**:
- run_service.py on boot
- Backend when asked via IPC

**Who Writes**:
- Backend when configuration changes

---

## Communication Protocols

### IPC Protocol (GUI ↔ IPC Server)

**Type**: JSON-RPC over Unix domain socket

**Socket**: `/tmp/wopr.sock`

**Request Format**:
```json
{
  "action": "action_name",
  "params": {
    "param1": "value1"
  }
}
```

**Response Format**:
```json
{
  "ok": true/false,
  "result": {...},
  "error": "message"
}
```

**Protocol Stack**:
```
GUI Application
    ↓
socket.socket(AF_UNIX, SOCK_STREAM)
    ↓
connect("/tmp/wopr.sock")
    ↓
sendall(json.dumps(request).encode())
    ↓
recvall(response_bytes)
    ↓
json.loads(response)
    ↓
close()
```

---

### Alert Queue (Hook → Pattern)

**Type**: Thread-safe queue

**Message Type**: HookMessage object

**How it Works**:
1. Each running pattern gets alert_queue parameter
2. Hook check puts message in queue
3. Pattern checks queue in each frame
4. Pattern reads and applies color change

**Thread Safety**:
- Queue is thread-safe (concurrent.futures.queue.Queue)
- Multiple threads can safely read/write
- No locks needed in application code

---

### LED Communication (Pattern → LEDs)

**Type**: SPI bus

**Device**: `/dev/spidev0.0`

**Data Format**: RGB values (0-255 each)

**Timing**: Via Pi5Neo library

---

## Error Handling

### IPC Level

**Socket Error**:
- GUI catches and shows "Disconnected"
- Retries on next command
- Persistent connection loss triggers warning

**Invalid JSON**:
- IPC Server catches and returns error
- GUI shows error dialog

**Invalid Action**:
- IPC Server validates action name
- Returns `{"ok": false, "error": "Unknown action"}`

### Backend Level

**Pattern Load Error**:
- Pattern fails to import
- Backend logs error
- Returns error response to IPC
- System stays stable

**Hook Check Error**:
- Individual hook check fails
- Error logged
- Other hooks continue
- Pattern gets no alert

**File I/O Error**:
- Configuration save fails
- Error returned to GUI
- Configuration not persisted
- User informed

---

## Data Flow Diagrams

### Configuration Save

```
User Action
    ↓
GUI (add_persistent_link_with_start)
    ↓
send_ipc_command("add_persistent_link", {...})
    ↓
IPC Server (handle_add_persistent_link)
    ↓
Backend (PatternManager.add_hook_link)
    ↓
hook_links["hook"] = "pattern"  (in memory)
    ↓
save_hook_links()
    ↓
Write to /opt/WOPR/backend/data/hook_links.json
    ↓
Return success to GUI
    ↓
GUI shows "Configuration saved"
```

### Configuration Load (on Boot)

```
System Boots
    ↓
systemd starts wopr.service
    ↓
run_service.py starts
    ↓
load_persistent_data()
    ↓
Read hook_links.json
Read startup_patterns.json
    ↓
In memory dicts populated
    ↓
For each in hook_links.values():
  manager.start_pattern(pattern_name)
    ↓
For each in startup_patterns:
  manager.start_pattern(pattern_name)
    ↓
Main loop starts
    ↓
Service running with configured patterns
```

---

## Summary: Interaction Timeline

**1. User starts GUI**
- GUI connects, checks service
- Shows connection status

**2. User configures auto-start**
- GUI sends IPC command
- Backend saves to disk
- Backend starts pattern
- Pattern starts receiving alerts

**3. Hook checks every 500ms**
- Hook generates message if needed
- Backend routes to pattern's queue
- Pattern reads queue next frame
- LEDs update with new color

**4. System reboots**
- Service starts automatically
- Loads configuration from disk
- Starts all configured patterns
- Main loop running
- System responsive to alerts

---

**Now you understand how all the pieces work together!**
