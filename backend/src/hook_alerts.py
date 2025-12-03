"""
Hook Alert System - Standardized messaging from hooks to patterns
Allows hooks to send multi-level alerts that patterns can respond to
"""

from enum import Enum, auto
from typing import Tuple, Optional, Dict, Any


class AlertLevel(Enum):
    """Alert severity levels that hooks can send"""
    NORMAL = auto()      # Normal/OK state
    WARNING = auto()     # Warning state (yellow/orange)
    CRITICAL = auto()    # Critical state (red)
    
    @staticmethod
    def from_string(value: str) -> 'AlertLevel':
        """Convert string to AlertLevel"""
        try:
            return AlertLevel[value.upper()]
        except KeyError:
            return AlertLevel.NORMAL


class HookMessage:
    """Message sent from a hook to a running pattern"""
    
    def __init__(
        self,
        hook_name: str,
        alert_level: AlertLevel,
        color: Tuple[int, int, int],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a hook message
        
        Args:
            hook_name: Name of the hook sending the message
            alert_level: Severity level of the alert
            color: RGB tuple (0-255 each) for the LED color
            metadata: Optional additional data (e.g., {"cpu_percent": 75})
        """
        self.hook_name = hook_name
        self.alert_level = alert_level
        self.color = color
        self.metadata = metadata or {}
    
    def __repr__(self):
        return (f"HookMessage(hook={self.hook_name}, level={self.alert_level.name}, "
                f"color={self.color})")


class AlertColorScheme:
    """Default color scheme for alert levels"""
    
    COLORS = {
        AlertLevel.NORMAL: (0, 255, 0),      # Green
        AlertLevel.WARNING: (255, 165, 0),   # Orange
        AlertLevel.CRITICAL: (255, 0, 0),    # Red
    }
    
    @staticmethod
    def get_color(level: AlertLevel) -> Tuple[int, int, int]:
        """Get RGB color for an alert level"""
        return AlertColorScheme.COLORS.get(level, (255, 255, 255))
