# WOPR LED Control - Beginner's Guide

Welcome to WOPR! This guide explains everything in simple terms.

## What is WOPR?

WOPR is an LED lighting system that:
- Shows cool animations on LED strips
- Changes colors based on what your computer is doing
- Starts automatically when your system boots
- Has a simple interface to control it

## What Do I Need?

**Hardware**:
- Raspberry Pi 5 (or similar)
- NeoPixel LED strip (addressable RGB LEDs)
- Power supply for LEDs and Pi

**Software** (already installed):
- LED control service (runs in background)
- GUI application (for control and configuration)

## Getting Started

### Step 1: Launch the GUI

Open terminal and type:
```bash
python3 /opt/WOPR/frontend/src/wopr_gui.py
```

A window will open. At the top:
- **Green dot** = Connected (good!)
- **Red dot** = Disconnected (service not running)

### Step 2: Test a Pattern

In "Available Patterns" section:
1. Click any pattern name (e.g., "knight_rider")
2. Click [Start]
3. Watch your LEDs animate!
4. Click [Stop] to stop

### Step 3: Make Pattern Auto-Start on Boot

You have two options:

#### Option A: Simple Auto-Start (Recommended for Start)

1. Click pattern dropdown at top
2. Select the pattern you want
3. Click "⭐ Start & Auto-start on Boot"
4. Pattern starts immediately ✓
5. Next reboot: Pattern runs automatically ✓

#### Option B: Smart Auto-Start (Responds to System Changes)

This makes patterns change color based on what's happening:

1. Click pattern dropdown at top
2. Select pattern (e.g., "loading_bar")
3. In "🔗 Hook Link" section, select a hook:
   - **cpu_monitor** - Responds to CPU usage
   - **disk_monitor** - Responds to disk space
   - **mem_monitor** - Responds to memory usage
   - **cpu_temp** - Responds to temperature
   - **voltage_monitor** - Responds to power supply
4. Click "🔗 Start & Auto-start on Boot"
5. Pattern starts immediately ✓
6. When CPU/disk/memory/temp changes: LED color changes ✓
7. Next reboot: Pattern runs and auto-responds ✓

## Understanding Colors

Different colors mean different things:

🟢 **Green** = Everything normal
🟠 **Orange** = Getting concerning (warning)
🔴 **Red** = Problem (critical)

### Example: CPU Monitor

- **Green animation**: CPU is relaxed (<20% usage)
- **Orange animation**: CPU working hard (20-50% usage)  
- **Red animation**: CPU maxed out (>50% usage)

## What Are These "Hooks"?

Hooks are system monitors that watch what's happening:

- **cpu_monitor** - Watches processor usage
- **disk_monitor** - Watches storage space
- **mem_monitor** - Watches memory usage
- **cpu_temp** - Watches processor temperature
- **voltage_monitor** - Watches power supply voltage

You can link a hook to a pattern, and the pattern will:
- Change color when the system condition changes
- Start automatically on boot
- Keep working even after reboot

## Common Workflows

### I want cool LEDs when I boot up

```
1. Open GUI
2. Click pattern dropdown → select "loading_bar"
3. Click "⭐ Start & Auto-start on Boot"
4. That's it! Next reboot → automatic!
```

### I want LEDs to show when my CPU is busy

```
1. Open GUI
2. Click pattern dropdown → select "loading_bar"
3. Select "cpu_monitor" from Hook Link dropdown
4. Click "🔗 Start & Auto-start on Boot"
5. Done! LEDs now show CPU activity with colors
```

### I want to test different patterns

```
1. Open GUI - Test Patterns section
2. Click pattern → Click [Start]
3. See it in action
4. Try different patterns this way
5. Once happy, configure for auto-start
```

### I want to remove auto-start

```
1. Open GUI
2. Click pattern dropdown → select pattern
3. Click "Remove & Stop" button (red)
4. Confirm - pattern stops and auto-start removed
```

## The GUI Explained Simply

### Top Section
- Green dot = Connected to service (good!)
- "Current Pattern" = What's running now

### Middle Section: Test Area
- **Left side**: Try different patterns
- **Right side**: Try different hooks
- Use these to experiment before configuring auto-start

### Bottom Section: Startup Config
- **Dropdown**: Pick which pattern to configure
- **Green buttons**: Set up auto-start
- **Red buttons**: Remove auto-start
- **Status text**: Shows what's configured

## What Patterns Do?

### Knight Rider
A light bounces back and forth (like the old TV show)

### Loading Bar
A progress bar that fills and empties repeatedly

### My Cool Pattern
A custom pattern (see `/opt/WOPR/backend/src/patterns/my_cool_pattern.py` to customize)

## Troubleshooting

### GUI shows red dot (Disconnected)

**The service isn't running.** Try:
```bash
systemctl --user status wopr
```

Should show "active (running)"

If not active, start it:
```bash
systemctl --user start wopr
```

### Pattern doesn't start

**Check**:
1. LEDs plugged in and powered?
2. Pattern selected in dropdown?
3. Try [Refresh All] button

### Pattern starts but no LEDs

**Could be**:
- LEDs not powered
- LED data pin not connected to Pi GPIO
- Check LED wiring

### Want to see what's happening?

View service logs:
```bash
journalctl --user -u wopr -n 50 -f
```

(Shows last 50 lines, updates live with `-f`)

### Something else?

Check the logs and the technical docs:
- `ARCHITECTURE.md` - How everything works together
- `IPC_ACTIONS_REFERENCE.md` - All technical details
- `GUI_DOCUMENTATION.md` - GUI details

## Tips & Tricks

### Keyboard Shortcuts
- **Tab** - Move between fields
- **Space/Enter** - Click buttons
- **Arrow keys** - Change dropdowns

### Quick Test
- Double-click any pattern to start it instantly

### Check What's Configured
- Click pattern dropdown to see status of each pattern

### Verify After Reboot
- Reboot: `sudo reboot`
- If pattern auto-starts, it worked!

## Next Steps

1. **Try a pattern**: Test section to play around
2. **Pick favorite**: Find which pattern you like
3. **Pick trigger**: Choose standalone or hook-based
4. **Configure**: Use buttons to set up auto-start
5. **Reboot**: Verify it auto-starts
6. **Enjoy**: Your LEDs are now smart!

## Quick Reference

| What I Want | Steps |
|------------|-------|
| Test a pattern | Click pattern → [Start] → [Stop] |
| Auto-start simple | Pattern dropdown → select → ⭐ button |
| Auto-start smart | Pattern → Hook → 🔗 button |
| Remove auto-start | Pattern dropdown → [Remove & Stop] |
| Refresh | Click [Refresh All] button |
| Stop everything | Click [Stop All Patterns] button |

## Frequently Asked Questions

**Q: How many patterns can run at once?**
A: One at a time. Pick one to run.

**Q: Can I create custom patterns?**
A: Yes! Edit `/opt/WOPR/backend/src/patterns/my_cool_pattern.py`

**Q: Can I add more hooks?**
A: Yes! Create new file in `/opt/WOPR/backend/src/hooks/`

**Q: Will configuration survive a reboot?**
A: Yes! Both standalone and hook-linked patterns auto-start.

**Q: How do I switch patterns?**
A: Click [Stop All], then start a different one. Or use dropdown config.

**Q: Are LEDs always on?**
A: Only when pattern is running. Otherwise LEDs are off.

**Q: Why is the pattern not responding to CPU?**
A: It needs to be linked to a hook. See "I want LEDs to show CPU" workflow.

**Q: Can multiple people use it?**
A: The system runs as a background service. Any user can use the GUI.

**Q: What if I mess up?**
A: All configurations are saved. Revert by clicking [Remove & Stop].

## Getting Help

1. **Connection problems?** Check logs: `journalctl --user -u wopr`
2. **Pattern problems?** Try [Refresh All]
3. **Want to understand more?** Read `ARCHITECTURE.md`
4. **Need technical details?** Read `IPC_ACTIONS_REFERENCE.md`

## Learning More

- **How it all works**: `ARCHITECTURE.md`
- **All technical actions**: `IPC_ACTIONS_REFERENCE.md`
- **GUI details**: `GUI_DOCUMENTATION.md`
- **Source code**: `/opt/WOPR/backend/src/`

---

**Congratulations!** You now know enough to use WOPR. Have fun with your smart LEDs! 🎉
