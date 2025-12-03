# ============================================================================
# VOLTAGE MONITORING (Raspberry Pi specific)
# ============================================================================

import subprocess
from backend import SystemEventHook
from hook_alerts import AlertLevel, HookMessage, AlertColorScheme


class UnderVoltageHook(SystemEventHook):
    """
    Detect under-voltage conditions (power supply issues)
    - NORMAL: No voltage issues
    - CRITICAL: Under-voltage detected
    """
    
    def __init__(self):
        self._last_level = None
        self._current_status = ""
    
    @property
    def event_name(self) -> str:
        return "voltage_monitor"
    
    def check(self) -> bool:
        """Check for voltage issues and return True if status changed"""
        try:
            under_voltage = self._check_under_voltage()
            
            # Determine alert level
            if under_voltage:
                current_level = AlertLevel.CRITICAL
                self._current_status = "Under-voltage detected"
            else:
                current_level = AlertLevel.NORMAL
                self._current_status = "Voltage OK"
            
            # Only trigger if level changed
            if self._last_level != current_level:
                self._last_level = current_level
                return True
            
        except Exception as e:
            print(f"Error checking voltage: {e}")
        
        return False
    
    def _check_under_voltage(self) -> bool:
        """Check throttle status for under-voltage conditions"""
        try:
            result = subprocess.run(
                ['vcgencmd', 'get_throttled'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # throttled=0x0 means no issues
            # Bit 0: under-voltage (current)
            # Bit 1: arm frequency capped
            # Bit 2: currently throttled
            # Bit 16: under-voltage has occurred (history)
            throttled = int(result.stdout.strip().split('=')[1], 16)
            
            # Check for under-voltage (current or historical)
            return bool(throttled & 0x1 or throttled & 0x10000)
        except Exception as e:
            print(f"Error parsing throttle status: {e}")
            return False
    
    def get_message(self) -> HookMessage:
        """Generate alert message for current voltage state"""
        color = AlertColorScheme.get_color(self._last_level)
        
        return HookMessage(
            hook_name=self.event_name,
            alert_level=self._last_level,
            color=color,
            metadata={"status": self._current_status}
        )
    
    def on_trigger(self, pattern_manager):
        """Called if no linked pattern is configured"""
        level = self._last_level.name if self._last_level else "UNKNOWN"
        print(f"Voltage alert [{level}]: {self._current_status}")
