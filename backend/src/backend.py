"""
NeoPixel Pattern Manager - Backend Core
Supports plugin-based patterns and system event hooks
Works with Pi5Neo library
"""

import os
import importlib.util
import inspect
import queue
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Callable
import threading
from config import PATTERN_FILE, PATTERN_LOCATION, HOOK_FILE 

class PatternBase(ABC):
    """Base class that all pattern plugins must inherit from"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for the pattern"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what the pattern does"""
        pass
    
    @abstractmethod
    def run(self, neo, stop_event: threading.Event, alert_queue=None):
        """
        Execute the pattern
        
        Args:
            neo: The Pi5Neo strip object
            stop_event: Threading event to signal when to stop
            alert_queue: Optional queue.Queue for receiving HookMessage alerts from hooks
        """
        pass
    
    def cleanup(self, neo):
        """Optional cleanup when pattern stops"""
        print("Cleaning up pattern from PatternBasic:", self.name)
        neo.clear_strip()
        neo.update_strip()


class SystemEventHook(ABC):
    """Base class for system event hooks"""
    
    @property
    @abstractmethod
    def event_name(self) -> str:
        """Name of the event (e.g., 'cpu_high', 'power_on')"""
        pass
    
    @abstractmethod
    def check(self) -> bool:
        """Check if event condition is met"""
        pass
    
    @abstractmethod
    def on_trigger(self, pattern_manager):
        """Action to take when event triggers"""
        pass
    
    def get_message(self):
        """
        Optional: Generate a HookMessage to send to patterns.
        Override this in subclasses that support multi-level alerts.
        Returns a HookMessage object or None.
        """
        return None


class PatternManager:
    """Manages pattern plugins and system hooks"""
    
    def __init__(self, neo, patterns_dir: str = "./patterns", hooks_dir: str = "./hooks"):
        self.neo = neo
        self.patterns_dir = Path(patterns_dir)
        self.hooks_dir = Path(hooks_dir)
        self.patterns: Dict[str, PatternBase] = {}
        self.hooks: List[SystemEventHook] = []
        self.current_pattern = None
        self.stop_event = threading.Event()
        self.pattern_thread = None
        self.startup_patterns = []
        self.startup_links = {}
        self.alert_queue = queue.Queue()  # Queue for hook messages to patterns
        
        # Create directories if they don't exist
        self.patterns_dir.mkdir(exist_ok=True)
        self.hooks_dir.mkdir(exist_ok=True)
        
    def load_patterns(self) -> List[str]:
        """Load all pattern plugins from patterns directory"""
        self.patterns.clear()
        
        for file_path in self.patterns_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            try:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(
                    file_path.stem, file_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find PatternBase subclasses
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, PatternBase) and 
                        obj is not PatternBase and
                        not inspect.isabstract(obj)):
                        
                        pattern = obj()
                        self.patterns[pattern.name] = pattern
                        print(f"Loaded pattern: {pattern.name}")
                        
            except Exception as e:
                print(f"Error loading pattern {file_path.name}: {e}")
        
        return list(self.patterns.keys())
    
    def load_hooks(self) -> List[str]:
        """Load all system event hooks"""
        self.hooks.clear()
        
        for file_path in self.hooks_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(
                    file_path.stem, file_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find SystemEventHook subclasses
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, SystemEventHook) and 
                        obj is not SystemEventHook and
                        not inspect.isabstract(obj)):
                        
                        hook = obj()
                        self.hooks.append(hook)
                        print(f"Loaded hook: {hook.event_name}")
                        
            except Exception as e:
                print(f"Error loading hook {file_path.name}: {e}")
        
        return [hook.event_name for hook in self.hooks]
    
    def get_pattern(self, name: str) -> PatternBase:
        """Get a pattern by name"""
        return self.patterns.get(name)
    
    def get_pattern_info(self, name: str) -> Dict[str, str]:
        """Get pattern metadata"""
        pattern = self.patterns.get(name)
        if pattern:
            return {
                "name": pattern.name,
                "description": pattern.description
            }
        return None
    
    def get_all_patterns_info(self) -> List[Dict[str, str]]:
        """Get info for all patterns"""
        return [
            {"name": p.name, "description": p.description}
            for p in self.patterns.values()
        ]
    
    def start_pattern(self, pattern_name: str):
        """Start running a pattern"""
        if self.pattern_thread and self.pattern_thread.is_alive():
            self.stop_pattern()
        
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_name}' not found")
        
        self.current_pattern = pattern
        self.stop_event.clear()
        # Create a fresh alert queue for this pattern
        self.alert_queue = queue.Queue()
        
        self.pattern_thread = threading.Thread(
            target=pattern.run,
            args=(self.neo, self.stop_event, self.alert_queue),
            daemon=True
        )
        self.pattern_thread.start()
        print(f"Started pattern: {pattern_name}")
        
    
    def stop_pattern(self):
        """Stop the currently running pattern"""
        if self.pattern_thread and self.pattern_thread.is_alive():
            self.stop_event.set()
            self.pattern_thread.join(timeout=2.0)
            
            if self.current_pattern:
                self.current_pattern.cleanup(self.neo)
                print(f"Stopped pattern: {self.current_pattern.name}")
            
            self.current_pattern = None
        # AUTO-SAVE: Clear saved pattern
        self.clear_pattern()
    
    def save_pattern(self, pattern_name: str):
        """Save the pattern to persist across reboots"""
        file_name = file_name = os.path.join(PATTERN_LOCATION, PATTERN_FILE)
        try:
            os.makedirs(PATTERN_LOCATION, exist_ok=True) 
            with open(file_name, 'w') as f:
                f.write(pattern_name)
            print(f"Saved pattern: {pattern_name}")
        except Exception as e:
            print(f"Error saving pattern: {e}")
    
    def clear_pattern(self):
        """Clear the saved pattern"""
        file_name = file_name = os.path.join(PATTERN_LOCATION, PATTERN_FILE)
        try:
            if os.path.exists(file_name):
                os.remove(file_name)
                print("Cleared pattern")
        except Exception as e:
            print(f"Error clearing pattern: {e}")
    
    def load_pattern(self):
        """Load and start the pattern from file"""
        file_name = file_name = os.path.join(PATTERN_LOCATION, PATTERN_FILE)
        try:
            with open(file_name, 'r') as f:
                pattern_name = f.read().strip()
                if pattern_name and pattern_name in self.patterns:
                    print(f"Restoring pattern: {pattern_name}")
                    self.start_pattern(pattern_name)
                    return True
        except FileNotFoundError:
            print("No saved pattern found")
        except Exception as e:
            print(f"Error loading pattern: {e}")
        return False
    
    def check_hooks(self):
        """Check all system hooks and trigger if needed"""
        for hook in self.hooks:
            try:
                # Only check hooks that have a purpose:
                # 1. They're linked to a pattern, OR
                # 2. A pattern is running that can receive alerts
                hook_has_link = hook.event_name in self.startup_links
                pattern_is_running = self.current_pattern is not None
                
                # Skip this hook if it has no purpose
                if not hook_has_link and not pattern_is_running:
                    continue
                
                if hook.check():
                    print(f"Event triggered: {hook.event_name}")
                    
                    # Check if this hook is linked to a pattern
                    linked_pattern = self.startup_links.get(hook.event_name)
                    
                    # Try to send alert message to currently running pattern
                    if self.current_pattern and hasattr(self, 'alert_queue'):
                        message = hook.get_message()
                        if message:
                            try:
                                self.alert_queue.put_nowait(message)
                                print(f"Sent alert from {hook.event_name} to running pattern: {message}")
                            except queue.Full:
                                print(f"Alert queue full, message from {hook.event_name} dropped")
                    
                    if linked_pattern and linked_pattern in self.patterns:
                        print(f"Starting linked pattern: {linked_pattern}")
                        self.start_pattern(linked_pattern)
            except Exception as e:
                print(f"Error checking hook {hook.event_name}: {e}")
    
    def save_persistent_link(self, hook_event_name: str, pattern_name: str):
        """Save a hook-pattern link to persistent storage"""
        try:
            data = self.load_persistent_data()
            if "linked" not in data:
                data["linked"] = {}
            data["linked"][hook_event_name] = pattern_name
            
            self._write_persistent_data(data)
            print(f"Saved persistent link: {hook_event_name} → {pattern_name}")
        except Exception as e:
            print(f"Error saving persistent link: {e}")
    
    def remove_persistent_link(self, hook_event_name: str):
        """Remove a hook-pattern link from persistent storage"""
        try:
            data = self.load_persistent_data()
            if "linked" in data and hook_event_name in data["linked"]:
                del data["linked"][hook_event_name]
                self._write_persistent_data(data)
                print(f"Removed persistent link: {hook_event_name}")
        except Exception as e:
            print(f"Error removing persistent link: {e}")
    
    def save_pattern_to_startup(self, pattern_name: str):
        """Add a standalone pattern to persistent startup (no hook required)"""
        try:
            data = self.load_persistent_data()
            if "standalone" not in data:
                data["standalone"] = []
            if pattern_name not in data["standalone"]:
                data["standalone"].append(pattern_name)
            
            self._write_persistent_data(data)
            print(f"Added standalone startup pattern: {pattern_name}")
        except Exception as e:
            print(f"Error saving standalone pattern: {e}")
    
    def remove_pattern_from_startup(self, pattern_name: str):
        """Remove a standalone pattern from persistent startup"""
        try:
            data = self.load_persistent_data()
            if "standalone" in data and pattern_name in data["standalone"]:
                data["standalone"].remove(pattern_name)
                self._write_persistent_data(data)
                print(f"Removed standalone startup pattern: {pattern_name}")
        except Exception as e:
            print(f"Error removing standalone pattern: {e}")
    
    def load_persistent_links(self) -> dict:
        """Load hook-pattern links from persistent storage (returns only linked patterns)"""
        try:
            data = self.load_persistent_data()
            return data.get("linked", {})
        except Exception as e:
            print(f"Error loading persistent links: {e}")
        return {}
    
    def load_startup_patterns_list(self) -> list:
        """Load standalone startup patterns from persistent storage"""
        try:
            data = self.load_persistent_data()
            return data.get("standalone", [])
        except Exception as e:
            print(f"Error loading startup patterns: {e}")
        return []
    
    def load_persistent_data(self) -> dict:
        """Load all persistent data (linked patterns and standalone patterns)"""
        try:
            hook_file = os.path.join(PATTERN_LOCATION, HOOK_FILE)
            if os.path.exists(hook_file):
                with open(hook_file, 'r') as f:
                    import json
                    data = json.load(f)
                    # Support legacy format: if data is a dict of strings (old format),
                    # convert it to new format with "linked" key
                    if data and isinstance(data, dict):
                        # Check if it's old format (has hook names as keys, patterns as values)
                        # vs new format (has "linked" and "standalone" keys)
                        if "linked" not in data and "standalone" not in data:
                            # Old format - convert to new format
                            data = {"linked": data, "standalone": []}
                    return data
        except Exception as e:
            print(f"Error loading persistent data: {e}")
        return {"linked": {}, "standalone": []}
    
    def _write_persistent_data(self, data: dict):
        """Write persistent data to file"""
        hook_file = os.path.join(PATTERN_LOCATION, HOOK_FILE)
        os.makedirs(PATTERN_LOCATION, exist_ok=True)
        
        with open(hook_file, 'w') as f:
            import json
            json.dump(data, f, indent=2)

    def start_startup_patterns(self):
        """Start all patterns registered to start on startup."""
        for name in list(self.startup_patterns):
            try:
                self.start_pattern(name)
            except Exception as e:
                print(f"Failed to start startup pattern '{name}': {e}")

    def stop_all_patterns(self):
        """Stop any running pattern(s)."""
        self.stop_pattern()

    def register_startup_pattern(self, pattern_name: str, linked_hook: str = None):
        """Register a pattern to automatically start on manager startup.

        If linked_hook is provided the manager will also start the pattern
        when that hook's event_name triggers.
        """
        if pattern_name not in self.startup_patterns:
            self.startup_patterns.append(pattern_name)
        if linked_hook:
            self.startup_links[linked_hook] = pattern_name
        print(f"Registered startup pattern: {pattern_name}" + 
              (f" (linked to hook: {linked_hook})" if linked_hook else ""))

    def save_startup_patterns(self, filepath: str = "/tmp/wopr_startup.txt"):
        """Save startup patterns to file"""
        try:
            with open(filepath, 'w') as f:
                for pattern in self.startup_patterns:
                    f.write(f"{pattern}\n")
            print(f"Saved {len(self.startup_patterns)} startup patterns to {filepath}")
        except Exception as e:
            print(f"Error saving startup patterns: {e}")

    def load_startup_patterns_from_file(self, filepath: str = "/tmp/wopr_startup.txt"):
        """Load startup patterns from file"""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    pattern_name = line.strip()
                    if pattern_name and pattern_name in self.patterns:
                        self.startup_patterns.append(pattern_name)
            print(f"Loaded {len(self.startup_patterns)} startup patterns from {filepath}")
        except FileNotFoundError:
            print(f"No startup patterns file found at {filepath}")
        except Exception as e:
            print(f"Error loading startup patterns: {e}")


# Example usage and testing
if __name__ == "__main__":
    from pi5neo import Pi5Neo
    
    # Initialize NeoPixel strip
    neo = Pi5Neo(DEVICE, NUM_LEDS, SPI_SPEED)
    
    # Initialize manager
    manager = PatternManager(neo)
    
    # Load plugins
    patterns = manager.load_patterns()
    print(f"\nAvailable patterns: {patterns}")
    
    hooks = manager.load_hooks()
    print(f"Active hooks: {hooks}")
    
    # Get pattern info
    for info in manager.get_all_patterns_info():
        print(f"\n{info['name']}: {info['description']}")