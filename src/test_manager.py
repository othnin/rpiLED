#!/usr/bin/env python3
"""
Test script for pattern manager
Run this to test the backend before building the GUI
"""

from pi5neo import Pi5Neo
from backend import PatternManager
import time


def main():
    print("Initializing NeoPixel strip...")
    neo = Pi5Neo('/dev/spidev0.0', 17, 800)
    print(f"Strip has {neo.num_leds} LEDs")
    
    print("\nInitializing Pattern Manager...")
    manager = PatternManager(neo)
    
    # Load patterns
    print("\nLoading patterns...")
    pattern_names = manager.load_patterns()
    
    if not pattern_names:
        print("No patterns found! Create some .py files in ./patterns/")
        return
    
    print(f"\nFound {len(pattern_names)} patterns:")
    for info in manager.get_all_patterns_info():
        print(f"  - {info['name']}: {info['description']}")
    
    # Load hooks
    print("\nLoading system hooks...")
    hook_names = manager.load_hooks()
    if hook_names:
        print(f"Loaded {len(hook_names)} hooks: {', '.join(hook_names)}")
    else:
        print("No hooks found (optional)")
    
    # Test each pattern for 5 seconds
    print("\n" + "="*50)
    print("Testing patterns (5 seconds each)")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    try:
        for pattern_name in pattern_names:
            print(f"\nRunning: {pattern_name}")
            manager.start_pattern(pattern_name)
            
            # Check hooks while pattern runs
            for _ in range(5):
                manager.check_hooks()
                time.sleep(1)
            
            manager.stop_pattern()
            time.sleep(0.5)
        
        print("\n✓ All patterns tested successfully!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
        manager.stop_pattern()
    
    finally:
        # Clean up
        # neo.clear_strip()
        # neo.update_strip()
        print("Cleanup complete")


if __name__ == "__main__":
    main()