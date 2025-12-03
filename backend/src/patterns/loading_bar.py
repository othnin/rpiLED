from backend import PatternBase
import time
import threading
import queue

class LoadingBarPattern(PatternBase):
    @property
    def name(self): return "Loading Bar Pattern"

    @property  
    def description(self): return "Loading Bar Effect"
    
    def run(self, neo, stop_event, alert_queue=None):
        """
        Run the loading bar pattern with support for dynamic color changes from alerts
        
        Args:
            neo: NeoPixel strip object
            stop_event: Threading event to stop pattern
            alert_queue: Queue for receiving HookMessage alerts
        """
        current_color = (0, 255, 0)  # Default green
        
        while not stop_event.is_set():
            # Check for incoming alert messages
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    current_color = message.color
                    print(f"Loading Bar: Changing color to {current_color} due to {message.hook_name} alert")
                except queue.Empty:
                    pass
            
            # Fill up - CHECK stop_event in the loop!
            for i in range(neo.num_leds):
                if stop_event.is_set():
                    break
                
                # Check for alerts during fill
                if alert_queue:
                    try:
                        message = alert_queue.get_nowait()
                        current_color = message.color
                        print(f"Loading Bar: Changing color to {current_color} due to {message.hook_name} alert")
                    except queue.Empty:
                        pass
                
                neo.set_led_color(i, *current_color)
                neo.update_strip()
                time.sleep(1)
            
            if stop_event.is_set():
                break
            
            # Check for alerts between passes
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    current_color = message.color
                    print(f"Loading Bar: Changing color to {current_color} due to {message.hook_name} alert")
                except queue.Empty:
                    pass
                
            # Empty down - CHECK stop_event here too!
            for i in range(neo.num_leds - 1, -1, -1):
                if stop_event.is_set():
                    break
                
                # Check for alerts during empty
                if alert_queue:
                    try:
                        message = alert_queue.get_nowait()
                        current_color = message.color
                        print(f"Loading Bar: Changing color to {current_color} due to {message.hook_name} alert")
                    except queue.Empty:
                        pass
                
                neo.set_led_color(i, 0, 0, 0)
                neo.update_strip()
                time.sleep(1)
