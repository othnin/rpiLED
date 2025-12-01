#!/usr/bin/env python3
"""
Test CPU hook - demonstrates CPUOver20Hook triggering a pattern
"""

from pi5neo import Pi5Neo
from backend import PatternManager
from hooks.cpu_monitor import CPUOver20Hook
import time
import sys
import threading
import math


def cpu_load_simulator(duration: float, intensity: float = 1.0):
    """
    Simulate CPU load by performing calculations
    
    Args:
        duration: How long to generate load (seconds)
        intensity: Load intensity multiplier (1.0 = baseline)
    """
    end_time = time.time() + duration
    while time.time() < end_time:
        # Perform CPU-intensive calculations
        for i in range(int(1000 * intensity)):
            _ = math.sqrt(i) * math.sin(i) * math.cos(i)


def main():
    # Configuration
    PATTERN_NAME = "Knight Rider Pattern"
    TEST_DURATION = 60  # How long to monitor CPU (seconds)
    CHECK_INTERVAL = 2  # How often to check CPU (seconds)
    
    print("Initializing NeoPixel strip...")
    print("Note: CPU load simulator will run in background to trigger the hook\n")
    from config import DEVICE, NUM_LEDS, SPI_SPEED
    
    # Initialize NeoPixel strip
    neo = Pi5Neo(DEVICE, NUM_LEDS, SPI_SPEED)
    print(f"Strip has {neo.num_leds} LEDs")
    
    print("\nInitializing Pattern Manager...")
    manager = PatternManager(neo)
    
    print("Loading patterns...")
    pattern_names = manager.load_patterns()
    
    if not pattern_names:
        print("ERROR: No patterns found in ./patterns/ directory!")
        return
    
    print(f"\nAvailable patterns:")
    for info in manager.get_all_patterns_info():
        print(f"  - {info['name']}")
    
    # Check if pattern exists
    if PATTERN_NAME not in pattern_names:
        print(f"\nERROR: Pattern '{PATTERN_NAME}' not found!")
        print(f"Available patterns: {', '.join(pattern_names)}")
        return
    
    # Get pattern info
    info = manager.get_pattern_info(PATTERN_NAME)
    print(f"\nTesting hook with pattern: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"\nMonitoring CPU usage for {TEST_DURATION} seconds...")
    print("When CPU exceeds 20%, the pattern will start.")
    print("Press Ctrl+C to stop\n")
    
    # Create the hook
    hook = CPUOver20Hook()
    
    # Start CPU load simulator in background thread
    print("Starting CPU load simulator in background...\n")
    cpu_load_thread = threading.Thread(
        target=lambda: cpu_load_simulator(TEST_DURATION, intensity=5.0),
        daemon=True
    )
    cpu_load_thread.start()
    
    try:
        start_time = time.time()
        pattern_running = False
        
        while time.time() - start_time < TEST_DURATION:
            # Check if hook condition is met
            if hook.check():
                if not pattern_running:
                    print(f"\n✓ CPU over 20% detected - Starting pattern!")
                    manager.start_pattern(PATTERN_NAME)
                    pattern_running = True
            else:
                if pattern_running:
                    print(f"\n✓ CPU back under 20% - Stopping pattern!")
                    manager.stop_pattern()
                    pattern_running = False
            
            time.sleep(CHECK_INTERVAL)
        
        # Clean up
        if pattern_running:
            print(f"\nStopping pattern...")
            manager.stop_pattern()
        
        print("✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        manager.stop_pattern()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        manager.stop_pattern()
        
    finally:
        # Clean up
        neo.clear_strip()
        neo.update_strip()
        print("LEDs cleared")


if __name__ == "__main__":
    main()
