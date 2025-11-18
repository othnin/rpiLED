from backend import PatternBase
import time
import threading

class LoadingBarPattern(PatternBase):
    @property
    def name(self): return "Loading Bar Pattern"
    
    def run(self, neo, stop_event):
        print("Num LEDS: ", neo.num_leds)
        while not stop_event.is_set():
            # Fill up - CHECK stop_event in the loop!
            for i in range(neo.num_leds):
                if stop_event.is_set():  # ← ADD THIS
                    break
                neo.set_led_color(i, 0, 255, 0)  # Green loading bar
                neo.update_strip()
                time.sleep(1)
            
            if stop_event.is_set():  # ← ADD THIS
                break
                
            # Empty down - CHECK stop_event here too!
            for i in range(neo.num_leds - 1, -1, -1):  # Fixed: was going to 0, should be -1
                if stop_event.is_set():  # ← ADD THIS
                    break
                print(i)
                neo.set_led_color(i, 0, 0, 0)  # Turn OFF, not green again
                neo.update_strip()
                time.sleep(1)