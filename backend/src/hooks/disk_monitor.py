# ============================================================================
# DISK SPACE MONITORING
# ============================================================================

import psutil
from backend import SystemEventHook
from hook_alerts import AlertLevel, HookMessage, AlertColorScheme


class DiskSpaceLowHook(SystemEventHook):
    """
    Monitor disk space and send alerts at multiple levels:
    - NORMAL: Above warning threshold
    - WARNING: At warning threshold (default 15% free)
    - CRITICAL: At critical threshold (default 10% free)
    """
    
    def __init__(self, warn_threshold=15.0, crit_threshold=10.0):
        """
        Initialize disk monitor hook
        
        Args:
            warn_threshold: % free disk to trigger WARNING level
            crit_threshold: % free disk to trigger CRITICAL level
        """
        self.warn_threshold = warn_threshold
        self.crit_threshold = crit_threshold
        self._last_level = None
    
    @property
    def event_name(self) -> str:
        return "disk_space_monitor"
    
    def check(self) -> bool:
        """Check disk usage and return True if alert level changed"""
        disk = psutil.disk_usage('/')
        free_percent = (disk.free / disk.total) * 100
        
        # Determine alert level
        if free_percent <= self.crit_threshold:
            current_level = AlertLevel.CRITICAL
        elif free_percent <= self.warn_threshold:
            current_level = AlertLevel.WARNING
        else:
            current_level = AlertLevel.NORMAL
        
        # Only trigger if level changed
        if self._last_level != current_level:
            self._last_level = current_level
            self._current_free_percent = free_percent
            return True
        
        return False
    
    def get_message(self) -> HookMessage:
        """Generate alert message for current disk state"""
        color = AlertColorScheme.get_color(self._last_level)
        
        return HookMessage(
            hook_name=self.event_name,
            alert_level=self._last_level,
            color=color,
            metadata={"disk_free_percent": self._current_free_percent}
        )
    
    def on_trigger(self, pattern_manager):
        """Called if no linked pattern is configured"""
        disk = psutil.disk_usage('/')
        free_percent = (disk.free / disk.total) * 100
        level = self._last_level.name if self._last_level else "UNKNOWN"
        print(f"Disk alert [{level}]: {free_percent:.1f}% free")
