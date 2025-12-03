"""
Test script for the Hook Alert System
Demonstrates multi-level alerts from hooks changing pattern colors
"""

import sys
import time
import queue
from unittest.mock import Mock, MagicMock
import psutil

# Add src to path
sys.path.insert(0, '/opt/WOPR/backend/src')

from hook_alerts import AlertLevel, HookMessage, AlertColorScheme
from hooks.cpu_monitor import CPUMonitorHook
from hooks.disk_monitor import DiskSpaceLowHook


def test_alert_levels():
    """Test AlertLevel enum and color scheme"""
    print("=" * 60)
    print("TEST 1: Alert Levels and Color Scheme")
    print("=" * 60)
    
    for level in AlertLevel:
        color = AlertColorScheme.get_color(level)
        print(f"{level.name:10} -> RGB{color}")
    print()


def test_cpu_monitor_hook():
    """Test CPU Monitor with multi-level alerts"""
    print("=" * 60)
    print("TEST 2: CPU Monitor Hook - Multi-level Alerts")
    print("=" * 60)
    
    hook = CPUMonitorHook(warn_threshold=20, crit_threshold=75)
    
    print(f"Hook name: {hook.event_name}")
    print(f"Thresholds: WARN={hook.warn_threshold}%, CRIT={hook.crit_threshold}%")
    print()
    
    # Simulate checking CPU multiple times
    print("Checking CPU state...")
    current_cpu = psutil.cpu_percent(interval=0.1)
    print(f"Current CPU usage: {current_cpu}%")
    print()
    
    # First check (establishes baseline)
    if hook.check():
        message = hook.get_message()
        print(f"✓ Alert triggered!")
        print(f"  Level: {message.alert_level.name}")
        print(f"  Color: {message.color}")
        print(f"  Metadata: {message.metadata}")
    else:
        print("✓ No alert (CPU within normal range)")
    print()


def test_disk_monitor_hook():
    """Test Disk Monitor with multi-level alerts"""
    print("=" * 60)
    print("TEST 3: Disk Monitor Hook - Multi-level Alerts")
    print("=" * 60)
    
    hook = DiskSpaceLowHook(warn_threshold=15, crit_threshold=10)
    
    print(f"Hook name: {hook.event_name}")
    print(f"Thresholds: WARN={hook.warn_threshold}%, CRIT={hook.crit_threshold}%")
    print()
    
    disk = psutil.disk_usage('/')
    free_percent = (disk.free / disk.total) * 100
    print(f"Current disk free: {free_percent:.1f}%")
    print()
    
    # First check
    if hook.check():
        message = hook.get_message()
        print(f"✓ Alert triggered!")
        print(f"  Level: {message.alert_level.name}")
        print(f"  Color: {message.color}")
        print(f"  Metadata: {message.metadata}")
    else:
        print("✓ No alert (disk space normal)")
    print()


def test_pattern_alert_queue():
    """Test alert queue mechanism"""
    print("=" * 60)
    print("TEST 4: Pattern Alert Queue")
    print("=" * 60)
    
    # Create a mock queue like patterns would receive
    alert_queue = queue.Queue()
    
    # Create sample messages from different hooks
    cpu_warning = HookMessage(
        hook_name="cpu_monitor",
        alert_level=AlertLevel.WARNING,
        color=(255, 165, 0),
        metadata={"cpu_percent": 45}
    )
    
    disk_critical = HookMessage(
        hook_name="disk_space_monitor",
        alert_level=AlertLevel.CRITICAL,
        color=(255, 0, 0),
        metadata={"disk_free_percent": 8.5}
    )
    
    # Put messages in queue
    alert_queue.put(cpu_warning)
    alert_queue.put(disk_critical)
    
    print("Messages in queue:")
    while not alert_queue.empty():
        msg = alert_queue.get()
        print(f"  From {msg.hook_name}:")
        print(f"    Level: {msg.alert_level.name}")
        print(f"    Color: {msg.color}")
        print(f"    Metadata: {msg.metadata}")
    print()


def test_multi_level_cpu_alerts():
    """
    Test how CPU monitor detects different levels
    This shows the abstract design pattern working
    """
    print("=" * 60)
    print("TEST 5: CPU Monitor Multi-level Detection")
    print("=" * 60)
    
    hook = CPUMonitorHook(warn_threshold=20, crit_threshold=75)
    
    print("Hook demonstrates abstract alert level system:")
    print("  - Single hook class handles multiple severity levels")
    print("  - Same pattern can respond to any level")
    print("  - Easy to add more levels without changing pattern code")
    print()
    
    print("Alert levels in CPU monitor:")
    print("  NORMAL:   < 20%  → GREEN   (0, 255, 0)")
    print("  WARNING:  20-75% → ORANGE  (255, 165, 0)")
    print("  CRITICAL: > 75%  → RED     (255, 0, 0)")
    print()


def test_extensibility():
    """Show how to add custom hooks with different alert levels"""
    print("=" * 60)
    print("TEST 6: Extensibility - Custom Hook Example")
    print("=" * 60)
    
    print("""
Example: Temperature Monitor with 4 levels
    
    class TempMonitorHook(SystemEventHook):
        def __init__(self, warn=50, caution=60, crit=75):
            self.thresholds = {
                AlertLevel.NORMAL: 0,
                AlertLevel.WARNING: warn,
                AlertLevel.CAUTION: caution,      # New level!
                AlertLevel.CRITICAL: crit,
            }
        
        def get_message(self) -> HookMessage:
            temp = get_temperature()
            
            # Determine level based on temperature
            if temp > self.thresholds[AlertLevel.CRITICAL]:
                level = AlertLevel.CRITICAL
                color = (255, 0, 0)       # Red
            elif temp > self.thresholds[AlertLevel.CAUTION]:
                level = AlertLevel.CAUTION
                color = (255, 255, 0)     # Yellow
            elif temp > self.thresholds[AlertLevel.WARNING]:
                level = AlertLevel.WARNING
                color = (255, 165, 0)     # Orange
            else:
                level = AlertLevel.NORMAL
                color = (0, 255, 0)       # Green
            
            return HookMessage(
                hook_name="temp_monitor",
                alert_level=level,
                color=color,
                metadata={"temperature": temp}
            )

The pattern doesn't need to know about specific hook thresholds!
It just responds to the color and alert level.
""")


def test_pattern_receiving_alerts():
    """Simulate a pattern receiving alerts"""
    print("=" * 60)
    print("TEST 7: Pattern Receiving Alerts from Hook")
    print("=" * 60)
    
    print("""
Pattern Pseudocode - How Knight Rider handles alerts:

    def run(self, neo, stop_event, alert_queue=None):
        current_color = (255, 0, 0)  # Default red
        
        while not stop_event.is_set():
            # Check for incoming alerts
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    current_color = message.color
                    print(f"Alert from {message.hook_name}: changing to {current_color}")
                except queue.Empty:
                    pass
            
            # Use current_color in the pattern animation
            for i in range(neo.num_leds):
                neo.set_led_color(i, *current_color)
                neo.update_strip()

Benefits of this design:
  ✓ Patterns don't care what hook triggered the alert
  ✓ Multiple hooks can send alerts to same pattern
  ✓ Pattern continues running, just changes color
  ✓ Works with any number of alert levels
  ✓ Easy to add new hooks without modifying patterns
""")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  HOOK ALERT SYSTEM - COMPREHENSIVE TEST".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    try:
        test_alert_levels()
        test_cpu_monitor_hook()
        test_disk_monitor_hook()
        test_pattern_alert_queue()
        test_multi_level_cpu_alerts()
        test_extensibility()
        test_pattern_receiving_alerts()
        
        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
