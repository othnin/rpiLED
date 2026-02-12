"""
CPU Usage Monitoring Hook
Monitors CPU and sends multi-level alerts to running patterns
"""

import psutil
from backend import SystemEventHook
from hook_alerts import AlertLevel, HookMessage, AlertColorScheme


class CPUMonitorHook(SystemEventHook):
    """
    Monitor CPU usage and send alerts at multiple levels:
    - NORMAL: Under 20%
    - WARNING: 20-75%
    - CRITICAL: Over 75%
    """
    
    def __init__(self, warn_threshold=20, crit_threshold=75):
        """
        Initialize CPU monitor hook
        
        Args:
            warn_threshold: CPU % to trigger WARNING level
            crit_threshold: CPU % to trigger CRITICAL level
        """
        self.warn_threshold = warn_threshold
        self.crit_threshold = crit_threshold
        self._last_level = None
        self._hysteresis = 5  # Avoid flapping between levels
    
    @property
    def event_name(self) -> str:
        return "cpu_monitor"
    
    def check(self) -> bool:
        """Check CPU usage and return True if alert level changed"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        print("CPU Percent: ", str(cpu_percent))
        
        # Determine alert level
        if cpu_percent > self.crit_threshold:
            current_level = AlertLevel.CRITICAL
        elif cpu_percent > self.warn_threshold:
            current_level = AlertLevel.WARNING
        else:
            current_level = AlertLevel.NORMAL
        
        # Only trigger if level changed (with hysteresis for stability)
        if self._last_level != current_level:
            self._last_level = current_level
            self._current_cpu_percent = cpu_percent
            return True
        
        return False
    
    def get_message(self) -> HookMessage:
        """Generate alert message for current CPU state"""
        color = AlertColorScheme.get_color(self._last_level)
        print("Color: ", str(color))
        
        return HookMessage(
            hook_name=self.event_name,
            alert_level=self._last_level,
            color=color,
            metadata={"cpu_percent": self._current_cpu_percent}
        )
    
    def on_trigger(self, pattern_manager):
        """Called if no linked pattern is configured"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        level = self._last_level.name if self._last_level else "UNKNOWN"
        print(f"CPU alert [{level}]: {cpu_percent}%")
