#!/usr/bin/env python3
"""
Debug version of run_service.py with extensive logging
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
    print("[MAIN] Starting service...", file=sys.stderr, flush=True)
    
    print("[MAIN] Initializing NeoPixel...", file=sys.stderr, flush=True)
    neo = Pi5Neo(NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED)
    
    print("[MAIN] Creating PatternManager...", file=sys.stderr, flush=True)
    manager = PatternManager(neo)

    # Load patterns and hooks
    print("[MAIN] Loading patterns...", file=sys.stderr, flush=True)
    patterns = manager.load_patterns()
    print(f"[MAIN] Loaded {len(patterns)} patterns: {patterns}", file=sys.stderr, flush=True)
    
    print("[MAIN] Loading hooks...", file=sys.stderr, flush=True)
    hooks = manager.load_hooks()
    print(f"[MAIN] Loaded {len(hooks)} hooks: {hooks}", file=sys.stderr, flush=True)

    # Register config-specified startup patterns and hook links
    print(f"[MAIN] Registering startup patterns: {STARTUP_PATTERNS}", file=sys.stderr, flush=True)
    for p in STARTUP_PATTERNS:
        manager.register_startup_pattern(p)
        
    print(f"[MAIN] Registering hook links: {HOOK_LINKS}", file=sys.stderr, flush=True)
    for hook_event, pattern_name in HOOK_LINKS.items():
        manager.register_startup_pattern(pattern_name, linked_hook=hook_event)

    # Start startup patterns
    print("[MAIN] Starting startup patterns...", file=sys.stderr, flush=True)
    manager.start_startup_patterns()

    # Start IPC server
    print(f"[MAIN] Starting IPC server on {socket_path}...", file=sys.stderr, flush=True)
    ipc = IPCServer(manager, socket_path=socket_path)
    ipc.start()
    print("[MAIN] IPC server started", file=sys.stderr, flush=True)

    # Wait for termination signal
    stop_event = threading.Event()

    def _signal(sig, frame):
        print(f"[MAIN] Received signal {sig}, shutting down...", file=sys.stderr, flush=True)
        stop_event.set()

    signal.signal(signal.SIGINT, _signal)
    signal.signal(signal.SIGTERM, _signal)

    print("[MAIN] Entering main loop...", file=sys.stderr, flush=True)
    try:
        counter = 0
        while not stop_event.is_set():
            time.sleep(5.0)
            counter += 1
            current = manager.current_pattern.name if manager.current_pattern else "None"
            print(f"[MAIN] Heartbeat {counter}: current_pattern={current}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[MAIN] Exception in main loop: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
    finally:
        print("[MAIN] Stopping patterns...", file=sys.stderr, flush=True)
        manager.stop_all_patterns()
        print("[MAIN] Stopping IPC server...", file=sys.stderr, flush=True)
        ipc.stop()
        ipc.join(timeout=2.0)
        print("[MAIN] Service stopped", file=sys.stderr, flush=True)


if __name__ == "__main__":
    print("[STARTUP] Script started", file=sys.stderr, flush=True)
    main()
    print("[SHUTDOWN] Script exiting", file=sys.stderr, flush=True)