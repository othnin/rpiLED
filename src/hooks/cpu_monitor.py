"""
CPU Usage Monitoring Hooks
Triggers patterns based on CPU load thresholds
"""

import psutil
from backend import SystemEventHook


class CPUOver20Hook(SystemEventHook):
    """Trigger when CPU usage exceeds 20%"""
    
    @property
    def event_name(self) -> str:
        return "cpu_over_20"
    
    def check(self) -> bool:
        """Check if CPU usage is over 20%"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return cpu_percent > 20
    
    def on_trigger(self, pattern_manager):
        """Start a pattern when CPU is over 20%"""
        print(f"CPU usage is {psutil.cpu_percent(interval=0.1)}% - over 20% threshold")
        # You can specify which pattern to run here
        # pattern_manager.start_pattern("some_pattern_name")


class CPUOver50Hook(SystemEventHook):
    """Trigger when CPU usage exceeds 50%"""
    
    @property
    def event_name(self) -> str:
        return "cpu_over_50"
    
    def check(self) -> bool:
        """Check if CPU usage is over 50%"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return cpu_percent > 50
    
    def on_trigger(self, pattern_manager):
        """Start a pattern when CPU is over 50%"""
        print(f"CPU usage is {psutil.cpu_percent(interval=0.1)}% - over 50% threshold")
        # You can specify which pattern to run here
        # pattern_manager.start_pattern("some_pattern_name")


class CPUOver75Hook(SystemEventHook):
    """Trigger when CPU usage exceeds 75%"""
    
    @property
    def event_name(self) -> str:
        return "cpu_over_75"
    
    def check(self) -> bool:
        """Check if CPU usage is over 75%"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return cpu_percent > 75
    
    def on_trigger(self, pattern_manager):
        """Start a pattern when CPU is over 75%"""
        print(f"CPU usage is {psutil.cpu_percent(interval=0.1)}% - over 75% threshold")
        # You can specify which pattern to run here
        # pattern_manager.start_pattern("some_pattern_name")
