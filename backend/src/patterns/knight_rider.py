#Knight Rider / Cylon Effect (A scanning LED light that moves back and forth)
from backend import PatternBase
import time
import queue


class KnightRiderPattern(PatternBase):
    @property
    def name(self): return "Knight Rider Pattern"
    
    @property  
    def description(self): return "Knight Rider or Cylon Effect"

    def run(self, neo, stop_event, alert_queue=None, color=(255, 0, 0)):
        """
        Run the Knight Rider pattern with support for dynamic color changes from alerts
        
        Args:
            neo: NeoPixel strip object
            stop_event: Threading event to stop pattern
            alert_queue: Queue for receiving HookMessage alerts
            color: Initial LED color (default red)
        """
        delay = 0.05  # Delay between LED updates
        num_leds = neo.num_leds
        current_color = color
        
        while not stop_event.is_set():
            # Check for incoming alert messages
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    current_color = message.color
                    print(f"Knight Rider: Changing color to {current_color} due to {message.hook_name} alert")
                except queue.Empty:
                    pass
            
            # Forward pass
            for i in range(num_leds):
                if stop_event.is_set():  
                    return  # Exit immediately
                
                # Check for alerts during forward pass too
                if alert_queue:
                    try:
                        message = alert_queue.get_nowait()
                        current_color = message.color
                        print(f"Knight Rider: Changing color to {current_color} due to {message.hook_name} alert")
                    except queue.Empty:
                        pass
                
                neo.fill_strip(0, 0, 0)  # Clear the strip
                neo.set_led_color(i, *current_color)  # Set the current LED to the current color
                neo.update_strip()
                time.sleep(delay)
            
            if stop_event.is_set(): 
                return
            
            # Check for alerts between passes
            if alert_queue:
                try:
                    message = alert_queue.get_nowait()
                    current_color = message.color
                except queue.Empty:
                    pass
                
            # Backward pass
            for i in range(num_leds - 1, -1, -1):
                if stop_event.is_set():  
                    return  # Exit immediately
                
                # Check for alerts during backward pass too
                if alert_queue:
                    try:
                        message = alert_queue.get_nowait()
                        current_color = message.color
                    except queue.Empty:
                        pass
                
                neo.fill_strip(0, 0, 0)  # Clear the strip
                neo.set_led_color(i, *current_color)  # Set the current LED to the current color
                neo.update_strip()
                time.sleep(delay)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
