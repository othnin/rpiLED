# File Cleanup Analysis

## Overview

This document analyzes which files in the WOPR codebase are actively used vs. unused/obsolete, helping determine what can be safely removed to reduce clutter.

**Analysis Date**: December 2025  
**Analysis Method**: Import tracking, grep search, code review

---

## Summary: Files by Category

### ✅ ACTIVELY USED (Keep)

| File | Purpose | Used By |
|------|---------|---------|
| `backend.py` | Core PatternManager class | run_service.py, ipc_server.py, GUI |
| `config.py` | System configuration | All backends and services |
| `hook_alerts.py` | Alert system (AlertLevel, HookMessage) | All hooks, patterns, backend |
| `ipc_server.py` | IPC/JSON-RPC server | run_service.py, GUI |
| `run_service.py` | Main service runner | systemd (wopr.service) |
| `hooks/cpu_monitor.py` | CPU monitoring | backend.check_hooks() |
| `hooks/mem_monitor.py` | Memory monitoring | backend.check_hooks() |
| `hooks/disk_monitor.py` | Disk monitoring | backend.check_hooks() |
| `hooks/cpu_temp.py` | Temperature monitoring | backend.check_hooks() |
| `hooks/voltage_monitor.py` | Voltage monitoring | backend.check_hooks() |
| `patterns/knight_rider.py` | LED animation pattern | User startup |
| `patterns/loading_bar.py` | LED animation pattern | User startup |
| `patterns/my_cool_pattern.py` | LED animation pattern | User startup |
| `wopr_gui.py` | GUI application | User execution |
| `verify_installation.py` | Installation checker | Setup/validation |
| `test_alert_system.py` | Alert system tests | Development/CI |
| `systemd/wopr.service` | Service definition | systemd boot |

---

### ⚠️ DEVELOPMENT/DEBUGGING ONLY (Safe to Remove)

| File | Purpose | Type | Notes |
|------|---------|------|-------|
| `cpu_load.py` | **Old/duplicate** | Development | Not imported anywhere; superseded by hooks |
| `debug_service.py` | Debug version of run_service | Development | Enhanced logging; for troubleshooting only |
| `test_hook.py` | CPU hook demo script | Development | Tests CPUOver20Hook manually |
| `test_ipc_client.py` | IPC protocol testing | Development | Manual socket protocol testing |
| `test_pattern.py` | Pattern tester script | Development | Run single pattern for development |
| `test_hook_linking.py` | Hook link testing | Development | Manual test of hook↔pattern linking |
| `wopr_client.py` | Old CLI client | Development | Redundant; GUI is the main interface |
| `test_dual_pattern_system.py` | Old system test | Development | Obsolete (testing dual patterns) |
| `hooks/test_hook.py` | Hook stub/template | Development | Empty test hook template |

---

## Detailed Analysis

### 1. **cpu_load.py** - SAFE TO REMOVE ❌

**Status**: NOT USED  
**Reason**: No imports found anywhere in codebase

```bash
# Verification
$ grep -r "cpu_load" /opt/WOPR/backend/src/ --include="*.py"
# Result: No matches
```

**Purpose**: Appears to be an old CPU monitoring module (likely pre-hook_alerts system)

**Impact of Removal**: None - not imported or used by anything

**Recommendation**: **DELETE**

---

### 2. **debug_service.py** - DEVELOPMENT ONLY ⚠️

**Status**: Not used in production  
**Purpose**: Debug version of `run_service.py` with extensive logging

**Imports/Dependencies**:
- Same imports as `run_service.py`
- Identical functionality but with `[MAIN]`, `[STARTUP]`, `[SHUTDOWN]` debug prefixes

**Who Uses It**: Manual debugging only

**Code Comparison**:
```python
# run_service.py (production)
ipc = IPCServer(manager, socket_path=socket_path)
ipc.start()

# debug_service.py (debug version with logging)
print("[MAIN] Starting IPC server on {socket_path}...", file=sys.stderr, flush=True)
ipc = IPCServer(manager, socket_path=socket_path)
ipc.start()
print("[MAIN] IPC server started", file=sys.stderr, flush=True)
```

**When To Use**: If you need verbose startup/shutdown debugging, run this instead of run_service.py

**Recommendation**: **OPTIONAL REMOVE** (can keep if want debug option, otherwise remove)

---

### 3. **test_hook.py** - DEVELOPMENT TEST ⚠️

**Status**: Manual development test  
**Purpose**: Demonstrates CPUOver20Hook triggering a pattern

**What It Does**:
1. Creates Pi5Neo strip
2. Creates PatternManager
3. Starts CPU load simulator in background thread
4. Monitors CPUOver20Hook.check()
5. Starts pattern when CPU > 20%

**Actual Usage Pattern**:
```python
# Creates CPU load to trigger hook
cpu_load_thread = threading.Thread(
    target=lambda: cpu_load_simulator(TEST_DURATION, intensity=5.0),
    daemon=True
)
```

**When To Use**: 
- Testing hook logic manually
- Verifying pattern starts when CPU threshold hit
- Development/debugging

**Can Be Replaced By**: 
- Running actual system monitor (top/htop) to trigger CPU
- Or using IPC to test directly with `test_alert_system.py`

**Recommendation**: **SAFE TO REMOVE** (can use test_alert_system.py instead)

---

### 4. **test_ipc_client.py** - DEVELOPMENT TEST ⚠️

**Status**: Manual IPC protocol testing  
**Purpose**: Test JSON-RPC socket communication

**What It Does**:
- Tests raw socket calls to `/tmp/wopr.sock`
- Sends JSON requests manually
- Validates response parsing

**Can Be Replaced By**: 
- GUI (has full IPC integration)
- socat command-line testing:
  ```bash
  printf '{"action":"list_patterns"}' | socat - UNIX-CONNECT:/tmp/wopr.sock
  ```

**Recommendation**: **SAFE TO REMOVE** (can test via GUI or socat)

---

### 5. **test_pattern.py** - DEVELOPMENT TEST ⚠️

**Status**: Manual pattern tester  
**Purpose**: Start a single pattern and run it for a set time

**What It Does**:
```python
# Test a specific pattern for RUN_TIME seconds
PATTERN_NAME = "Knight Rider Pattern"
RUN_TIME = 10  # seconds

manager.start_pattern(PATTERN_NAME)
time.sleep(RUN_TIME)
manager.stop_pattern()
```

**Can Be Replaced By**: GUI "Test Patterns" section or IPC commands

**Recommendation**: **SAFE TO REMOVE** (can test via GUI)

---

### 6. **test_hook_linking.py** - DEVELOPMENT TEST ⚠️

**Status**: Manual hook↔pattern linking test  
**Purpose**: Test linking hooks to patterns

**What It Does**:
- Tests `add_hook_link()` and `remove_hook_link()`
- Verifies persistent storage
- Tests pattern starting from hook

**Can Be Replaced By**: GUI "Hook Links" section or test_alert_system.py

**Recommendation**: **SAFE TO REMOVE** (can test via GUI)

---

### 7. **wopr_client.py** - OLD CLI CLIENT ⚠️

**Status**: Legacy alternative to GUI  
**Purpose**: Command-line IPC client for pattern control

**Command Examples**:
```bash
./wopr_client.py list              # List patterns
./wopr_client.py start "Pattern"   # Start pattern
./wopr_client.py stop              # Stop pattern
./wopr_client.py status            # Show status
```

**Why Redundant**: 
- GUI does everything this does
- Less user-friendly than GUI
- Additional maintenance burden

**Can Be Replaced By**: 
- GUI application (wopr_gui.py)
- Direct socat commands for scripting

**Who Might Use It**: 
- Headless server users
- Automation/scripting

**Recommendation**: **OPTIONAL REMOVE** (keep if want CLI option, otherwise remove for simplicity)

---

### 8. **test_dual_pattern_system.py** - OBSOLETE ❌

**Status**: Old/obsolete system test  
**Purpose**: Testing "dual pattern" system (can't run 2+ patterns simultaneously)

**Why Obsolete**: 
- System only runs ONE pattern at a time by design
- Single pattern + hook alerts is the architecture
- "Dual pattern" concept is not supported/desired

**Recommendation**: **DELETE** (not part of current design)

---

### 9. **hooks/test_hook.py** - STUB/TEMPLATE ⚠️

**Status**: Empty hook template  
**Purpose**: Placeholder for developing new hooks

**Content**: 
```python
# Empty hook - doesn't do anything
```

**Used By**: Not used (skipped by pattern loader due to underscore naming convention)

**Recommendation**: **DELETE** or rename to `_template_hook.py` if keeping as template

---

## Directory Cleanup Summary

### `/opt/WOPR/backend/src/`

**Safe to Remove** (9 files):
- ❌ `cpu_load.py` - Not imported anywhere
- ⚠️ `debug_service.py` - Debug version only
- ⚠️ `test_hook.py` - Manual test only
- ⚠️ `test_ipc_client.py` - Socket protocol test only
- ⚠️ `test_pattern.py` - Pattern tester only
- ⚠️ `test_hook_linking.py` - Hook linking test only
- ⚠️ `wopr_client.py` - Legacy CLI client
- ❌ `hooks/test_hook.py` - Empty stub

**Keep** (7 files):
- ✅ `backend.py`
- ✅ `config.py`
- ✅ `hook_alerts.py`
- ✅ `ipc_server.py`
- ✅ `run_service.py`
- ✅ All 5 hooks (cpu_monitor, mem_monitor, disk_monitor, cpu_temp, voltage_monitor)
- ✅ All 3 patterns (knight_rider, loading_bar, my_cool_pattern)

---

### `/opt/WOPR/` (Root)

**Safe to Remove** (1 file):
- ❌ `test_dual_pattern_system.py` - Obsolete (dual pattern not supported)

**Keep** (2 files):
- ✅ `test_alert_system.py` - Comprehensive alert system tests
- ✅ `verify_installation.py` - Installation verification utility

---

## Cleanup Recommendations

### Option A: Conservative (Remove Obvious Garbage)

**Remove**:
- `cpu_load.py` - Not used
- `test_dual_pattern_system.py` - Obsolete design
- `hooks/test_hook.py` - Empty stub

**Keep**: Everything else (includes test/debug utilities for development)

**Rationale**: Keeps optional tools for developers/troubleshooting

---

### Option B: Moderate (Clean Workspace)

**Remove**:
- `cpu_load.py` - Not used
- `test_dual_pattern_system.py` - Obsolete
- `hooks/test_hook.py` - Empty stub
- `test_hook.py` - Manual test only
- `test_pattern.py` - Manual test only
- `test_hook_linking.py` - Manual test only

**Keep**: 
- `debug_service.py` - Useful for troubleshooting
- `wopr_client.py` - Useful for headless/scripting
- `test_ipc_client.py` - Reference for socket protocol

**Rationale**: Removes test utilities you won't use, keeps documentation/alternatives

---

### Option C: Aggressive (Production Only)

**Remove Everything from Option B Plus**:
- `debug_service.py` - Use run_service.py + logging
- `test_ipc_client.py` - Not needed in production
- `wopr_client.py` - GUI is standard interface

**Keep Only**:
- Core: backend.py, config.py, hook_alerts.py, ipc_server.py, run_service.py
- All hooks and patterns
- GUI, test_alert_system.py, verify_installation.py

**Rationale**: Minimal code surface, production-focused

---

## Recommended Action: Option B (Moderate)

This balances clean workspace with keeping useful tools.

### Files to Archive/Remove:

```
# High Priority (definitely unused)
/opt/WOPR/backend/src/cpu_load.py
/opt/WOPR/backend/src/hooks/test_hook.py
/opt/WOPR/test_dual_pattern_system.py

# Medium Priority (development/testing utilities)
/opt/WOPR/backend/src/test_hook.py
/opt/WOPR/backend/src/test_pattern.py
/opt/WOPR/backend/src/test_hook_linking.py

# Optional (keep one copy, archive elsewhere if needed)
/opt/WOPR/backend/src/test_ipc_client.py
/opt/WOPR/backend/src/debug_service.py
/opt/WOPR/backend/src/wopr_client.py
```

### Why Keep debug_service.py, test_ipc_client.py, wopr_client.py:

1. **debug_service.py** - Useful for troubleshooting service startup issues
2. **test_ipc_client.py** - Reference implementation for IPC protocol
3. **wopr_client.py** - Alternative interface for automation/headless systems

### What's Safe to Keep Running:

- `/opt/WOPR/backend/src/run_service.py` via systemd ✅
- `/opt/WOPR/frontend/src/wopr_gui.py` for user control ✅
- All hooks automatically checked ✅
- All patterns available ✅

---

## Archive Recommendations

If you want to keep files but not in main directory:

```
mkdir -p /opt/WOPR/archive/development
mkdir -p /opt/WOPR/archive/tests
mkdir -p /opt/WOPR/archive/old

# Move development utilities
mv /opt/WOPR/backend/src/debug_service.py /opt/WOPR/archive/development/
mv /opt/WOPR/backend/src/wopr_client.py /opt/WOPR/archive/development/

# Move test scripts
mv /opt/WOPR/backend/src/test_*.py /opt/WOPR/archive/tests/
mv /opt/WOPR/backend/src/hooks/test_hook.py /opt/WOPR/archive/tests/

# Move obsolete
mv /opt/WOPR/backend/src/cpu_load.py /opt/WOPR/archive/old/
mv /opt/WOPR/test_dual_pattern_system.py /opt/WOPR/archive/old/
```

---

## Impact Analysis

### If we delete all recommended files:

**What breaks?** Nothing - only test/debug utilities are removed

**What still works?**
- ✅ Service starts and runs (run_service.py intact)
- ✅ Patterns load and animate (all pattern files intact)
- ✅ Hooks monitor system (all hook files intact)
- ✅ GUI controls system (wopr_gui.py intact)
- ✅ IPC server works (ipc_server.py intact)
- ✅ Alert routing works (hook_alerts.py intact)

**What you lose?**
- Manual test scripts (can re-write if needed)
- CLI alternative (GUI is full-featured)
- Debug startup logging (can add to run_service.py if needed)

---

## Summary Table

| File | Category | Safe? | Reason |
|------|----------|-------|--------|
| cpu_load.py | Unused | ✅ YES | Not imported |
| debug_service.py | Optional | ⚠️ OPTIONAL | Debug version, keep for troubleshooting |
| test_hook.py | Optional | ✅ YES | Manual test only |
| test_ipc_client.py | Optional | ⚠️ OPTIONAL | Reference implementation, keep for protocol docs |
| test_pattern.py | Optional | ✅ YES | Manual test only |
| test_hook_linking.py | Optional | ✅ YES | Manual test only |
| wopr_client.py | Optional | ⚠️ OPTIONAL | Keep for headless/scripting |
| test_dual_pattern_system.py | Obsolete | ✅ YES | Old design, not used |
| hooks/test_hook.py | Stub | ✅ YES | Empty, not used |

---

## Next Steps

1. **Review** this analysis and choose Option A, B, or C
2. **Archive** files to `/opt/WOPR/archive/` if you might need them later
3. **Delete** truly unused files (cpu_load.py, test_dual_pattern_system.py at minimum)
4. **Update** any documentation if removing files referenced in guides
5. **Test** that service still starts: `systemctl restart wopr`
6. **Verify** GUI still connects and controls patterns

---

**Questions?**

- Is there a file you want to keep that we identified as unused?
- Want different archival strategy?
- Need help migrating code from removed files?

Let me know which option fits best!
