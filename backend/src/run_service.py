#!/usr/bin/env python3
"""
Service runner: initialize Neo, PatternManager, hooks/patterns, start startup patterns
and run an IPC server for external control.
"""
import signal
import sys
import time
import threading

from pi5neo import Pi5Neo
from backend import PatternManager
from ipc_server import IPCServer
from config import DEVICE, NUM_LEDS, SPI_SPEED, STARTUP_PATTERNS, HOOK_LINKS


def main(socket_path: str = "/tmp/wopr.sock"):
    neo = Pi5Neo(DEVICE, NUM_LEDS, SPI_SPEED)
    manager = PatternManager(neo)

    # Load patterns and hooks
    manager.load_patterns()
    manager.load_hooks()

    # Register config-specified startup patterns and hook links
    for p in STARTUP_PATTERNS:
        manager.register_startup_pattern(p)
    for hook_event, pattern_name in HOOK_LINKS.items():
        manager.register_startup_pattern(pattern_name, linked_hook=hook_event)
    
    # Load persistent configuration from previous sessions
    persistent_data = manager.load_persistent_data()
    
    # Restore hook-linked patterns (they auto-start on boot)
    linked_patterns = persistent_data.get("linked", {})
    for hook_event, pattern_name in linked_patterns.items():
        if hook_event not in manager.startup_links:
            manager.startup_links[hook_event] = pattern_name
            # Auto-start hook-linked patterns on boot
            if pattern_name in manager.patterns:
                manager.startup_patterns.append(pattern_name)
                print(f"Restored persistent hook link: {hook_event} → {pattern_name} (auto-starting)")
    
    # Restore standalone patterns (also auto-start them)
    standalone_patterns = persistent_data.get("standalone", [])
    for pattern_name in standalone_patterns:
        if pattern_name in manager.patterns and pattern_name not in manager.startup_patterns:
            manager.startup_patterns.append(pattern_name)
            print(f"Restored standalone startup pattern: {pattern_name}")

    # RESTORE LAST PATTERN (from previous session)
    if not manager.load_pattern():
        # If no saved pattern, start config defaults and startup patterns
        manager.start_startup_patterns()

    # Start IPC server
    ipc = IPCServer(manager, socket_path=socket_path)
    ipc.start()

    # Wait for termination signal
    stop_event = threading.Event()

    def _signal(sig, frame):
        print(f"Received signal {sig}, shutting down...")
        stop_event.set()

    signal.signal(signal.SIGINT, _signal)
    signal.signal(signal.SIGTERM, _signal)

    try:
        last_hook_check = time.time()
        while not stop_event.is_set():
            # Check hooks every 500ms for alerts
            now = time.time()
            if now - last_hook_check >= 0.5:
                manager.check_hooks()
                last_hook_check = now
            
            time.sleep(0.1)
    finally:
        #print("Stopping patterns...")
        #manager.stop_all_patterns()  //Kills patterns when we want to keep them running but the service is always running.
        print("Stopping IPC server...")
        ipc.stop()
        ipc.join(timeout=2.0)
        print("Service stopped")


if __name__ == "__main__":
    main()
