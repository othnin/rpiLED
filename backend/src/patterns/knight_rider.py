#Knight Rider / Cylon Effect (A scanning LED light that moves back and forth)
from backend import PatternBase
import time


class KnightRiderPattern(PatternBase):
    @property
    def name(self): return "Knight Rider Pattern"
    
    @property  
    def description(self): return "Knight Rider or Cylon Effect"

    def run(self, neo, stop_event):
        color = (255, 0, 0)  # Red color
        delay = 0.05  # Delay between LED updates
        num_leds = neo.num_leds
        
        while not stop_event.is_set():  # ← FIXED: was "while True"
            # Forward pass
            for i in range(num_leds):
                if stop_event.is_set():  # ← ADDED: check stop
                    return  # Exit immediately
                neo.fill_strip(0, 0, 0)  # Clear the strip
                neo.set_led_color(i, *color)  # Set the current LED to the color
                neo.update_strip()
                time.sleep(delay)
            
            if stop_event.is_set():  # ← ADDED: check between passes
                return
                
            # Backward pass
            for i in range(num_leds - 1, -1, -1):
                if stop_event.is_set():  # ← ADDED: check stop
                    return  # Exit immediately
                neo.fill_strip(0, 0, 0)  # Clear the strip
                neo.set_led_color(i, *color)  # Set the current LED to the color
                neo.update_strip()
                time.sleep(delay)

    def cleanup(self, neo):
        print("Cleaning up Knight Rider Pattern")
        neo.clear_strip()
        neo.update_strip()