#!/usr/bin/env python3
"""
Test/control script for PatternManager and hooks
Allows starting/stopping patterns and hooks, viewing status, and running at startup via CLI args.
"""
import argparse
import sys
import time
from pi5neo import Pi5Neo
from backend import PatternManager
from config import NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED


def main():
    parser = argparse.ArgumentParser(description="PatternManager control script")
    parser.add_argument("--pattern", type=str, help="Name of pattern to control")
    parser.add_argument("--hook", type=str, help="Name of hook to control (event_name)")
    parser.add_argument("--startup", action="store_true", help="Run pattern at startup")
    parser.add_argument("--stop", action="store_true", help="Stop the pattern (and hook if running)")
    parser.add_argument("--status", action="store_true", help="Show currently running pattern and loaded hooks")
    parser.add_argument("--link", action="store_true", help="Link hook to pattern (hook triggers pattern)")
    parser.add_argument("--wait", type=int, default=30, help="How long to run before stopping (seconds)")
    args = parser.parse_args()

    neo = Pi5Neo(NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED)
    manager = PatternManager(neo)
    patterns = manager.load_patterns()
    hooks = manager.load_hooks()

    if args.status:
        print(f"Currently running pattern: {manager.current_pattern.name if manager.current_pattern else 'None'}")
        print(f"Loaded hooks: {[h.event_name for h in manager.hooks]}")
        sys.exit(0)

    if args.pattern and args.pattern not in patterns:
        print(f"Pattern '{args.pattern}' not found. Available: {patterns}")
        sys.exit(1)
    if args.hook and args.hook not in [h.event_name for h in manager.hooks]:
        print(f"Hook '{args.hook}' not found. Available: {[h.event_name for h in manager.hooks]}")
        sys.exit(1)

    if args.startup and args.pattern:
        manager.register_startup_pattern(args.pattern)
        manager.start_startup_patterns()
        print(f"Started pattern '{args.pattern}' at startup.")
        time.sleep(args.wait)
        manager.stop_all_patterns()
        print(f"Stopped pattern '{args.pattern}'.")
        sys.exit(0)

    if args.link and args.pattern and args.hook:
        manager.register_startup_pattern(args.pattern, linked_hook=args.hook)
        print(f"Linked hook '{args.hook}' to pattern '{args.pattern}'.")
        # Simulate hook check loop
        print("Checking hooks for trigger...")
        for _ in range(args.wait):
            manager.check_hooks()
            time.sleep(1)
        manager.stop_all_patterns()
        print(f"Stopped pattern '{args.pattern}'.")
        sys.exit(0)

    if args.pattern and not args.stop:
        manager.start_pattern(args.pattern)
        print(f"Started pattern '{args.pattern}'. Running for {args.wait} seconds...")
        time.sleep(args.wait)
        manager.stop_pattern()
        print(f"Stopped pattern '{args.pattern}'.")
        sys.exit(0)

    if args.pattern and args.stop:
        manager.stop_pattern()
        print(f"Stopped pattern '{args.pattern}'.")
        sys.exit(0)

    print("No valid action specified. Use --help for options.")

if __name__ == "__main__":
    main()
