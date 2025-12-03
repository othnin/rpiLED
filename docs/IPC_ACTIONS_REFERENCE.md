# IPC Server - Complete Action Reference

**Socket**: `/tmp/wopr.sock`  
**Protocol**: JSON request/response  
**Total Actions**: 22

## Quick Reference Table

| Action | Purpose | Parameters | Response |
|--------|---------|------------|----------|
| `start_pattern` | Start pattern immediately | `name` | pattern info |
| `stop_pattern` | Stop current pattern | none | status |
| `stop_all` | Stop all patterns | none | status |
| `status` | Get current pattern | none | pattern info |
| `list_patterns` | List available patterns | none | array |
| `list_hooks` | List available hooks | none | array |
| `trigger_test_hook` | Manually trigger test hook | none | status |
| `list_hook_states` | Get hook status | none | states dict |
| `add_persistent_link` | Link hook to pattern | hook, pattern | status |
| `remove_persistent_link` | Remove hook link | hook | status |
| `list_persistent_links` | Get hook links | none | links dict |
| `add_pattern_to_startup` | Add to auto-start | pattern | status |
| `remove_pattern_from_startup` | Remove from auto-start | pattern | status |
| `list_startup_patterns` | Get auto-start patterns | none | array |
| `debug_status` | Get debug info | none | debug data |
| `reload_config` | Reload config | none | status |

## Detailed Action Reference

### Pattern Control

#### `start_pattern`
**Purpose**: Start a pattern immediately

**Request**:
```json
{
  "action": "start_pattern",
  "params": {
    "name": "knight_rider"
  }
}
```

**Response Success**:
```json
{
  "ok": true,
  "result": {
    "pattern": "knight_rider",
    "started": true,
    "message": "Pattern started"
  }
}
```

**Response Failure**:
```json
{
  "ok": false,
  "error": "Pattern 'unknown_pattern' not found"
}
```

**Valid Patterns**: knight_rider, loading_bar, my_cool_pattern

---

#### `stop_pattern`
**Purpose**: Stop the currently running pattern

**Request**:
```json
{
  "action": "stop_pattern"
}
```

**Response Success**:
```json
{
  "ok": true,
  "result": {
    "pattern": "knight_rider",
    "stopped": true,
    "message": "Pattern stopped"
  }
}
```

**Response Failure**:
```json
{
  "ok": false,
  "error": "No pattern currently running"
}
```

---

#### `stop_all`
**Purpose**: Stop all patterns and hooks

**Request**:
```json
{
  "action": "stop_all"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "patterns_stopped": 1,
    "message": "All patterns stopped"
  }
}
```

---

#### `status`
**Purpose**: Get current running pattern status

**Request**:
```json
{
  "action": "status"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "current_pattern": "knight_rider",
    "is_running": true,
    "uptime_seconds": 42.5
  }
}
```

**Response (No Pattern Running)**:
```json
{
  "ok": true,
  "result": {
    "current_pattern": null,
    "is_running": false
  }
}
```

---

#### `list_patterns`
**Purpose**: List all available patterns

**Request**:
```json
{
  "action": "list_patterns"
}
```

**Response**:
```json
{
  "ok": true,
  "result": [
    "knight_rider",
    "loading_bar",
    "my_cool_pattern"
  ]
}
```

---

### Hook Management

#### `list_hooks`
**Purpose**: List all available hooks

**Request**:
```json
{
  "action": "list_hooks"
}
```

**Response**:
```json
{
  "ok": true,
  "result": [
    "cpu_monitor",
    "disk_monitor",
    "cpu_temp",
    "mem_monitor",
    "test_trigger",
    "voltage_monitor"
  ]
}
```

---

#### `trigger_test_hook`
**Purpose**: Manually trigger the test hook (for testing alert system)

**Request**:
```json
{
  "action": "trigger_test_hook"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "hook": "test_trigger",
    "triggered": true,
    "message": "Test hook triggered"
  }
}
```

**Use Case**: Test that alerts are working without waiting for actual system conditions

---

#### `list_hook_states`
**Purpose**: Get current state of all hooks

**Request**:
```json
{
  "action": "list_hook_states"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "cpu_monitor": {
      "enabled": true,
      "current_value": 45.2,
      "alert_level": "NORMAL",
      "thresholds": [20, 50, 75]
    },
    "disk_monitor": {
      "enabled": true,
      "current_value": 12.5,
      "alert_level": "WARNING",
      "thresholds": [15, 10]
    },
    "mem_monitor": {
      "enabled": true,
      "current_value": 78.0,
      "alert_level": "CRITICAL",
      "thresholds": [50, 80]
    },
    "cpu_temp": {
      "enabled": true,
      "current_value": 62.3,
      "alert_level": "NORMAL",
      "thresholds": [60, 75]
    },
    "voltage_monitor": {
      "enabled": true,
      "current_value": 4.95,
      "alert_level": "NORMAL",
      "thresholds": [4.8]
    }
  }
}
```

---

### Persistent Configuration

#### `add_persistent_link`
**Purpose**: Link a hook to a pattern for auto-start and alert response

**Request**:
```json
{
  "action": "add_persistent_link",
  "params": {
    "hook_event_name": "cpu_monitor",
    "pattern_name": "loading_bar"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "hook": "cpu_monitor",
    "pattern": "loading_bar",
    "message": "Link created",
    "persistent": true
  }
}
```

**Behavior**:
- On boot: Pattern auto-starts
- At runtime: Hook alerts update pattern color
- Configuration saved to disk

---

#### `remove_persistent_link`
**Purpose**: Remove hook→pattern link

**Request**:
```json
{
  "action": "remove_persistent_link",
  "params": {
    "hook_event_name": "cpu_monitor"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "hook": "cpu_monitor",
    "message": "Link removed",
    "persistent": true
  }
}
```

---

#### `list_persistent_links`
**Purpose**: Get all hook→pattern links

**Request**:
```json
{
  "action": "list_persistent_links"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "cpu_monitor": "loading_bar",
    "disk_monitor": "knight_rider",
    "mem_monitor": "my_cool_pattern"
  }
}
```

---

#### `add_pattern_to_startup`
**Purpose**: Configure pattern to auto-start on boot (no hook required)

**Request**:
```json
{
  "action": "add_pattern_to_startup",
  "params": {
    "pattern_name": "knight_rider"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "pattern": "knight_rider",
    "message": "Added to startup",
    "auto_start": true
  }
}
```

**Behavior**:
- Pattern starts on boot
- No hook integration
- Runs standalone
- Configuration saved to disk

---

#### `remove_pattern_from_startup`
**Purpose**: Remove pattern from auto-start

**Request**:
```json
{
  "action": "remove_pattern_from_startup",
  "params": {
    "pattern_name": "knight_rider"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "pattern": "knight_rider",
    "message": "Removed from startup"
  }
}
```

---

#### `list_startup_patterns`
**Purpose**: Get patterns configured for auto-start

**Request**:
```json
{
  "action": "list_startup_patterns"
}
```

**Response**:
```json
{
  "ok": true,
  "result": [
    "knight_rider",
    "loading_bar"
  ]
}
```

---

### System Management

#### `debug_status`
**Purpose**: Get detailed debug information

**Request**:
```json
{
  "action": "debug_status"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "service_uptime_seconds": 1234.56,
    "current_pattern": "loading_bar",
    "pattern_uptime_seconds": 45.2,
    "active_hooks": ["cpu_monitor", "disk_monitor"],
    "alert_queue_size": 0,
    "hook_links": {
      "cpu_monitor": "loading_bar"
    },
    "startup_patterns": ["knight_rider"],
    "recent_alerts": [
      {
        "timestamp": "2025-12-03T10:45:23.456Z",
        "hook": "cpu_monitor",
        "level": "WARNING",
        "value": 65.5
      }
    ],
    "error_log": []
  }
}
```

---

#### `reload_config`
**Purpose**: Reload configuration from disk

**Request**:
```json
{
  "action": "reload_config"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "message": "Configuration reloaded",
    "hook_links_loaded": 3,
    "startup_patterns_loaded": 2
  }
}
```

**Use Case**: Apply changes made directly to config files without restart

---

## Alert Levels

When hooks detect system conditions, they send alerts with these levels:

### CPU Monitor
- **NORMAL** (< 20%): Green
- **WARNING** (20-50%): Orange
- **CRITICAL** (> 50%): Red

### Disk Monitor
- **NORMAL** (> 15% free): Green
- **WARNING** (10-15% free): Orange
- **CRITICAL** (< 10% free): Red

### Memory Monitor
- **NORMAL** (< 50% used): Green
- **WARNING** (50-80% used): Orange
- **CRITICAL** (> 80% used): Red

### CPU Temperature
- **NORMAL** (< 60°C): Green
- **WARNING** (60-75°C): Orange
- **CRITICAL** (> 75°C): Red

### Voltage Monitor
- **NORMAL** (≥ 4.8V): Green
- **CRITICAL** (< 4.8V): Red

---

## Common Usage Patterns

### Pattern 1: List Available Options
```python
import socket
import json

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/tmp/wopr.sock')

# Get patterns
sock.sendall(json.dumps({"action": "list_patterns"}).encode())
sock.shutdown(socket.SHUT_WR)
data = sock.recv(4096)
patterns = json.loads(data)['result']
sock.close()

print("Available patterns:", patterns)
```

### Pattern 2: Start Pattern and Check Status
```python
# Start pattern
sock.sendall(json.dumps({
    "action": "start_pattern",
    "params": {"name": "knight_rider"}
}).encode())
sock.shutdown(socket.SHUT_WR)
result = json.loads(sock.recv(4096))
sock.close()

if result['ok']:
    print("Pattern started!")
    
    # Check status
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/tmp/wopr.sock')
    sock.sendall(json.dumps({"action": "status"}).encode())
    sock.shutdown(socket.SHUT_WR)
    status = json.loads(sock.recv(4096))
    sock.close()
    
    print("Current:", status['result']['current_pattern'])
```

### Pattern 3: Configure Hook Link
```python
sock.sendall(json.dumps({
    "action": "add_persistent_link",
    "params": {
        "hook_event_name": "cpu_monitor",
        "pattern_name": "loading_bar"
    }
}).encode())
sock.shutdown(socket.SHUT_WR)
result = json.loads(sock.recv(4096))
sock.close()

if result['ok']:
    print("Hook linked! Pattern will respond to CPU alerts")
```

---

## Error Codes

All errors return `{"ok": false, "error": "message"}`

**Common Errors**:
- `"Pattern 'xyz' not found"` - Invalid pattern name
- `"Hook 'xyz' not found"` - Invalid hook name
- `"No pattern currently running"` - Can't stop nothing
- `"Pattern already running"` - Can't start while one runs
- `"Pattern not in startup list"` - Can't remove what's not there
- `"Failed to save configuration"` - Disk write error

---

## Response Guarantees

**All responses**:
- Always include `"ok"` field (true or false)
- On success: Include `"result"` field
- On failure: Include `"error"` field
- Valid JSON (always parseable)
- Returned within 100ms typically

---

## Socket Connection Notes

**One Request per Connection**:
- Connect → Send request → Receive response → Close
- Don't reuse socket for multiple requests
- This is how GUI does it and it works reliably

**Timeout**: None hardcoded, but recommend 5-10 second timeout

**Error on Connection**: 
- Socket doesn't exist: Service not running
- Permission denied: Check socket permissions
- Connection refused: Service crashed

---

## GUI Integration

The GUI calls these actions in this order:

**On Startup**:
1. `list_patterns` - Populate pattern lists
2. `list_hooks` - Populate hook dropdown
3. `status` - Check current pattern
4. `list_persistent_links` - Show configured hooks
5. `list_startup_patterns` - Show configured standalone

**On Pattern Test**:
1. User selects pattern
2. `start_pattern` - Start it
3. `status` - Show it's running
4. User clicks stop
5. `stop_pattern` - Stop it

**On Configure Hook Link**:
1. `add_persistent_link` - Link hook to pattern
2. `start_pattern` - Start pattern immediately
3. `status` - Show running status

**Every 2 Seconds**:
1. `status` - Refresh current pattern

---

## Testing Actions

Use command line to test:

```bash
# List patterns
printf '{"action":"list_patterns"}' | socat - UNIX-CONNECT:/tmp/wopr.sock

# Start pattern
printf '{"action":"start_pattern","params":{"name":"knight_rider"}}' | socat - UNIX-CONNECT:/tmp/wopr.sock

# Get status
printf '{"action":"status"}' | socat - UNIX-CONNECT:/tmp/wopr.sock

# Trigger test hook
printf '{"action":"trigger_test_hook"}' | socat - UNIX-CONNECT:/tmp/wopr.sock
```

Install `socat` if needed:
```bash
sudo apt install socat
```

---

## Next Steps

See `ARCHITECTURE.md` for how these actions fit into the system  
See `BEGINNER_GUIDE.md` for user-friendly explanations
