"""
Memory Usage Monitoring Hook
Monitors memory usage and sends multi-level alerts to patterns
"""

import psutil
from backend import SystemEventHook
from hook_alerts import AlertLevel, HookMessage, AlertColorScheme


class MemoryMonitorHook(SystemEventHook):
    """
    Monitor memory usage and send alerts at multiple levels:
    - NORMAL: Below warning threshold
    - WARNING: At warning threshold (default 70%)
    - CRITICAL: At critical threshold (default 90%)
    """
    
    def __init__(self, warn_threshold=70.0, crit_threshold=90.0):
        """
        Initialize memory monitor hook
        
        Args:
            warn_threshold: Memory % to trigger WARNING level
            crit_threshold: Memory % to trigger CRITICAL level
        """
        self.warn_threshold = warn_threshold
        self.crit_threshold = crit_threshold
        self._last_level = None
    
    @property
    def event_name(self) -> str:
        return "memory_monitor"
    
    def check(self) -> bool:
        """Check memory usage and return True if alert level changed"""
        memory = psutil.virtual_memory()
        mem_percent = memory.percent
        
        # Determine alert level
        if mem_percent >= self.crit_threshold:
            current_level = AlertLevel.CRITICAL
        elif mem_percent >= self.warn_threshold:
            current_level = AlertLevel.WARNING
        else:
            current_level = AlertLevel.NORMAL
        
        # Only trigger if level changed
        if self._last_level != current_level:
            self._last_level = current_level
            self._current_mem_percent = mem_percent
            return True
        
        return False
    
    def get_message(self) -> HookMessage:
        """Generate alert message for current memory state"""
        color = AlertColorScheme.get_color(self._last_level)
        
        return HookMessage(
            hook_name=self.event_name,
            alert_level=self._last_level,
            color=color,
            metadata={"memory_percent": self._current_mem_percent}
        )
    
    def on_trigger(self, pattern_manager):
        """Called if no linked pattern is configured"""
        memory = psutil.virtual_memory()
        level = self._last_level.name if self._last_level else "UNKNOWN"
        print(f"Memory alert [{level}]: {memory.percent}%")
