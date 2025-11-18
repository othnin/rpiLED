"""
NeoPixel Pattern Manager - Backend Core
Supports plugin-based patterns and system event hooks
Works with Pi5Neo library
"""

import os
import importlib.util
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Callable, Optional
import threading


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
    def run(self, neo, stop_event: threading.Event):
        """
        Execute the pattern
        
        Args:
            neo: The Pi5Neo strip object
            stop_event: Threading event to signal when to stop
        """
        pass
    
    def cleanup(self, neo):
        """Optional cleanup when pattern stops"""
        print(f"Cleaning up pattern: {self.name}")
        neo.clear_strip()
        neo.update_strip()
        print(f"Cleaned up pattern: {self.name}")


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
        # Thread-safety lock for starting/stopping patterns
        self._lock = threading.RLock()

        # Patterns to automatically start on manager startup
        self.startup_patterns: List[str] = []
        # Optional mapping from hook.event_name -> pattern_name to start
        self.startup_links: Dict[str, str] = {}

        # Simple callback registry for UI integration (e.g. PyQt signals)
        # Callbacks are called with a single argument: the pattern name
        self._callbacks: Dict[str, List[Callable[[str], None]]] = {}

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
        with self._lock:
            if self.pattern_thread and self.pattern_thread.is_alive():
                self.stop_pattern()

            pattern = self.patterns.get(pattern_name)
            if not pattern:
                raise ValueError(f"Pattern '{pattern_name}' not found")

            self.current_pattern = pattern
            self.stop_event.clear()

            self.pattern_thread = threading.Thread(
                target=pattern.run,
                args=(self.neo, self.stop_event),
                daemon=True
            )
            self.pattern_thread.start()
            print(f"Started pattern: {pattern_name}")
            self._emit("pattern_started", pattern_name)
    
    def stop_pattern(self):
        """Stop the currently running pattern"""
        with self._lock:
            if self.pattern_thread and self.pattern_thread.is_alive():
                self.stop_event.set()
                self.pattern_thread.join(timeout=2.0)

                if self.current_pattern:
                    name = self.current_pattern.name
                    self.current_pattern.cleanup(self.neo)
                    print(f"Stopped pattern: {name}")
                    self._emit("pattern_stopped", name)

                self.current_pattern = None
    
    def check_hooks(self):
        """Check all system hooks and trigger if needed"""
        for hook in self.hooks:
            try:
                if hook.check():
                    print(f"Event triggered: {hook.event_name}")
                    # Prefer manager-controlled handling so we can start linked
                    # patterns automatically. Hooks may still call manager
                    # directly if needed.
                    self.handle_hook_trigger(hook)
            except Exception as e:
                print(f"Error checking hook {hook.event_name}: {e}")

    def handle_hook_trigger(self, hook: SystemEventHook):
        """Handle a triggered hook.

        If a hook is linked to a pattern via `startup_links` the pattern
        will be started. Otherwise we call the hook's own on_trigger
        handler so existing hooks keep working.
        """
        linked = self.startup_links.get(hook.event_name)
        try:
            if linked:
                try:
                    self.start_pattern(linked)
                except Exception as e:
                    print(f"Failed to start linked pattern '{linked}': {e}")
            else:
                # Fallback to the hook's custom behavior
                hook.on_trigger(self)
        except Exception as e:
            print(f"Error handling hook {hook.event_name}: {e}")

    def register_startup_pattern(self, pattern_name: str, linked_hook: Optional[str] = None):
        """Register a pattern to automatically start on manager startup.

        If linked_hook is provided the manager will also start the pattern
        when that hook's event_name triggers.
        """
        if pattern_name not in self.startup_patterns:
            self.startup_patterns.append(pattern_name)
        if linked_hook:
            self.startup_links[linked_hook] = pattern_name

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

    def register_callback(self, event: str, callback: Callable[[str], None]):
        """Register a UI callback for events like 'pattern_started' or
        'pattern_stopped'. The callback will be called with the pattern name.
        """
        self._callbacks.setdefault(event, []).append(callback)

    def _emit(self, event: str, pattern_name: str):
        print(f"Emitting event '{event}' for pattern '{pattern_name}'")
        for cb in self._callbacks.get(event, []):
            print(cb)
            print(pattern_name)
            try:
                cb(pattern_name)
            except Exception as e:
                print(f"Callback for {event} failed: {e}")


# Example usage and testing
if __name__ == "__main__":
    from pi5neo import Pi5Neo
    from config import (
        NEO_DEVICE,
        NEO_NUM_LEDS,
        NEO_SPI_SPEED,
        STARTUP_PATTERNS,
        HOOK_LINKS,
    )

    # Initialize NeoPixel strip
    neo = Pi5Neo(NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED)

    # Initialize manager
    manager = PatternManager(neo)

    # Load plugins
    patterns = manager.load_patterns()
    print(f"\nAvailable patterns: {patterns}")

    hooks = manager.load_hooks()
    print(f"Active hooks: {hooks}")

    # Register any configured startup patterns and hook links
    for p in STARTUP_PATTERNS:
        manager.register_startup_pattern(p)
    for hook_event, pattern_name in HOOK_LINKS.items():
        manager.register_startup_pattern(pattern_name, linked_hook=hook_event)

    # Start startup patterns (if any)
    manager.start_startup_patterns()

    # Get pattern info
    for info in manager.get_all_patterns_info():
        print(f"\n{info['name']}: {info['description']}")