"""
CPU Temperature Monitoring Hook
Monitors CPU temperature and sends multi-level alerts to patterns
"""

import subprocess
from backend import SystemEventHook
from hook_alerts import AlertLevel, HookMessage, AlertColorScheme


class CPUTemperatureHook(SystemEventHook):
    """
    Monitor CPU temperature and send alerts at multiple levels:
    - NORMAL: Below warning threshold
    - WARNING: At warning threshold (default 65°C)
    - CRITICAL: At critical threshold (default 80°C)
    """
    
    def __init__(self, warn_threshold=65.0, crit_threshold=80.0):
        """
        Initialize temperature monitor hook
        
        Args:
            warn_threshold: Temperature (°C) to trigger WARNING level
            crit_threshold: Temperature (°C) to trigger CRITICAL level
        """
        self.warn_threshold = warn_threshold
        self.crit_threshold = crit_threshold
        self._last_level = None
    
    @property
    def event_name(self) -> str:
        return "cpu_temp_monitor"
    
    def check(self) -> bool:
        """Check CPU temperature and return True if alert level changed"""
        try:
            temp = self._get_temperature()
            if temp is None:
                return False
            
            # Determine alert level
            if temp >= self.crit_threshold:
                current_level = AlertLevel.CRITICAL
            elif temp >= self.warn_threshold:
                current_level = AlertLevel.WARNING
            else:
                current_level = AlertLevel.NORMAL
            
            # Only trigger if level changed
            if self._last_level != current_level:
                self._last_level = current_level
                self._current_temp = temp
                return True
            
        except Exception as e:
            print(f"Error checking temperature: {e}")
        
        return False
    
    def _get_temperature(self) -> float:
        """Get CPU temperature from vcgencmd (Raspberry Pi)"""
        try:
            result = subprocess.run(
                ['vcgencmd', 'measure_temp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            temp_str = result.stdout.strip().replace("temp=", "").replace("'C", "")
            return float(temp_str)
        except Exception as e:
            print(f"Error getting temperature: {e}")
            return None
    
    def get_message(self) -> HookMessage:
        """Generate alert message for current temperature state"""
        color = AlertColorScheme.get_color(self._last_level)
        
        return HookMessage(
            hook_name=self.event_name,
            alert_level=self._last_level,
            color=color,
            metadata={"temperature_c": self._current_temp}
        )
    
    def on_trigger(self, pattern_manager):
        """Called if no linked pattern is configured"""
        temp = self._get_temperature()
        if temp:
            level = self._last_level.name if self._last_level else "UNKNOWN"
            print(f"CPU temperature alert [{level}]: {temp}°C")

