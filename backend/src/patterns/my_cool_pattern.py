# patterns/my_cool_pattern.py
from backend import PatternBase
import time
import threading

class MyCoolPattern(PatternBase):
    @property
    def name(self):
        return "My Cool Pattern"
    
    @property
    def description(self):
        return "Does something awesome"
    
    def run(self, neo, stop_event):
        while not stop_event.is_set():
            # Your pattern code here
            for i in range(neo.num_leds):
                neo.set_led_color(i, 255, 0, 255)  # Purple
                neo.update_strip()
                time.sleep(0.1)