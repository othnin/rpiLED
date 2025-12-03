# patterns/my_cool_pattern.py
from backend import PatternBase
import time
import threading
import queue

class MyCoolPattern(PatternBase):
    @property
    def name(self):
        return "My Cool Pattern"
    
    @property
    def description(self):
        return "Does something awesome"
    
    def run(self, neo, stop_event, alert_queue=None):
        current_color = (255, 0, 255)  # Default purple
        
        while not stop_event.is_set():
            # Check for incoming alert messages
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    current_color = message.color
                    print(f"My Cool Pattern: Changing color to {current_color} due to {message.hook_name} alert")
                except queue.Empty:
                    pass
            
            # Your pattern code here
            for i in range(neo.num_leds):
                # Check for alerts during pattern
                if alert_queue:
                    try:
                        message = alert_queue.get_nowait()
                        current_color = message.color
                        print(f"My Cool Pattern: Changing color to {current_color} due to {message.hook_name} alert")
                    except queue.Empty:
                        pass
                
                neo.set_led_color(i, *current_color)
                neo.update_strip()
                time.sleep(0.1)
