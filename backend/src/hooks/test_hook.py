"""
Test/Mock Hook
Allows manual triggering for testing pattern behavior
"""

from backend import SystemEventHook


class TestHook(SystemEventHook):
    """Mock hook for testing - manually triggered"""
    
    def __init__(self):
        self._triggered = False
    
    @property
    def event_name(self) -> str:
        return "test_trigger"
    
    def check(self) -> bool:
        """Check if test was triggered"""
        if self._triggered:
            self._triggered = False  # Reset for next trigger
            return True
        return False
    
    def trigger(self):
        """Manually trigger this hook"""
        self._triggered = True
    
    def on_trigger(self, pattern_manager):
        """Called if no linked pattern is configured"""
        print(f"Test hook triggered - no linked pattern")