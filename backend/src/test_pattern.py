#!/usr/bin/env python3
"""
Test a single pattern - useful for development and debugging
"""

from pi5neo import Pi5Neo
from backend import PatternManager
import time
import sys


def main():
    # Configuration
    PATTERN_NAME = "Knight Rider Pattern"  # Change this to test different patterns
    RUN_TIME = 30  # How long to run the pattern (seconds)
    
    print("Initializing NeoPixel strip...")
    from config import NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED
    
    # Initialize NeoPixel strip
    neo = Pi5Neo(NEO_DEVICE, NEO_NUM_LEDS, NEO_SPI_SPEED)
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
    print(f"\nTesting: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"Duration: {RUN_TIME} seconds")
    print("\nPress Ctrl+C to stop early\n")
    
    try:
        # Start the pattern
        manager.start_pattern(PATTERN_NAME)
        print(f"Pattern '{PATTERN_NAME}' started...")
        
        # Let it run
        time.sleep(RUN_TIME)
        
        # Stop the pattern
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