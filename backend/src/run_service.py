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
from config import NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED, STARTUP_PATTERNS, HOOK_LINKS


def main(socket_path: str = "/tmp/wopr.sock"):
    neo = Pi5Neo(NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED)
    manager = PatternManager(neo)

    # Load patterns and hooks
    manager.load_patterns()
    manager.load_hooks()

    # Register config-specified startup patterns and hook links
    for p in STARTUP_PATTERNS:
        manager.register_startup_pattern(p)
    for hook_event, pattern_name in HOOK_LINKS.items():
        manager.register_startup_pattern(pattern_name, linked_hook=hook_event)

    # RESTORE LAST PATTERN (from previous session)
    if not manager.load_last_pattern():
        # If no saved pattern, start config defaults
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
        while not stop_event.is_set():
            time.sleep(0.5)
    finally:
        #print("Stopping patterns...")
        #manager.stop_all_patterns()  //Kills patterns when we want to keep them running but the service is always running.
        print("Stopping IPC server...")
        ipc.stop()
        ipc.join(timeout=2.0)
        print("Service stopped")


if __name__ == "__main__":
    main()
